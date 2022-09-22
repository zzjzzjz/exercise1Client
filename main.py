import socket
import handler

IP = "127.0.0.1"
PORT1 = 9090  # 对应三种服务的端口
PORT2 = 9091
PORT3 = 9092
if __name__ == "__main__":
    print('1----查看文件列表\n2----tcp下载文件\n3----udp下载文件\n4----退出')
    selected = input()
    while True:
        if selected == '1':
            handler.getFiles(IP, PORT1)
        elif selected == '2':
            handler.getFileByTCP(IP, PORT2)
        elif selected == '3':
            handler.getFileByUDP(IP, PORT3)
        elif selected == '4':
            exit(0)
        else:
            print('输入错误')
        print('-------------------------------')
        print('1----查看文件列表\n2----tcp下载文件\n3----udp下载文件\n4----退出')
        selected = input()
