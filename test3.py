import threading
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
        #取消进度框标志
        self.is_canceled = False
        # 获取当前活动的线程数
        self.active_threads = get_active_thread_count()
        print("当前活动线程数：", self.active_threads) 
        
    def run(self):
        print("-----UploadThread线程开启------")     
        total_files = len(self.file_paths)
        uploaded_files = 0
        total_progress = 0     
        for i in range(total_files):
            if self.is_canceled:
                break           
            uploaded_files += 1
            #这里模拟待处理的功能，需要放置功能代码
            time.sleep(2)
            # 计算总体进度           
            total_progress = int(uploaded_files / total_files * 100)
            #一定得这样判断，否者得点击两次取消按钮才行
            if not self.is_canceled:
            # 发送总体进度信号
                self.progressUpdated.emit(total_progress)
        if 100 == total_progress:    
            self.finished.emit(1)                 
    def cancel_upload(self):
        self.is_canceled = True


class MW(Ui_Form, QWidget):
    def __init__(self, parent=None):
        super(MW, self).__init__()
        self.setupUi(self)
        
        self.imgName = []  # 用来存储全部图片的名字
        self.imgPathName = []  # 用来存储全部图片的路径+名字
        self.imgPathNames = []  # 用来存储图片的路径+名字
        self.pushButton.clicked.connect(self.upLoadImage)
        self.uploadButton.clicked.connect(self.creatProgressDialog)
        
        self.label.setPixmap(QPixmap("./images/Python.png"))
        #设置label标签的大小
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.tableWidget1.itemClicked.connect(self.clicked)
        self.tableWidget1.itemDoubleClicked.connect(self.clicked)
        
        self.tableWidget1.setContextMenuPolicy(Qt.CustomContextMenu)  # 右键菜单
        self.tableWidget1.customContextMenuRequested.connect(self.rightMenuShow)
        
        # self.status_bar = self.statusBar()
        # self.statusBar().showMessage("Status: Updated")        
    
    #上传图片到系统    
    def upLoadImage(self):
        self.imgPathNames, imgType = QtWidgets.QFileDialog.getOpenFileNames(self, "多文件选择", "/", "图像文件 (*.png *.jpg *.jpeg)")
        
        fileNames = [QFileInfo(fileName).fileName() for fileName in self.imgPathNames]  # 提取图片的名字
        self.imgName.extend(fileNames)  # 收集图片的名字
        self.imgPathName.extend(self.imgPathNames)  # 收集图片的路径+名字
        
        self.tableWidget1.clearContents()  # 清除表格内容
        self.tableWidget1.setRowCount(len(self.imgName)) # 设置行数
        for row, (imgName_1, imgPathName_1) in enumerate(zip(self.imgName, self.imgPathName)):#zip组合他们俩，返回元组，用到了枚举循环遍历
            nameItem = QTableWidgetItem(imgName_1)#创建QTableWidgetItem对象，填充表格
            self.tableWidget1.setItem(row, 0, nameItem)
        #路径显示   
        self.image_directory = os.path.dirname(str(self.imgPathNames[0]))#变量得是实例变量，否则不显示
        self.textEdit.setPlainText(f"-----本次处理的图片所在路径:{self.image_directory}-----\n")                     
    
    #创建进度条    
    def creatProgressDialog(self):
        #进度条部分+创建线程
        #创建线程
        self.uploadThread = UploadThread(self.imgPathNames)
        self.uploadThread.progressUpdated.connect(self.updateProgress)
        self.uploadThread.finished.connect(self.uploadFinished)            
        #启动线程
        self.uploadThread.start()        
        if self.imgPathNames and self.uploadThread:       
            self.progress_dialog = QProgressDialog('', '', 0, 100, mw)#需要正确继承父级窗口
            self.progress_dialog.setFixedSize(400, 200)
            self.progress_dialog.setWindowTitle('上传中')
            self.progress_dialog.setLabelText('当前发送进度值')
            self.progress_dialog.setCancelButtonText('取消')
            self.progress_dialog.setRange(0, 100)
            self.progress_dialog.canceled.connect(self.cancel_upload)
            self.progress_dialog.setAutoClose(True)#value为最大值时自动关闭
            self.progress_dialog.setValue(0)
            # self.progress_dialog.setModal(True)  # 设置为模态
            self.progress_dialog.show()#显示出来
    
    #进度条
    def updateProgress(self, progress):
        #判断该线程是否存在
        if self.progress_dialog:
            self.progress_dialog.setValue(progress)
            self.textEdit.append("-----发送图片ing-----\n")                    

    def uploadFinished(self, is_done):
        if is_done == 1:
            self.progress_dialog.setValue(100)
            self.textEdit.append("-----发送成功！-----\n")
            self.imgPathNames = []
            self.uploadThread = None
            
    def cancel_upload(self):
        self.imgPathNames = []
        if self.uploadThread:
            self.uploadThread.cancel_upload()
            self.uploadThread.wait()  # 等待线程完成
            self.progress_dialog.close()
            self.textEdit.setPlainText("已取消上传文件！\n")
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
        rightMenu = QtWidgets.QMenu(self.tableWidget1)
        removeAction = QtWidgets.QAction("Delete", self, triggered=self.removeImage)  # triggered 为右键菜单点击后的激活事件
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())
    
    #右键删除项目函数    
    def removeImage(self):
        selected = self.tableWidget1.selectedIndexes()
        for index in reversed(selected):
            self.tableWidget1.removeRow(index.row())
            del self.imgName[index.row()]
            del self.imgPathName[index.row()]
        self.updateRowNumbers()
    
    #更新表格行号    
    def updateRowNumbers(self):
        for row in range(self.tableWidget1.rowCount()):
            item = QTableWidgetItem(str(row + 1))
            self.tableWidget1.setVerticalHeaderItem(row, item)     


def get_active_thread_count():
    # 获取当前活动的线程数
    return threading.active_count()  # 减去主线程

                    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MW()
    mw.show()
    sys.exit(app.exec_())