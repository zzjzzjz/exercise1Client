import hashlib
import os
import socket
import time
from math import ceil

import select
import re
import sys

UDP_RECV_DATA_SIZE = 1024 * 10000  # udp一次接受数据的大小


def getFiles(ip, port):
    CONNECT_TUPLE = (ip, port)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(CONNECT_TUPLE)
    print("---------------可下载文件列表---------------")
    try:
        while True:
            ready = client.recv(1024).decode('utf8')
            length = int(ready)
            client.send(ready.encode('utf8'))
            files = client.recv(length)
            files = files.decode('utf8')  # 文件列表
            print(files)
            if not files:
                break
    except ValueError:
        pass

    print("------------------------------------------")


def getFileByTCP(ip, port):
    fileName = input("下载文件名：")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    client.send(fileName.encode('utf-8'))
    data = b''
    data, addr = client.recvfrom(35) # 在这一行打断点会出问题，不够稳定，打断点暂停的时间缓存已经有更多的数据，此时data会掺杂其他的东西
    # bug 形如 ---> print(data) b'{\'ok\': True, \'fileSize\': 155921579}\x00\x00\x00\x14ftypiso\n'
    print(data)# b"{'ok': True, 'fileSize': 155921579}"
    data = eval(data.decode('utf-8'))

    if not data['ok']:
        print('请求文件可能不存在')
        client.close()
        return
    i = 1
    fileName = re.split('[/\\\]', fileName)[-1]
    filepath = "folder\\" + fileName
    file = open(filepath, "wb")  # 下载文件保存在floder目录下
    fileSize = data['fileSize']
    timebefore = time.time()
    while True:
        data = client.recv(1024 * 10)
        i = i + 1
        per = int((os.stat("folder\\" + fileName).st_size / fileSize) * 100)
        # print("进度: {}%: ".format(per),"▋" * (per // 2) , end="")
        # sys.stdout.flush()
        # time.sleep(0.05)

        if not data:
            break
        file.write(data)

    file.close()
    print("\r", end="")
    print("进度: {}%:\n ".format(int((os.stat("folder\\" + fileName).st_size / fileSize) * 100)), "", end="")
    timeafter = time.time()
    print('大小' + str(os.path.getsize(filepath)/pow(2,20))+ 'MB' + '总用时：' + str(timeafter - timebefore) + ' s')
    client.close()


def getFileByUDP(ip, port):
    id = 0  # 请求文件数据偏移量
    fileName = input("下载文件名：")
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(('127.0.0.1', 5678))
    filepath = "folder\\" + re.split('[/\\\]', fileName)[-1]
    id = 0
    file = open(filepath, "wb")  # 下载文件保存在floder目录下
    i = 0  # 失败次数，超过5次判定网络有问题
    timebefore = time.time()
    while True:

        if i > 5:
            print('请检测网络')
            file.close()
            return

        sendData = {'fileName': fileName, 'id': id}
        client.sendto(str(sendData).encode('utf-8'), (ip, port))
        try:

            data, addr = client.recvfrom(UDP_RECV_DATA_SIZE)
            data = eval(data.decode('utf-8'))
        except:
            i = i + 1
            continue
        if not __testMd5OfDict(data):
            i = i + 1
            continue
        if data['ok'] == False:  # 响应信息表示错误则退出该函数
            print('\n文件不存在或服务器出问题')
            file.close()
            return
        if data['id'] == id:  # 响应数据的是想要的数据
            file.write(data['fileData'])
            id = id + 1

        # print("\r", end="")
        # print("进度: {}%: ".format(data['per']),"" , end="")
        if data['end']:
            break
        i = 0

    print("\r", end="")
    print("进度: {}%: \n".format(data['per']), "", end="")
    timeafter = time.time()
    print('大小' + str(os.path.getsize(filepath) / pow(2,20)) + 'MB' + '总用时：' + str(timeafter - timebefore) + ' s')
    file.close()


def __testMd5OfDict(ob: dict):  # 测试字典的md5值
    try:

        md5 = ob['md5']
    except:
        return False
    del ob['md5']
    recMd5 = hashlib.md5(str(ob).encode('utf-8')).hexdigest()
    if md5 == recMd5:
        return True
    else:
        return False
