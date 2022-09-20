import hashlib
import os
import socket
import time
import select
import re
import sys
UDP_RECV_DATA_SIZE = 1024 * 100  # udp一次接受数据的大小


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
    data, addr = client.recvfrom(1024)
    print(data)
    data = eval(data.decode('utf-8'))

    if not data['ok']:
        print('请求文件可能不存在')
        client.close()
        return
    i = 1
    fileName=re.split('[/\\\]',fileName)[-1]
    file = open("folder\\"+fileName, "wb")#下载文件保存在floder目录下
    fileSize=data['fileSize']
    while True:
        data = client.recv(1024*10)
        i = i + 1
        per = int((os.stat("folder\\" + fileName).st_size / fileSize) * 100)
        print("进度: {}%: ".format(per),"" , end="")
        sys.stdout.flush()


        if not data:
            break
        file.write(data)

    file.close()
    print("\r", end="")
    print("进度: {}%:\n ".format(int((os.stat("folder\\" + fileName).st_size / fileSize) * 100)), "", end="")

    client.close()


def getFileByUDP(ip, port):
    id = 0  # 请求文件数据偏移量
    fileName = input("下载文件名：")
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(('127.0.0.1', 5678))




    id=0
    file = open("folder\\" + re.split('[/\\\]', fileName)[-1], "wb")  # 下载文件保存在floder目录下
    i=0#失败次数，超过5次判定网络有问题
    while True:

        if i>5:
            print('请检测网络')
            file.close()
            return

        sendData = {'fileName': fileName, 'id': id}
        client.sendto(str(sendData).encode('utf-8'), (ip, port))
        try:

            data, addr = client.recvfrom(UDP_RECV_DATA_SIZE)
            data = eval(data.decode('utf-8'))
        except:
            i=i+1
            continue
        if not __testMd5OfDict(data):
            i=i+1
            continue
        if data['ok']==False:  # 响应信息表示错误则退出该函数
            print('\n文件不存在或服务器出问题')
            file.close()
            return
        if data['id'] == id:  # 响应数据的是想要的数据
            file.write(data['fileData'])
            id = id + 1

        print("\r", end="")
        print("进度: {}%: ".format(data['per']),"" , end="")
        if data['end']:
            break
        i=0




    print("\r", end="")
    print("进度: {}%: \n".format(data['per']), "", end="")
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

    """
    while True:
        if data['end']:
            file.close()
            break
        id=data['id']
        print(id)
        file.seek(id*1024)
        file.write(data['data'])
        data={'type':2,'id':id+1}#下一个请求序号
        client.sendto(str(data).encode('utf-8'),addr)

        data, addr = client.recvfrom(1024*10)
        print(data)
        data = eval(data.decode('utf-8'))
        while data['id']!=id+1:
            client.sendto(str(data).encode('utf-8'),addr)
            data, addr = client.recvfrom(1024 * 10)
            data = eval(data.decode('utf-8'))


    print('结束')
    """


