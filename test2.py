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
        self.tableWidget.itemClicked.connect(self.clicked)
        self.tableWidget.itemDoubleClicked.connect(self.clicked)
        
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # 右键菜单
        self.tableWidget.customContextMenuRequested.connect(self.rightMenuShow)
    
    #上传图片到系统    
    def upLoadImage(self):
        global imgPathNames
        imgPathNames, imgType = QtWidgets.QFileDialog.getOpenFileNames(self, "多文件选择", "/", "图像文件 (*.png *.jpg *.jpeg)")
        fileNames = [QFileInfo(fileName).fileName() for fileName in imgPathNames]  # 提取图片的名字
        self.imgName.extend(fileNames)  # 收集图片的名字
        self.imgPathName.extend(imgPathNames)  # 收集图片的路径+名字
        
        self.tableWidget.clearContents()  # 清除表格内容
        self.tableWidget.setRowCount(len(self.imgName)) # 设置行数
        for row, (imgName_1, imgPathName_1) in enumerate(zip(self.imgName, self.imgPathName)):#zip组合他们俩，返回元组，用到了枚举循环遍历
            nameItem = QTableWidgetItem(imgName_1)#创建QTableWidgetItem对象，填充表格
            self.tableWidget.setItem(row, 0, nameItem)
    
    #点击表格预览图片    
    def clicked(self, qModelIndex):
        # QMessageBox.information(self, "QtableWidget", "你选择了: " + self.imgPathName[qModelIndex.row()])  # 这里要使用完整的路径，用imgPathName
        global path
        row = qModelIndex.row()
        if row >= 0 and row < len(self.imgPathName):#判断是否在该数组的范围内
            self.label.setPixmap(QPixmap(self.imgPathName[row]))
            path = self.imgPathName[row]
            print(path)
    
    #自适应窗口大小调整label标签的图片，主窗口需要继承自类QMainWindow，并正确地调用了父类的resizeEvent方法
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.label.setScaledContents(True)
        self.label.resize(event.size())
    
    #右键表格菜单    
    def rightMenuShow(self, pos):
        rightMenu = QtWidgets.QMenu(self.tableWidget)
        removeAction = QtWidgets.QAction("Delete", self, triggered=self.removeImage)  # triggered 为右键菜单点击后的激活事件
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())
    
    #右键删除项目函数    
    def removeImage(self):
        selected = self.tableWidget.selectedIndexes()
        for index in reversed(selected):
            self.tableWidget.removeRow(index.row())
            del self.imgName[index.row()]
            del self.imgPathName[index.row()]
        self.updateRowNumbers()
    
    #更新表格行号    
    def updateRowNumbers(self):
        for row in range(self.tableWidget.rowCount()):
            item = QTableWidgetItem(str(row + 1))
            self.tableWidget.setVerticalHeaderItem(row, item)     
                     
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MW()
    mw.show()
    sys.exit(app.exec_())