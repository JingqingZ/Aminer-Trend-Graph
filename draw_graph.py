import json
import math
import operator
from trend_tree import TrendTree
from trend_tree import TrendTreeNode
from trend_tree import NodeType


class DrawGraph(object):
    """docstring for DrawGraph"""
    def __init__(self, data_file_name, stem_topic):
        super(DrawGraph, self).__init__()
        with open(data_file_name) as data_file:
            self.data = json.load(data_file)
        self.stem_topic = stem_topic
        self.start_year = self.data["topics"][stem_topic]["start_year"]
        self.end_year = self.data["topics"][stem_topic]["end_year"]
        assert(self.stem_topic in self.data["topics"])
        self.color_empty = "#EEEEEE"
        self.color_topic = "#87CEFF"
        # self.drawed_topics = dict()
        # self.dist_sum = list()
        self.display_data = list()

    def display_data_topic(self, node, order):
        display_node_list = list()
        for i in range(0, self.end_year - self.start_year + 1):
            display_node = dict()
            display_node["year"] = self.start_year + i
            display_node["name"] = node.topic
            display_node["display_name"] = node.topic.replace("_", " ")
            display_node["order"] = order
            display_node["value"] = node.info["dist"][i]
            display_node["color"] = self.color_topic
            display_node_list.append(display_node)
        return display_node_list

    def display_data_empty(self, node, order):
        display_node_list = list()
        for i in range(0, self.end_year - self.start_year + 1):
            display_node = dict()
            display_node["year"] = self.start_year + i
            display_node["name"] = "empty" + repr(order)
            display_node["display_name"] = " "
            display_node["order"] = order
            display_node["value"] = node.info["dist"][i]
            display_node["color"] = self.color_empty
            display_node_list.append(display_node)
        return display_node_list

    def draw_graph(self, display_list):
        self.display_data = list()
        for i in range(0, len(display_list)):
            node = display_list[i]
            if node.node_type == NodeType.topic:
                self.display_data += self.display_data_topic(node, i)
            elif node.node_type == NodeType.empty:
                self.display_data += self.display_data_empty(node, i)

    def outputDisplayData(self, outfilename):
        with open(outfilename, 'w') as outfile:
            json.dump(self.display_data, outfile)


def main():
    ad = DrawGraph("./data/visual_artificial_intelligence_complete.json", "artificial_intelligence")
    tt = TrendTree(ad.data, "artificial_intelligence", 5)
    tt.build_tree()
    display_list = tt.traverseRoot()
    ad.draw_graph(display_list)
    ad.outputDisplayData("./data.txt")

if __name__ == '__main__':
    main()
        