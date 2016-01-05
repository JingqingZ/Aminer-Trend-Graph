import operator
import math
import copy
from enum import Enum


class NodeType(Enum):
    """docstring for NodeType"""
    topic = 0
    empty = 1
    left = 2
    right = 3


class TrendTreeNode(object):
    """docstring for TrendTreeNode"""
    def __init__(self, node_type, parent, topic="", info=None):
        super(TrendTreeNode, self).__init__()
        if node_type == NodeType.left or node_type == NodeType.right:
            self.node_type = node_type
            self.parent = parent
            self.children = list()
            self.topic = ""
            self.info = None
        elif node_type == NodeType.topic:
            self.node_type = node_type
            self.parent = parent
            self.children = [TrendTreeNode(NodeType.left, self), TrendTreeNode(NodeType.right, self)]
            self.topic = topic
            self.info = copy.deepcopy(info)
            # process dist data
            for i in range(0, len(info["dist"])):
                self.info["dist"][i] = math.log(info["dist"][i] + 1)
        elif node_type == NodeType.empty:
            self.node_type = node_type
            self.parent = parent
            self.children = list()
            self.topic = ""
            self.info = dict()
            self.info["dist"] = list()
            self.info["year"] = info["year"]
            self.info["start_year"] = info["start_year"]
            self.info["end_year"] = info["end_year"]
            # print(self.info)
        else:
            self.node_type = None
            self.parent = None
            self.children = list()
            self.topic = ""
            self.info = None

    def compute_empty_dist(self, arg, etype=0):
        # self.info = dict()
        self.info["dist"] = copy.deepcopy(arg)
        # print(self.info)
        if etype == 0:  # not bottom
            for i in range(0, self.info["year"] - self.info["start_year"] + 1):
                self.info["dist"][i] = 0
        '''
        elif etype == 0:
            self.info["dist"] = copy.deepcopy(arg["dist"])
            if len(arg["dist"]) <= 0:
                return
            year = arg["year"]
            start_year = arg["start_year"]
            end_year = arg["end_year"]
            for i in range(0, year - start_year + 1):
                self.info["dist"][i] = 0
            for i in range(0, end_year - year):
                self.info["dist"][year - start_year + 1 + i] = arg["dist"][-i]
            # print(arg["dist"])
            # print(self.info["dist"])
        '''


class TrendTree(object):
    """docstring for TrendTree"""
    def __init__(self, data, stem_topic, threhold=4):
        super(TrendTree, self).__init__()
        self.root = TrendTreeNode(NodeType.left, None)
        self.data = data
        self.stem_topic = stem_topic
        self.threhold = threhold
        self.traverse_results = list()
        self.unique = dict()

    def check_topic_validation(self, topic):
        if topic not in self.data["topics"]:
            return False
        start_year = self.data["topics"][topic]["start_year"]
        end_year = self.data["topics"][topic]["end_year"]
        dist = self.data["topics"][topic]["dist"]
        if start_year < 1900 or start_year > 2015 or \
                end_year < 1900 or end_year > 2015 or \
                len(dist) <= 0 or len(dist) != end_year - start_year + 1:
            return False
        return True

    def generate_children_topics(self, topic):
        # fetch afterwards topics from data and check validation
        to = self.data["topics"][topic]["to"]
        to_num = self.data["topics"][topic]["to_num"]
        assert(len(to) == len(to_num))
        # if no children topics, return empty list
        if (len(to) == 0):
            return []
        # sort by weight (descending) and get the top n topics (n = self.threhold)
        to_dict = dict()
        for i in range(0, len(to)):
            to_dict[to[i]] = to_num[i]
        sorted_to_dict_by_weight = sorted(to_dict.items(), key=operator.itemgetter(1), reverse=True)
        # sort by year (descending)
        to_dict = dict()
        end = min(len(sorted_to_dict_by_weight), self.threhold)
        for i in range(0, end):
            ctopic = sorted_to_dict_by_weight[i][0]
            to_dict[ctopic] = self.data["topics"][ctopic]["year"]
        sorted_to_dict_by_year = sorted(to_dict.items(), key=operator.itemgetter(1), reverse=False)
        # return results, format: [(topic, year), ...]
        # print(sorted_to_dict_by_year)
        return sorted_to_dict_by_year

    def build_tree(self):
        # initialize root and stem_topic node
        current_topic_node = TrendTreeNode(NodeType.topic, self.root, self.stem_topic, self.data["topics"][self.stem_topic])
        self.root.children.append(current_topic_node)
        self.root.children.append(TrendTreeNode(NodeType.empty, self.root, "", self.data["topics"][self.stem_topic]))  # TODO!!!
        # BFS
        topic_node_list = list()  # save those topics that have NOT been added into trees
        topic_node_list.append(current_topic_node)
        while(len(topic_node_list) > 0):
            parent_node = topic_node_list[0]
            # print(parent_node.topic)
            children_topic_list = self.generate_children_topics(parent_node.topic)
            for i in range(0, len(children_topic_list)):
                child_topic = children_topic_list[i][0]  # get child topic name, exclude year information
                # print("\t" + child_topic)
                child_node = TrendTreeNode(NodeType.topic, parent_node.children[i % 2], child_topic, self.data["topics"][child_topic])
                # update node
                parent_node.children[i % 2].children.append(child_node)
                empty_node = TrendTreeNode(NodeType.empty, parent_node.children[i % 2], "", self.data["topics"][child_topic])
                # empty_node.compute_empty_dist(child_node.info, 0)
                parent_node.children[i % 2].children.append(empty_node)  # TODO!!!
                # update topic node list
                topic_node_list.append(child_node)
            # update topic node list
            topic_node_list = topic_node_list[1:]

    def traverse_left(self, node):
        for i in range(0, len(node.children), 2):
            if node.children[i].topic in self.unique:
                continue
            if not self.check_topic_validation(node.children[i].topic):
                continue
            self.traverse_topic(node.children[i])
            self.traverse_results.append(node.children[i + 1])

    def traverse_right(self, node):
        for i in range(len(node.children) - 1, -1, -2):
            if node.children[i - 1].topic in self.unique:
                continue
            if not self.check_topic_validation(node.children[i - 1].topic):
                continue
            self.traverse_results.append(node.children[i])
            self.traverse_topic(node.children[i - 1])

    def traverse_topic(self, node):
        assert(node.node_type == NodeType.topic)
        assert(node.topic not in self.unique)
        self.traverse_left(node.children[0])
        self.traverse_results.append(node)
        self.unique[node.topic] = 1
        self.traverse_right(node.children[1])

    def traverseRoot(self):
        self.traverse_results = list()
        self.unique = dict()
        self.traverse_topic(self.root.children[0])
        self.traverse_results.append(self.root.children[1])
        # compute the stem_topic's empty dist
        assert(len(self.traverse_results) % 2 == 0)
        dist_sum = copy.deepcopy(self.traverse_results[0].info["dist"])
        for i in range(1, len(self.traverse_results)):
            if self.traverse_results[i].node_type == NodeType.empty:
                # compute empty dist
                dist_max = -1
                for j in range(0, len(dist_sum)):
                    if dist_sum[j] > dist_max:
                        dist_max = dist_sum[j]
                center = dist_max * 0.6
                empty_dist = list()
                for j in range(0, len(dist_sum)):
                    empty_dist.append(center - 0.5 * dist_sum[j])
                # update empty dist
                # print(self.traverse_results[i].info)
                if i != len(self.traverse_results) - 1:
                    self.traverse_results[i].compute_empty_dist(empty_dist, 0)
                else:
                    self.traverse_results[i].compute_empty_dist(empty_dist, 1)
            # update dist_sum
            for j in range(0, len(dist_sum)):
                dist_sum[j] += self.traverse_results[i].info["dist"][j]
        return self.traverse_results
