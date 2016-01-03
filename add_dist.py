import json

class AddDist(object):
    """docstring for AddDist"""
    def __init__(self):
        super(AddDist, self).__init__()
        self.topicdist = dict()
        self.jsondist = ""
        self.topic = ""
        self.dist = {}
        self.datadist = ""

    def update(self, line, year1, year2):
        content = line.split("\t")
        if len(content) == 1 and self.topic != "":
            self.topicdist[self.topic] = dict()
            distlist = []
            for year in range(year1, year2 + 1):
                if year not in self.dist:
                    distlist.append(0)
                else:
                    distlist.append(self.dist[year])
            self.topicdist[self.topic]["dist"] = distlist
            self.topicdist[self.topic]["start_year"] = year1
            self.topicdist[self.topic]["end_year"] = year2
        if len(content) == 1:
            self.topic = content[0].replace("\n", "")
            self.dist = {}
        else:
            year = int(content[1])
            numb = int(content[2])
            self.dist[year] = numb

    def loadDist(self, infilename, year1, year2):
        infile = open(infilename, 'r')
        self.topic = ""
        self.dist = {}
        for line in infile:
            self.update(line, year1, year2)
        self.update("end", year1, year2)

    def loadData(self, infilename):
        with open(infilename) as data_file:    
            self.datadist = json.load(data_file)
            for key in self.datadist["topics"].keys():
                if key not in self.topicdist:
                    print(key + " not in topic dist")
                    self.datadist["topics"][key]["dist"] = []
                    self.datadist["topics"][key]["start_year"] = 0
                    self.datadist["topics"][key]["end_year"] = 0
                else:
                    self.datadist["topics"][key]["dist"] = self.topicdist[key]["dist"]
                    self.datadist["topics"][key]["start_year"] = self.topicdist[key]["start_year"]
                    self.datadist["topics"][key]["end_year"] = self.topicdist[key]["end_year"]
            
    def outputData(self, outfilename):
        with open(outfilename, 'w') as outfile:
            json.dump(self.datadist, outfile, indent=1, separators=(',', ': '))

def main():
    ad = AddDist()
    ad.loadDist("./pub_artificial_intelligence.dist", 1975, 2014)
    ad.loadData("./visual_artificial_intelligence.json")
    ad.outputData("./visual_artificial_intelligence_complete.json")

if __name__ == '__main__':
    main()
        