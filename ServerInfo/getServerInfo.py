import os, gzip, pathlib
from ServerInfo.serverModel import ServerModel
from datetime import datetime

class getServerInfo():
    def __init__(self, serverPath):
        self.serverPath = serverPath
        self.logCount = 0
        self.server = ServerModel()
        for file in os.listdir(str(self.serverPath + "\logs")):
            valid = True
            self.filename = os.fsdecode(file)
            if "debug" in self.filename or "latest" in self.filename:
                valid = False
            if valid:
                contents = self.openContents(f"{self.serverPath}\logs\{self.filename}")
                if contents != "Error":
                    self.logCount += 1
                    self.calculateStatistics(contents)
                    print(f"Logs searched: {self.logCount}")
        self.printServerStats()
    
    def openContents(self, file):
        try:
            #print(f"Opened File {file}")
            file = gzip.open(file, "r")
            lines = file.readlines()
            return lines
        except:
            try:
                #print(f"Opened File {file}")
                file = open(file, "r")
                lines = file.readlines()
                return lines
            except:
                print("Error Opening File!")
                return "Error"
    
    def calculateStatistics(self,contents):
        contents = self.convertContentsToString(contents)
        self.getName()
        self.getTotalUptime(contents)
        self.findTotalAdvancements(contents)
        self.findCrash(contents)
        self.findModLoader(contents)
    
    def getName(self):
        self.server.serverName = str(os.path.normpath(self.serverPath).split(os.sep)[-1:]).strip("['").strip("']")
    
    def getTotalUptime(self, contents):
        firstLine = contents[0]

        # Calculate Start Time
        startTime = f"{firstLine.split(' ')[0]} {firstLine.split(' ')[1]}".strip("]").strip("[")
        
        #Convert string to date time
        line = list(startTime)
        day = int(str(line[0]) + str(line[1]))
        month = int(datetime.strptime(str(line[2] + line[3] + line[4]), "%b").month)
        year = int(str(line[5]) + str(line[6]) + str(line[7]) + str(line[8]))
        hour = int(str(line[10]) + str(line[11]))
        minute = int(str(line[13]) + str(line[14]))
        second = int(str(line[16]) + str(line[17]))

        startTime = datetime(year, month, day, hour, minute, second)

        #Calculate Finish Time
        falseLine = True
        i = -1
        lastLine = contents[i:][0]
        while falseLine: ## This is done as some files end without a date
            try:
                endTime = f"{lastLine.split(' ')[0]} {lastLine.split(' ')[1]}".strip("]").strip("[")

                #Convert string to date time
                line = list(endTime)
                day = int(str(line[0]) + str(line[1]))
                month = int(datetime.strptime(str(line[2] + line[3] + line[4]), "%b").month)
                year = int(str(line[5]) + str(line[6]) + str(line[7]) + str(line[8]))
                hour = int(str(line[10]) + str(line[11]))
                minute = int(str(line[13]) + str(line[14]))
                second = int(str(line[16]) + str(line[17]))
                falseLine = False
            except:
                i -= 1
                lastLine = contents[i:][0]

        endTime = datetime(year, month, day, hour, minute, second)

        # Calculate Time Difference
        timeDifference = endTime - startTime
        self.server.totalUptime += timeDifference.total_seconds()


    def convertContentsToString(self, contents):
        for line in contents:
            templine = line.decode("utf-8")
            idx = contents.index(line)
            contents[idx] = templine
        return contents
    
    def findTotalAdvancements(self, contents):
        for line in contents:
            if "advancements" in line and "Loaded" in line:
                self.server.totalAdvancements = line.split(" ")[5]

    def findCrash(self, contents):
        for line in contents:
            if "Preparing crash report" in line:
                self.server.crashes += 1
    
    def findModLoader(self, contents):
        keywords = open("ServerInfo\modloaderKeywords.txt","r").readlines()
        for keyword in keywords:
            keywordStripped = keyword.strip("\n")
            idx = keywords.index(keyword)
            keywords[idx] = keywordStripped

        for line in contents:
            for keyword in keywords:
                if "forge" in line.lower(): ## sets line to lowercase for consistency
                    if keyword == "forge":
                        self.server.moddedServer = "Forge"
                    elif keyword == "fabric":
                        self.server.moddedServer = "Fabric"

    

    def printServerStats(self):
        print(f"Server Name: {self.server.serverName}")
        print(f"Up Time: {self.server.totalUptime}")
        print(f"Mod Server Type: {self.server.moddedServer}")
        print(f"Total number of crashes: {self.server.crashes}")
        print(f"Total Advancements: {self.server.totalAdvancements}")