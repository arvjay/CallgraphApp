import json
import networkx as nx
from matplotlib import pyplot as plt
from pycg import formats
from pycg.pycg import CallGraphGenerator
from pycg.utils.constants import CALL_GRAPH_OP
import re
import sys
import os


# Takes a dictionary containing the parent as the key and a list of strings as a value
# (matching the structure of a JSON file) and converts it into a directed graph containing parent-child relationships
def json_to_graph(f):
    json_dict = json.load(f)
    f.close()
    graph = nx.DiGraph()
    for key in json_dict:
        if not graph.has_node(key):
            graph.add_node(key)
        for i in json_dict[key]:
            graph.add_edge(key, i)
    return graph


# Takes a dictionary containing a parent as a key and a list of strings as a value
# (matching the structure of a JSON file) and converts it into a directed graph containing
# parent-child relationships, with a filter on a list keywords
def json_to_graph_filter(f, filter):
    json_dict = json.load(f)
    f.close()
    graph = nx.DiGraph()
    for key in json_dict:
        for i in json_dict[key]:
            tf = check_if_filtered_child(json_dict, json_dict[i], filter)
            if contains_any_of(i, filter) or tf:
                graph.add_edge(key, i)
    return graph


# Helper method to filter by keyword
def contains_any_of(str, list):
    for i in list:
        if i in str.lower():
            return True
    return False


# Recursive helper method to determine whether a node has any descendants that have a keyword
def check_if_filtered_child(json_dict, child_nodes, filter):
    child_list = []
    for child in child_nodes:
        if contains_any_of(child, filter):
            return True
        elif json_dict[child] != child_nodes:
            child_list.extend(json_dict[child])
    if len(child_nodes) <= 0:
        return False
    return check_if_filtered_child(json_dict, child_list, filter)

def searchDirectory(directory):
    entry_points = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            if re.search(".+\.py$", filename) != None:
                entry_points.append(f)
        else:
            entry_points.extend(searchDirectory(f))
    return entry_points

def convert_to_json(path):
    # Entry points into package
    entry_points = []
    if re.search(".+\.py$", path) != None:
        entry_points.append(path)
    else:
        entry_points = searchDirectory(path)
            
    # Specified package
    package = "example"
    max_iter = 1000
    # Specified Call Graph Operation
    operation = CALL_GRAPH_OP
    outputpath = "example.json"
    # Call Graph Generation
    cg = CallGraphGenerator(entry_points, package,
                            max_iter, operation)
    cg.analyze()
    formatter = formats.Simple(cg)
    output = formatter.generate()

    # Call Graph output written to JSON file
    with open(outputpath, "w+") as file:
        file.write(json.dumps(output))

fileStructure = sys.argv[1]
convert_to_json(fileStructure)
file = open('./example.json')
keywords = []
if len(sys.argv) == 3:
    keywords = sys.argv[2].split(",")
    json_graph = json_to_graph_filter(file, keywords)
else:
    json_graph = json_to_graph(file)
file.close()
plt.tight_layout()
pos = nx.spring_layout(json_graph)
nx.draw_networkx(json_graph, pos=pos, arrows=True, arrowsize=4, width=0.15, node_size=100, font_size=3)
plt.savefig("example.png", format="PNG", dpi=1080)
plt.clf()

