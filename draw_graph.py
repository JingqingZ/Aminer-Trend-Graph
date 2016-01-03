import json
import math
import operator

class DrawGraph(object):
    """docstring for DrawGraph"""
    def __init__(self, data_file_name, stem_topic):
        super(DrawGraph, self).__init__()
        with open(data_file_name) as data_file:
            self.data = json.load(data_file)
        self.stem_topic = stem_topic
        assert(self.stem_topic in self.data["topics"])
        self.color_empty = "#EEEEEE"
        self.color_topic = "#87CEFF"
        self.graph_data = []

    def check_valid_topic(self, topic):
        if topic not in self.data["topics"]:
            return False
        start_year = self.data["topics"][topic]["start_year"]
        end_year = self.data["topics"][topic]["end_year"]
        dist = self.data["topics"][topic]["dist"]
        if start_year < 1900 or start_year > 2015 or \
            end_year < 1900 or end_year > 2015 or \
            len(dist) <= 0 or len(dist) != end_year - start_year + 1:
            # print(start_year)
            # print(end_year)
            # print(len(dist))
            return False
        return True

    def graph_data_update(self, topic, order, empty):
        # print(topic)
        year = self.data["topics"][topic]["year"]
        start_year = self.data["topics"][topic]["start_year"]
        end_year = self.data["topics"][topic]["end_year"]
        dist = self.data["topics"][topic]["dist"]
        for i in range(0, end_year - start_year + 1):
            node = dict()
            node["year"] = start_year + i
            node["name"] = topic
            node["display_name"] = topic.replace("_", " ")
            node["order"] = order
            node["value"] = math.log(dist[i] + 1)
            node["color"] = self.color_topic
            self.graph_data.append(node)
        if not empty["empty"]:
            return
        for i in range(0, end_year - start_year + 1):
            node = dict()
            node["year"] = start_year + i
            node["name"] = empty["name"]
            node["display_name"] = "empty"
            node["order"] = order + empty["orientation"]
            if (empty["start_year_mode"] == 1 and node["year"] < year + 2):
                node["value"] = 0
            elif (empty["start_year_mode"] == 1 and node["year"] > year + 2):
                node["value"] = 0.5 * math.log(dist[i] + 1)
            elif (empty["start_year_mode"] == 0):
                node["value"] = 10 - 0.5 * math.log(dist[i] + 1)
            node["color"] = self.color_empty
            self.graph_data.append(node)

    def sort_afterwards_topic(self, topic, config):
        to = self.data["topics"][topic]["to"]
        to_num = self.data["topics"][topic]["to_num"]
        assert(len(to) == len(to_num))
        to_dict = dict()
        for i in range(0, len(to)):
            to_dict[to[i]] = to_num[i]
        sorted_to_dict = sorted(to_dict.items(), key=operator.itemgetter(1))
        # to_dict = {}
        # end = -1
        # if len(sorted_to_dict) > config["top"]:
        #     end = len(sorted_to_dict) - config["top"] - 1
        # for i in range(len(sorted_to_dict) - 1, end, -1):
        #     to_dict[sorted_to_dict[i][0]] = self.data["topics"][topic]["year"]
        # sorted_to_dict = sorted(to_dict.items(), key=operator.itemgetter(1))
        # print(sorted_to_dict)
        return sorted_to_dict

    def draw_graph(self):
        self.graph_data = []
        # {"year": 1993, "name":"4", "order": 9, "value": 30, "color": "#EEEEEE"},
        assert(self.check_valid_topic(self.stem_topic))
        self.graph_data_update(self.stem_topic, 100, {"name": "empty10", "empty": True, "start_year_mode": 0, "center": 0, "orientation": 100})
        # empty, start_year_mode, # 0: start year, 1: year
        # empty, center, # 0: topic, 1: empty
        sorted_to_dict = self.sort_afterwards_topic(self.stem_topic, {"top": 5})
        empty = False
        for i in range(0, len(sorted_to_dict)):
            rank = len(sorted_to_dict) - i - 1
            to_topic = sorted_to_dict[rank][0]
            # print(to_topic)
            if not self.check_valid_topic(to_topic):
                continue
            orientation = (i % 2) * 2 - 1
            self.graph_data_update(to_topic, 100 - i * 2 * orientation, {"name": "empty" + repr(8 - i * 2), "empty": empty, "start_year_mode": 1, "center": 1, "orientation": orientation})
            empty = True
            if (i > 1):
                break
        self.graph_data = json.dumps(self.graph_data)
        print(self.graph_data)

def main():
    ad = DrawGraph("./visual_artificial_intelligence_complete.json", "artificial_intelligence")
    ad.draw_graph()

if __name__ == '__main__':
    main()
        