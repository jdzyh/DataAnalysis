import xml.etree.ElementTree as ET
from collections import defaultdict
import pprint
import re

############################################
# 探索用户
############################################
BASIC_NODES = ["relation", "node", "way"]

def get_user(element):
    return element.get("uid"), element.get("user")

#获取所有的用户-id对
def get_user_of_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag in BASIC_NODES:
            user_id, user_name = get_user(element)
            users.add(user_id + ':' + user_name)
    return users

users_set = get_user_of_map(OSM_FILE_NAME)
print(len(users_set))
print(users_set)

###########################################
# 街道名（课程内代码）
OSM_FILE_NAME = "map.xml"
#匹配街道名称最后独立字符串（称谓）
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Rd": "Road",
            "Rd.": "Road",
            "Ave": "Avenue"
            }
def audit_street_type(street_types, street_name):
    m = re.search(street_type_re, street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    
    osm_file.close()
    return street_types


def update_name(name, mapping):
    for from_name, to_name in mapping.iteritems():
        #print '(.*)(' + from_name + ')$'
        name_regex = re.compile(r'(.*)(' + from_name + ')$', re.IGNORECASE)
        match_result = re.search(name_regex, name)

        if match_result:
            name = match_result.group(1) + to_name
            break;
    return name