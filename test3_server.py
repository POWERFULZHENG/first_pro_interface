# -*- coding: utf-8 -*-
#  === TCP 服务端程序 test3_server.py ===
# 服务器端代码
import socket
import os

# 主机地址为空字符串，表示绑定本机所有网络接口ip地址
# 等待客户端来连接
# IP = '192.168.1.104'
# IP = 'DESKTOP-IV28T95'
IP = '192.168.1.104'
# 端口号
PORT = 50000
# 定义一次从socket缓冲区最多读入1024个字节数据
BUFLEN = 1024

def process_image(image_data):
    # 在此处编写图片处理逻辑，可以使用图像处理库或自定义算法
    # 处理后的结果生成新的图片数据
    processed_image_data = image_data  # 这里只是示例，将原始图片数据作为处理结果

    return processed_image_data

def handle_client(client_socket):
    while True:
        # 接收文件数量
        data = client_socket.recv(BUFLEN).decode()
        if not data:
            break
        num_files = int(data)
        print('文件数量:', num_files)

        # 发送确认给客户端
        client_socket.sendall("OK".encode())

        for _ in range(num_files):
            # 接收文件名
            data = client_socket.recv(BUFLEN).decode()
            print("调试信息1")
            if not data:
                break
            file_name = data
            print('收到文件名:', file_name)

            # 发送确认给客户端
            client_socket.sendall("OK".encode())

            # 接收文件大小
            file_size = int(client_socket.recv(BUFLEN).decode())
            print("接收文件大小:", file_size)
            print("调试信息2")
            # 发送确认给客户端
            client_socket.sendall("OK".encode())

            # 接收并保存文件内容
            save_folder = "uploads"
            os.makedirs(save_folder, exist_ok=True)
            save_path = os.path.join(save_folder, file_name)
            with open(save_path, "wb") as file:
                received_size = 0
                j = 0
                while received_size < file_size:
                    print("调试信息23")
                    data = client_socket.recv(BUFLEN)
                    print("调试信息3")
                    file.write(data)
                    received_size += len(data)
                    if len(data) < 1024:
                        break
                    if received_size >= file_size:
                        break
                client_socket.sendall("OK".encode())
                print("调试信息34")
                data = client_socket.recv(BUFLEN)
                print("调试信息4")
                if data == b'EOF':
                    # 发送文件接收完成确认
                    client_socket.sendall("OK".encode())
                    print("文件已保存:", save_path)

            print("调试信息5")
        # 接收全部文件传输完成标记
        data = client_socket.recv(BUFLEN)
        # print(data.decode())
        print("调试信息5")
        if data == b'FINISH':
            print('全部文件传输完成')
            # 发送确认给客户端
            client_socket.sendall("OK".encode())
            break
                    
    print('接收完毕，开始处理图片...')

    # 处理完成后，将结果发送回客户端   
    result = "Processing result"
    upload_size = 0
    result_file_path = os.path.join(save_folder, "result.txt")

    with open(result_file_path, "rb") as result_file:
        while True:
            data = result_file.read()[upload_size:upload_size + 1024]
            if not data:
                break
            client_socket.sendall(data)
        print('图片处理完成，发送结果回客户端...')
        print('结果发送完成，关闭连接。')

    client_socket.close()
    #server_socket.close()

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    # 使socket处于监听状态，等待客户端的连接请求
    # 参数 1 表示 最多接受多少个等待连接的客户端
    server_socket.listen(1)

    print(f'服务端启动成功，在{IP}:{PORT}端口等待客户端连接...')

    while True:
        client_socket, client_address = server_socket.accept()
        print('客户端已连接:', client_address)

        handle_client(client_socket)