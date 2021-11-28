import os, gzip
from datetime import datetime, time
from PlayerStats.PlayerModel import *
import requests, json



class Main:
    def __init__(self, serverPath):
        self.totalPlaytime = 0
        self.serverPath = serverPath
        self.findPlayers()
        self.clearPlayerFiles()
        for file in os.listdir(str(self.serverPath + "\logs")):
            valid = True
            filename = os.fsdecode(file)
            if "debug" in filename or "latest" in filename:
                valid = False
            
            if valid:
                contents = self.openContents(f"{self.serverPath}\logs\{filename}")
                if contents != "Error":
                    self.filterContents(contents)
        self.calculatePlayTime()
        self.printAllPlayerInfo()
    
    def findPlayers(self):
        print("Finding players...")
        open("PlayerStats\players.txt","w").close() #clear players file
        for file in os.listdir(str(self.serverPath + "\world\playerdata")):
            if "old" not in file:
                uuid = file.strip(".dat")
                name = requests.get(f"https://api.mojang.com/user/profile/{uuid}")
                try:
                    name = json.loads(name.text)['name']
                    print(f"New Player Found! {name}")
                    with open("PlayerStats\players.txt","a") as playerFile:
                        playerFile.write(name + "\n")
                        playerFile.close()
                except:
                    pass
        #if "Nuschy" not in open("PlayerStats\players.txt","r").readlines():
        #    file = open("PlayerStats\players.txt","a")
        #    file.write("Nuschy")
        #    file.close()
        #### The above commented out lines were for a player of this specific server, please ignore
               

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
    
    def clearPlayerFiles(self):
        self.players = open("PlayerStats\players.txt","r").readlines()
        for player in self.players:
            player = player.strip("\n")
            open(f"PlayerStats\playerData\{player}.txt","w+").close() # Clears previous player file
            open(f"PlayerStats\playerData\{player}.txt","w").close() # Clears previous player file

    def filterContents(self, contents):
        for player in self.players:
            player = player.strip("\n")
            for line in contents:
                line = line.decode("utf-8")
                line = line.strip("\n").strip("\r") + "\n"
                if player in line:
                    with open(f"PlayerStats\playerData\{player}.txt","a") as playerFile:
                        playerFile.write(line)
                    playerFile.close()
            with open(f"PlayerStats\playerData\{player}.txt","a") as playerFile:
                playerFile.write("###\n") # Splitter value to split the different values apart
                playerFile.close()

    def calculatePlayTime(self):
        self.playerObjects = []
        for file in os.listdir("PlayerStats\playerData"):
            totalTime = 0
            currentPlayer = file.strip(".txt")
            contents = open(f"PlayerStats\playerData\{file}").readlines()

            newPlayer = PlayerModel()
            newPlayer.name = currentPlayer

            playerOnlineTimes = []
            onlineTime = []
            for line in contents:
                line = line.strip("\n")
                if "###" not in line:
                    onlineTime.append(line)
                else:
                    playerOnlineTimes.append(onlineTime)
                    onlineTime = []
        
            ## Calculate Time Played
            for i in range(0,len(playerOnlineTimes)):
                for line in playerOnlineTimes[i]:
                    if "joined the game" in line:
                        line = line.split("]")[0].strip("[")
                        line = list(line)
                        day = int(str(line[0]) + str(line[1]))
                        month = int(datetime.strptime(str(line[2] + line[3] + line[4]), "%b").month)
                        year = int(str(line[5]) + str(line[6]) + str(line[7]) + str(line[8]))
                        hour = int(str(line[10]) + str(line[11]))
                        minute = int(str(line[13]) + str(line[14]))
                        second = int(str(line[16]) + str(line[17]))

                        joinTime = datetime(year, month, day, hour, minute, second)
                    if "left the game" in line or "Stopping the server" in line: ## Not all players leave before server stop
                        line = line.split("]")[0].strip("[")
                        line = list(line)
                        day = int(str(line[0]) + str(line[1]))
                        month = int(datetime.strptime(str(line[2] + line[3] + line[4]), "%b").month)
                        year = int(str(line[5]) + str(line[6]) + str(line[7]) + str(line[8]))
                        hour = int(str(line[10]) + str(line[11]))
                        minute = int(str(line[13]) + str(line[14]))
                        second = int(str(line[16]) + str(line[17]))

                        leaveTime = datetime(year, month, day, hour, minute, second)

                        timeDifference = (leaveTime - joinTime).total_seconds()
                        totalTime += timeDifference
                        newPlayer.totalPlaytime = totalTime

                    if "server operator" in line: # Server Operator Yes
                        print(line)
                        newPlayer.serverOperator = True

                    if "no longer a server operator" in line: # Server Operator No
                        print(line)
                        newPlayer.serverOperator = False

                    if "made the advancement" in line: ## Advancement Tracker
                        newPlayer.advancementsMade += 1
                        advancement = line.split("[")[4].strip("]")
                        newPlayer.advancements.append(advancement)

                    if "UUID" in line: ## UUID
                        uuid = line.split(" ")
                        uuid = uuid[len(uuid)-1]
                        newPlayer.uuid = uuid

                    if "logged in with entity id" in line: ## IP Address
                        ipLine = line.split("/")[3]
                        ip = ipLine.split("]")[0].split(":")[0]
                        if ip not in newPlayer.ips:
                            newPlayer.ips.append(ip)

            self.playerObjects.append(newPlayer)
            
            
            
    
    def printAllPlayerInfo(self):
        print(self.playerObjects)
        for player in self.playerObjects:
            print(f"Player: {player.name}")
            print(f"Total Play Time:{player.totalPlaytime}")
            print(f"Server Operator: {player.serverOperator}")
            print(f"Advancements: {player.advancementsMade}")
            print(f"UUID: {player.uuid}")
            print(player.ips)
            print("")
