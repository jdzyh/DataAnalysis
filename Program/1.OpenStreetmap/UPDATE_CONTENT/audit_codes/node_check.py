import xml.etree.ElementTree as ET
import pprint
import re

##############################################
# 用于检查文件包含哪些基本节点
##############################################
OSM_FILE_NAME = "map.xml"
NODE_TYPES = set()
def get_node_types(file_name="sample.xml"):
    context = ET.iterparse(file_name, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event=='start':
            #print('start----'+elem.tag)
            NODE_TYPES.add(elem.tag)
			

get_node_types(OSM_FILE_NAME)
print(NODE_TYPES)

###############################################
# 用于检查各个类型的基本节点的attribute类型
###############################################
CHECK_NODES = ["relation", "node", "way"]

way_attribs=set()
way_tag_attribs=set()
node_attribs=set()
node_tag_attribs=set()
relation_attribs=set()
relation_tag_attribs=set()
relation_member_attribs=set()

def get_basic_attributes(file_name="sample.xml"):
    context = ET.iterparse(file_name, events=('start',))
    _, root = next(context)
    for event, elem in context:
        if event=='start' and elem.tag=='node':
            for attrib in elem.attrib.keys():
                node_attribs.add(attrib)
            for node_tag in elem.iter("tag"):
                for attrib in node_tag.attrib.keys():
                    node_tag_attribs.add(attrib)
        elif event=='start' and elem.tag=='way':
            for attrib in elem.attrib.keys():
                way_attribs.add(attrib)
            for way_tag in elem.iter("tag"):
                for attrib in way_tag.attrib.keys():
                    way_tag_attribs.add(attrib)
        elif event=='start' and elem.tag=='relation':
            for attrib in elem.attrib.keys():
                relation_attribs.add(attrib)
            for relation_tag in elem.iter("tag"):
                for attrib in relation_tag.attrib.keys():
                    relation_tag_attribs.add(attrib)
            for relation_member in elem.iter("member"):
                for attrib in relation_member.attrib.keys():
                    relation_member_attribs.add(attrib)


get_basic_attributes("map.xml")
#输出各类标签的 attribute 类型
print("way_attribs:=" + str(way_attribs))
print("way_tag_attribs:="+ str(way_tag_attribs))
print("node_attribs:="+ str(node_attribs))
print("node_tag_attribs:="+ str(node_tag_attribs))
print("relation_attribs:="+ str(relation_attribs))
print("relation_tag_attribs:="+ str(relation_tag_attribs))
print("relation_member_attribs:="+ str(relation_member_attribs))

#######################################################
# 检查tag标签节点的 k 值
#######################################################
WAY_TAG_K=set()
NODE_TAG_K=set()
REL_TAG_K=set()

def get_tag_k(file_name="sample.xml"):
    context = ET.iterparse(file_name, events=('start',))
    _, root = next(context)
    for event, elem in context:
        if event=='start' and elem.tag=='way':
            for way_tag in elem.iter("tag"):
                WAY_TAG_K.add(way_tag.attrib['k'])
                
        elif event=='start' and elem.tag=='node':
            for node_tag in elem.iter("tag"):
                NODE_TAG_K.add(node_tag.attrib['k'])
                
        elif event=='start' and elem.tag=='relation':
            for rel_tag in elem.iter("tag"):
                REL_TAG_K.add(rel_tag.attrib['k'])
				
get_tag_k("map.xml")

#检查每一个K值出现的次数
way_tag_k_counter = {k_name:0 for k_name in WAY_TAG_K}
node_tag_k_counter = {k_name:0 for k_name in NODE_TAG_K}
rel_tag_k_counter = {k_name:0 for k_name in REL_TAG_K}

#对每一个k值出现次数进行计数
def count_K_field(file_name="sample.xml"):
    context = ET.iterparse(file_name, events=('start',))
    _, root = next(context)
    for event, elem in context:
        if event=='start' and elem.tag=='way':
            for way_tag in elem.iter("tag"):
                way_tag_k_counter[way_tag.attrib['k']] +=1
                
        elif event=='start' and elem.tag=='node':
            for node_tag in elem.iter("tag"):
                node_tag_k_counter[node_tag.attrib['k']] +=1
                
        elif event=='start' and elem.tag=='relation':
            for rel_tag in elem.iter("tag"):
                rel_tag_k_counter[rel_tag.attrib['k']] +=1

				
count_K_field("map.xml")
print(node_tag_k_counter, way_tag_k_counter, rel_tag_k_counter)

########################################################
# 检查k值是否是其他k值的前缀
def check_one_prefix_of_set(k, src_set, result_list):
    for k_name in src_set:
        regex = re.compile(r'^' + k + ':.*$')
        m = re.search(regex, k_name)
        if m:
            result_list.append(k_name)

def check_prefix(k_set):
    result_counter = {k_name:[] for k_name in k_set}
    
    for (k_name, k_list) in result_counter.items():
        check_one_prefix_of_set(k_name, k_set, k_list)
    
    keys = list(result_counter.keys())
    keys.sort()
    return [(k, result_counter[k]) for k in keys]

#Reletion_tag_k的前缀情况
for (k, k_list) in check_prefix(REL_TAG_K):
    if len(k_list)>=1:
        print(k+"==>" + str(k_list))

#Node_tag_k的前缀情况
for (k, k_list) in check_prefix(NODE_TAG_K):
    if len(k_list)>=1:
        print(k+"==>" + str(k_list))

#Way_tag_k的前缀情况
for (k, k_list) in check_prefix(WAY_TAG_K):
    if len(k_list)>=1:
        print(k+"==>" + str(k_list))

