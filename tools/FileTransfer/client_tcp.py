import socket
import struct
import pickle
import os

# server_ip = '0.0.0.0'
# server_port = 5400

def get(client,filepath):
    obj = client.recv(4)
    header_size = struct.unpack('i', obj)[0]
    if header_size == 0:
        raise Exception('File not found')
    else:
        header_types = client.recv(header_size)
        header = pickle.loads(header_types)
        print(header)
        file_size = header['file_size']
        file_name = header['file_name']
        with open('%s/%s' % (filepath, file_name), 'wb') as f:
            recv_size = 0
            while recv_size < file_size:
                res = client.recv(1024)
                f.write(res)
                recv_size += len(res)
                # print('一共有这么大：%s B 你已经下载了：%s B' % (file_size, recv_size))
            # print('下完啦 (0 V 0)')

def run(client,file_path):
    get(client,file_path)

def test():
    path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(path)

if __name__ == '__main__':
    test()
