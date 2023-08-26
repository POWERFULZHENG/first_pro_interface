from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from interface import Ui_Form

class MW(Ui_Form, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MW, self).__init__()
        self.setupUi(self)
        
        self.imgName = []  # 用来存储图片的名字
        self.imgPathName = []  # 用来存储图片的路径+名字
        self.pushButton.clicked.connect(self.upLoadImage)
        
        self.label.setPixmap(QPixmap("./images/Python.png"))
        self.tableView.doubleClicked.connect(self.clicked)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)  # 右键菜单
        self.tableView.customContextMenuRequested.connect(self.rightMenuShow)
        
        self.tableModel = QStandardItemModel()
        self.tableView.setModel(self.tableModel)
        
        self.tableView.setSortingEnabled(True)  # 启用排序
        
    def upLoadImage(self):
        global imgPathNames
        imgPathNames, imgType = QtWidgets.QFileDialog.getOpenFileNames(self, "多文件选择", "/", "图像文件 (*.png *.jpg *.jpeg)")
        fileNames = [QFileInfo(fileName).fileName() for fileName in imgPathNames]  # 提取图片的名字
        self.imgName.extend(fileNames)  # 收集图片的名字
        self.imgPathName.extend(imgPathNames)  # 收集图片的路径+名字
        
        self.tableModel.clear()  # 清除已有数据
        self.tableModel.setHorizontalHeaderLabels(["Image Name"])  # 设置表头
        for imgName in self.imgName:
            item = QStandardItem(imgName)
            self.tableModel.appendRow(item)
        
    def rightMenuShow(self, pos):
        rightMenu = QtWidgets.QMenu(self.tableView)
        removeAction = QtWidgets.QAction("Delete", self, triggered=self.removeImage)  # triggered 为右键菜单点击后的激活事件
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())
        
    def clicked(self, qModelIndex):
        QMessageBox.information(self, "QTableView", "你选择了: " + self.imgPathName[qModelIndex.row()])  # 这里要使用完整的路径，用imgPathName
        global path
        self.label.setPixmap(QPixmap(self.imgPathName[qModelIndex.row()]))
        path = self.imgPathName[qModelIndex.row()]
        print(path)
        
    def removeImage(self):
        selected = self.tableView.selectedIndexes()
        for index in selected:
            self.tableModel.removeRow(index.row())
            del self.imgName[index.row()]
            del self.imgPathName[index.row()]
              
                     
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MW()
    mw.show()
    sys.exit(app.exec_())