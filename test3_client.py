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

        self.upload_file(self.file_paths)

        #关闭客户端的写方向，但是还可以从服务器读取数据回来   
        # self.client_socket.shutdown(socket.SHUT_WR)
        self.client_socket.shutdown(SHUT_WR)
        
        self.result_receive_file()
        
        self.client_socket.close()
        
        self.finished.emit(1)

    def upload_file(self, file_paths):
        # 发送文件数量
        num_files = len(file_paths)
        print("客户端发送的文件：", num_files)
        self.client_socket.sendall(str(num_files).encode())
        server_response = self.client_socket.recv(self.BUFLEN)
        #调试信息
        i = 1
        if server_response == b'OK':
            for file_path in file_paths:
                # 获取文件名
                file_name = file_path.split('/')[-1]
                print("文件名为：" + file_name)

                # 发送文件名并等待服务器响应
                self.client_socket.sendall(file_name.encode())
                server_response = self.client_socket.recv(self.BUFLEN)
                print("调试信息1")
                if server_response == b'OK':
                    file_size = int(os.path.getsize(file_path))
                    print("文件大小：", file_size)
                    # 发送文件大小
                    self.client_socket.sendall(str(file_size).encode())
                    server_response = self.client_socket.recv(self.BUFLEN)
                    print("调试信息2")
                    upload_size = 0
                    if server_response == b'OK':                           
                        # 读取并发送文件内容
                        with open(file_path, "rb") as file:
                            j = 0
                            while upload_size < file_size:
                                print("调试信息3")
                                file_data = file.read(self.BUFLEN)
                                print("调试信息34")
                                # 发送文件数据
                                self.client_socket.sendall(file_data)
                                upload_size += len(file_data)
                                #应该是比较稳妥的判断
                                # if len(file_data) < 1024:
                                #     break
                                print("调试信息4")
                                #调试信息
                                j += 1
                                print(file_name, "一个文件发送次数：", j)
                                # if upload_size >= file_size:
                                #     break
                        server_response = self.client_socket.recv(self.BUFLEN)
                        if server_response == b'OK':
                            # 发送文件结束标记
                            self.client_socket.sendall(b'EOF')
                            print("调试信息45")
                            server_response = self.client_socket.recv(self.BUFLEN)
                            print("调试信息5")
                            if server_response == b'OK':
                                print('文件传输完成')
                            #调试信息
                            print(f"次数：{i}")
                            i += 1
                            #发送完一个文件就加一
                            self.current_upload_files += 1            
                            self.progressUpdated.emit(int(self.current_upload_files / self.total_files * 100))
        print("调试信息6")
        # 发送全部文件传输完成标记
        self.client_socket.sendall(b'FINISH')
        print("调试信息7")
        server_response = self.client_socket.recv(self.BUFLEN)
        print("调试信息8")
        if server_response == b'OK':
            print('全部文件传输完成')
        self.finished.emit(1)
        
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