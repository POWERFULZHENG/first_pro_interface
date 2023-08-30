#  === TCP 服务端程序 test3_server.py ===
# 服务器端代码
import socket

# 主机地址为空字符串，表示绑定本机所有网络接口ip地址
# 等待客户端来连接
IP = ''
# 端口号
PORT = 50000
# 定义一次从socket缓冲区最多读入1024个字节数据
BUFLEN = 1024

def process_image(image_data):
    # 在此处编写图片处理逻辑，可以使用图像处理库或自定义算法
    # 处理后的结果生成新的图片数据
    processed_image_data = image_data  # 这里只是示例，将原始图片数据作为处理结果

    return processed_image_data

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('IP', PORT))
# 使socket处于监听状态，等待客户端的连接请求
# 参数 1 表示 最多接受多少个等待连接的客户端
server_socket.listen(1)

print(f'服务端启动成功，在{PORT}端口等待客户端连接...')

client_socket, client_address = server_socket.accept()
print('客户端已连接:', client_address)

# 接收文件名
file_name = client_socket.recv(BUFLEN).decode()
print('收到文件名:', file_name)

# 接收图片数据
#image_data = b'' 是一个字节串（byte string）,b代表字节串
image_data = b''
while True:
    data = client_socket.recv(BUFLEN)
    if not data:
        break
    image_data += data

print('接收完毕，开始处理图片...')

# 处理图片
processed_image_data = process_image(image_data)

print('图片处理完成，发送结果回客户端...')

# 发送处理后的图片数据
# 发送的数据类型必须是bytes，所以要编码
client_socket.sendall(processed_image_data)

print('结果发送完成，关闭连接。')

# 服务端也调用close()关闭socket
client_socket.close()
server_socket.close()