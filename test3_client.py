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
import socket
from socket import *
from PyQt5.QtNetwork import QAbstractSocket

class UploadThread(QThread):
    progressUpdated = pyqtSignal(int)  # 上传进度信号
    finished = pyqtSignal(int)  # 上传完成信号
    resultReceived = pyqtSignal(bytes)
    IP = '127.0.0.1'
    SERVER_PORT = 50000
    BUFLEN = 1024

    def __init__(self, file_paths, host, port, parent = None):
        super().__init__()
        self.host = host
        self.port = port
        self.file_paths  = file_paths
        self.total_files = len(file_paths)
        self.current_upload_files = 0

    def run(self):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        #调试信息
        i = 1
        for file_path in self.file_paths:
            # if self.is_canceled:
            #     break
            self.upload_file(file_path)
            print(f"次数：{i}")
            #发送完一个文件就加一
            self.current_upload_files += 1
            
            self.progressUpdated.emit(int(self.current_upload_files / self.total_files * 100))
        #关闭客户端的写方向，但是还可以从服务器读取数据回来   
        # self.client_socket.shutdown(socket.SHUT_WR)
        self.client_socket.shutdown(SHUT_WR)
        
        self.result = self.result_receive_file()
        
        self.client_socket.close()
        
        self.finished.emit(1)

    def upload_file(self, file_path):
        #获取文件名
        file_name = file_path.split('/')[-1]
        print("文件名字为：" + file_name)

        # 发送文件名并等待服务器响应
        self.client_socket.sendall(file_name.encode())
        print("调试信息1")
        server_response = self.client_socket.recv(self.BUFLEN)
        print("调试信息2")
        if server_response == b'OK':
            # 读取并发送文件内容
            with open(file_path, "rb") as file:
                file_data = file.read()
                file_size = len(file_data)
                
                # 发送文件大小
                self.client_socket.sendall(str(file_size).encode())
                print("两次ok")
                # 等待服务器确认
                server_response = self.client_socket.recv(self.BUFLEN)

                if server_response == b'OK':
                    sent_size = 0
                    # 发送文件数据
                    while sent_size < file_size:
                        print("调试信息3")
                        data = file.read(self.BUFLEN)
                        if not data:
                            break
                        self.client_socket.sendall(data)
                        sent_size += len(data)
                        print("调试信息4")
        
    def result_receive_file(self):
        # 接收处理结果
        # result = b''
        # 接收服务器返回的结果
        result_folder = "results"
        os.makedirs(result_folder, exist_ok=True)
        result_file_path = os.path.join(result_folder, "result.txt")

        with open(result_file_path, "wb") as result_file:
            while True:
                data = self.client_socket.recv(self.BUFLEN)
                if not data:
                    break
                # result += data
                result_file.write(data)
        
    def cancel_upload(self):
        self.is_canceled = True
        
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.progress_dialog = None

        # 显示文件选择对话框
        file_paths, _ = QFileDialog.getOpenFileNames(self, "选择文件", filter="Images (*.png *.xpm *.jpg)")

        if file_paths:
            # 创建并显示进度对话框
            self.progress_dialog = QProgressDialog("上传中...", "取消", 0, 100, self)
            self.progress_dialog.setWindowTitle("文件上传")
            self.progress_dialog.setWindowModality(Qt.ApplicationModal)
            self.progress_dialog.setAutoClose(True)
            self.progress_dialog.setAutoReset(False)
            self.progress_dialog.show()

            # 创建上传线程
            self.upload_thread = UploadThread(file_paths, '192.168.1.104', 50000)
            self.upload_thread.progressUpdated.connect(self.update_progress)
            self.upload_thread.finished.connect(self.upload_finished)
            self.upload_thread.start()

    def update_progress(self, progress):
        if self.progress_dialog:
            self.progress_dialog.setValue(progress)

    def upload_finished(self):
        if self.progress_dialog:
            self.progress_dialog.close()
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())