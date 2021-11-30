from PlayerStats.findPlayerStats import *
from ServerInfo.getServerInfo import *
import gui
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
__version__ = "0.2.1"
__beta__ = False



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Widget = QtWidgets.QWidget()
    ui = gui.Ui_Widget()
    ui.setupUi(Widget)

    if len(open("cache/serverLocations.txt").readlines()) <= 0:
        noPreviousLocation = True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("You do not appear to have any previous server locations selected.")
        msg.setInformativeText("No worries! We'll popup a box to let you select one. Simply select the server directory ONLY!")
        msg.setWindowTitle("No previous locations found!")
        msg.exec_()

        while noPreviousLocation:
            location = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
            if location != "":
                noPreviousLocation = False
                with open("cache/serverLocations.txt","a") as file:
                    file.write(str(location) + "\n")
                    file.close()
                
                with open("cache/mostRecentServer.txt","a") as file:
                    file.write(str(location) + "\n")
                    file.close()

    elif len(open("cache/mostRecentServer.txt").readlines()) <= 0:
        location = open("cache/serverLocations.txt").readlines()[0].strip("\n")
        with open("cache/mostRecentServer.txt","a") as file:
                    file.write(str(location) + "\n")
                    file.close()

        
    
    ## Create start.bat file
    batFile = open(f"{location}\start.bat","w")
    batFile.write("java -Xmx4G -Xms2G -jar forge-1.16.5-36.2.0.jar nogui")
    batFile.close()

    Widget.show()

    sys.exit(app.exec_())


#path = input("Path to server file: ")