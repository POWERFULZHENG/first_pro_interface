from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from interface import Ui_Form
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import os
import time

class UploadThread(QThread):
    progressUpdated = pyqtSignal(int)  # 上传进度信号
    finished = pyqtSignal(int)  # 上传完成信号
    
    def __init__(self, file_paths):
        super(UploadThread, self).__init__()
        self.file_paths = file_paths
        
    def run(self):
        url = "http://example.com/upload"  # 上传服务器的 URL
        # 创建网络访问管理器和请求对象
        # manager = QNetworkAccessManager()
        
        # total_files = len(self.file_paths)
        # uploaded_files = 0        
        # for file_path in self.file_paths:
        #     request = QNetworkRequest(QUrl(url))
        #     # 打开待上传的文件
        #     file = open(file_path, "rb")
        #     # 设置请求头，指定 Content-Type
        #     request.setHeader(QNetworkRequest.ContentTypeHeader, "image/jpeg")
        #     # 获取文件大小
        #     file_size = os.path.getsize(file_path)
            
        #     file_content = file.read()  # 读取文件内容
        #     byte_array = QByteArray(file_content)  # 将文件内容存储在 QByteArray 中
        #     # 发送请求并读取响应
        #     reply = manager.put(request, byte_array)
        #     # 读取响应数据，模拟上传过程
        #     bytes_uploaded = 0
        #     while not reply.isFinished():
        #         data = reply.readAll()
        #         bytes_uploaded += len(data)           
        #         # 计算上传进度
        #         progress = int(bytes_uploaded / file_size * 100)
        #         # 发送上传进度信号
        #         self.progressUpdated.emit(progress)
        #     file.close()
            
        #     uploaded_files += 1
        #     # 计算总体进度           
        #     total_progress = int(uploaded_files / total_files * 100)
            # 发送总体进度信号
        self.progressUpdated.emit(50)
        time.sleep(5)
        self.finished.emit(1)

class MW(Ui_Form, QWidget):
    def __init__(self, parent=None):
        super(MW, self).__init__()
        self.setupUi(self)
        
        self.imgName = []  # 用来存储图片的名字
        self.imgPathName = []  # 用来存储图片的路径+名字
        self.pushButton.clicked.connect(self.upLoadImage)
        
        self.label.setPixmap(QPixmap("./images/Python.png"))
        #设置label标签的大小
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.tableWidget.itemClicked.connect(self.clicked)
        self.tableWidget.itemDoubleClicked.connect(self.clicked)
        
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # 右键菜单
        self.tableWidget.customContextMenuRequested.connect(self.rightMenuShow)
        
        #多线程进度条部分
        self.uploadThread = None
    
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
        
        #进度条部分+创建线程
        if imgPathNames:
            self.progressBar.setValue(0)
            self.imageLabel.clear()
            self.uploadThread = UploadThread(imgPathNames)
            self.uploadThread.progressUpdated.connect(self.updateProgress)
            self.uploadThread.finished.connect(self.uploadFinished)
            self.uploadThread.start()
    
    #进度条
    def updateProgress(self, progress):
        self.progressBar.setValue(progress)
    def uploadFinished(self, is_done):
        if is_done == 1:
            self.progressBar.setValue(100)
            self.imageLabel.setText("上传完成！")
            self.uploadThread = None
    
    #点击表格预览图片    
    def clicked(self, qModelIndex):
        # QMessageBox.information(self, "QtableWidget", "你选择了: " + self.imgPathName[qModelIndex.row()])  # 这里要使用完整的路径，用imgPathName
        global path
        row = qModelIndex.row()
        if row >= 0 and row < len(self.imgPathName):#判断是否在该数组的范围内
            #缩放图片，自适应窗口——new
            image = QPixmap(self.imgPathName[row])
            # 获取标签的大小
            label_size = self.label.size()            
            # 获取图片的原始大小
            image_size = image.size()           
            # 计算缩放比例
            scale_factor = min(label_size.width() / image_size.width(), label_size.height() / image_size.height())            
            # 缩放图片
            scaled_image = image.scaled(image_size * scale_factor)
            self.label.setPixmap(scaled_image)
            path = self.imgPathName[row]
            print(path)
    
    #自适应窗口大小调整label标签的图片，主窗口需要继承自类QMainWindow，并正确地调用了父类的resizeEvent方法
    #resizeEvent是QWidget类（或其子类）的一个事件处理函数。它用于处理窗口或控件的大小调整事件。
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