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
        super(MW,self).__init__()
        self.setupUi(self)
        
        self.imgName = []#用来存储图片的名字
        self.imgPathName = []#用来存储图片的路径+名字
        self.pushButton.clicked.connect(self.upLoadImage)
        
        self.label.setPixmap(QPixmap("./images/Python.png"))
        self.listView.doubleClicked.connect(self.clicked)
        self.listView.clicked.connect(self.clicked)
        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)#右键菜单
        self.listView.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow)
        
        self.slm = QStringListModel()#在listView中显示字符串
        self.listView.setModel(self.slm)
        
    def upLoadImage(self):
        global imgPathNames
        imgPathNames,imgType = QtWidgets.QFileDialog.getOpenFileNames(self, "多文件选择", "/", "图像文件 (*.png *.jpg *.jpeg)")
        fileNames = [QFileInfo(fileName).fileName() for fileName in imgPathNames]#提取图片的名字
        self.imgName.extend(fileNames)#收集图片的名字
        self.imgPathName.extend(imgPathNames)#收集图片的路径＋名字
        self.slm.setStringList(self.imgName)#在列表中显示图片的名字
        
    def rightMenuShow(self):
        rightMenu = QtWidgets.QMenu(self.listView)
        removeAction = QtWidgets.QAction(u"Delete", self, triggered=self.removeimage)       # triggered 为右键菜单点击后的激活事件。这里slef.close调用的是系统自带的关闭事件。
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())
        
        
    def clicked(self, qModelIndex):
        QMessageBox.information(self, "QListView", "你选择了: "+ self.imgPathName[qModelIndex.row()])#这里要使用完整的路径，用imgPathName
        global path
        self.label.setPixmap(QPixmap(self.imgPathName[qModelIndex.row()]))
        path = self.imgPathName[qModelIndex.row()]
        print(path)
        
    def removeimage(self):
        selected = self.listView.selectedIndexes()
        itemmodel = self.listView.model()
        for i in selected:
            itemmodel.removeRow(i.row())
              
                     
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MW()
    mw.show()
    sys.exit(app.exec_())