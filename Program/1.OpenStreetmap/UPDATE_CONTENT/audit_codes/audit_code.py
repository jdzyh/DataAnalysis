#############################################
# 数据清洗并生成CSV文件的代码
#############################################
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "map.xml"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"
REL_PATH = "relations.csv"
REL_TAGS_PATH = "rel_tags.csv"
REL_MEMBERS_PATH = "rel_members.csv"

NODE_TAG_COLON = re.compile(r'^(.*?):(.*)')
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']

WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

REL_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
REL_TAGS_FIELDS = ['id', 'key', 'value', 'type']
REL_MEMBER_FIELDS = ['id', 'ref', 'type', 'role', 'position']


"""Clean and shape node or way XML element to Python dict"""
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS, rel_attr_fields=REL_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    node_attribs = {}
    
    way_attribs = {}
    way_nodes = []
    
    rel_attribs = {}
    rel_members = []
    
    tags = []  # Handle secondary tags the same way for both node and way elements

    # 检查 node 节点
    if element.tag == 'node':
        for node_attr_field in node_attr_fields:
            node_attribs[node_attr_field] = element.get(node_attr_field)
        for tag in element.iter("tag"):
            key_string = tag.get('k')
            if re.search(PROBLEMCHARS, key_string):
                continue
            if key_string.find(':')<0:
                current_tag = {}
                current_tag['id'] = element.get('id')
                current_tag['value'] = tag.get('v')
                current_tag['key'] = key_string
                current_tag['type'] = "regular"
                tags.append(current_tag)
            else:
                current_tag = {}
                m = re.search(NODE_TAG_COLON, key_string)
                current_tag['id'] = element.get('id')
                current_tag['value'] = tag.get('v')
                current_tag['key'] = m.group(2)
                current_tag['type'] = m.group(1)
                tags.append(current_tag)
        return {'node': node_attribs, 'node_tags': tags}
    #检查 way 节点    
    elif element.tag == 'way':
        for way_attr_field in way_attr_fields:
            way_attribs[way_attr_field] = element.get(way_attr_field)
        for tag in element.iter("tag"):
            key_string = tag.get('k')
            if re.search(PROBLEMCHARS, key_string):
                continue
            if key_string.find(':')<0:
                current_tag = {}
                current_tag['id'] = element.get('id')
                current_tag['value'] = tag.get('v')
                current_tag['key'] = key_string
                current_tag['type'] = "regular"
                tags.append(current_tag)
            else:
                current_tag = {}
                m = re.search(NODE_TAG_COLON, key_string)
                current_tag['id'] = element.get('id')
                current_tag['value'] = tag.get('v')
                current_tag['key'] = m.group(2)
                current_tag['type'] = m.group(1)
                tags.append(current_tag)
        cnt=0
        for node in element.iter("nd"):
            way_node = {}
            way_node['id'] = element.get('id')
            way_node['node_id'] = node.get('ref')
            way_node['position'] = cnt
            cnt+=1
            way_nodes.append(way_node)
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    
    #检查 relation 节点
    elif element.tag == 'relation':
        #relation节点的属性
        for rel_attr_field in rel_attr_fields:
            rel_attribs[rel_attr_field] = element.get(rel_attr_field)
        #迭代tag子节点
        for tag in element.iter('tag'):
            key_string = tag.get('k')
            if re.search(PROBLEMCHARS, key_string):
                continue
            if key_string.find(':')<0:
                current_tag = {}
                current_tag['id'] = element.get('id')
                current_tag['value'] = tag.get('v')
                current_tag['key'] = key_string
                current_tag['type'] = "regular"
                tags.append(current_tag)
            else:
                current_tag = {}
                m = re.search(NODE_TAG_COLON, key_string)
                current_tag['id'] = element.get('id')
                current_tag['value'] = tag.get('v')
                current_tag['key'] = m.group(2)
                current_tag['type'] = m.group(1)
                tags.append(current_tag)
        #迭代member子节点
        cnt=0
        for member in element.iter('member'):
            member_node = {}
            member_node['id'] = element.get('id')
            member_node['type'] = member.get('type')
            member_node['ref'] = member.get('ref')
            member_node['role'] = member.get('role')
            member_node['position'] = cnt
            cnt+=1
            rel_members.append(member_node)
        return {'relation': rel_attribs, 'rel_tags': tags, 'rel_members': rel_members}

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        #field, errors = next(validator.errors.items())
        #message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        #error_string = pprint.pformat(errors)
        #raise Exception(message_string.format(field, error_string))
        raise Exception(validator._errors)


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            #k: (v.encode('utf-8') if isinstance(v, str) else v) for k, v in row.items()
            k: (v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w', encoding='utf-8') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w', encoding='utf-8') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w', encoding='utf-8') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w', encoding='utf-8') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w', encoding='utf-8') as way_tags_file, \
         codecs.open(REL_PATH, 'w', encoding='utf-8') as relations_file, \
         codecs.open(REL_TAGS_PATH, 'w', encoding='utf-8') as rel_tags_file, \
         codecs.open(REL_MEMBERS_PATH, 'w', encoding='utf-8') as rel_members_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)
        
        relations_writer = UnicodeDictWriter(relations_file, REL_FIELDS)
        rel_tags_writer = UnicodeDictWriter(rel_tags_file, REL_TAGS_FIELDS)
        rel_members_writer = UnicodeDictWriter(rel_members_file, REL_MEMBER_FIELDS)
        
        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()
        
        relations_writer.writeheader()
        rel_tags_writer.writeheader()
        rel_members_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way', 'relation')):
        #for element in get_element(file_in, tags=('node')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
                elif element.tag == 'relation':
                    relations_writer.writerow(el['relation'])
                    rel_members_writer.writerows(el['rel_members'])
                    rel_tags_writer.writerows(el['rel_tags'])

process_map("map.xml", validate=True)

