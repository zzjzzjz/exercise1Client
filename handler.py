import  socket
import time
UDP_RECV_DATA_SIZE=1024*100#udp一次接受数据的大小
def getFiles(ip,port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    files = client.recv(4096)#文件列表(byte)
    files=files.decode('utf-8')#转为字符串
    files=eval(files)#转为列表
    print("---------------可下载文件列表---------------")
    for i in files:
        print(i)
    print("------------------------------------------")

def getFileByTCP(ip,port):
    fileName=input("下载文件名：")
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((ip,port))
    client.send(fileName.encode('utf-8'))
    file=open(fileName,"wb")
    i=1
    while True:

        data = client.recv(1024)
        print(i)
        i=i+1
        if not data:
            break
        file.write(data)


    file.close()
    client.close()

def getFileByUDP(ip,port):
    id=0#请求文件数据偏移量
    fileName = input("下载文件名：")
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(('127.0.0.1',5678))
    sendData = {'fileName': fileName, 'id': id}#构造请求数据，包括文件名，
    client.sendto(str(sendData).encode('utf-8'),(ip,port))
    data,addr=client.recvfrom(UDP_RECV_DATA_SIZE)
    print(data)
    data=eval(data.decode('utf-8'))
    if not data['ok']:#响应信息表示错误则退出该函数
        print('文件请求错误或服务器出问题')
        return
    file = open(fileName, "wb")
    while not data['end']:
        print(id)
        if data['id']==id:#响应数据的是想要的数据
            file.write(data['fileData'])
            id=id+1
        sendData = {'fileName': fileName, 'id': id}
        client.sendto(str(sendData).encode('utf-8'), (ip, port))
        data, addr = client.recvfrom(UDP_RECV_DATA_SIZE)
        data=eval(data.decode('utf-8'))
    file.close()






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




