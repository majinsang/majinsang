import socket
import struct

from PlayerInformationCollector import PlayerInformation
from PlayerInformationCollector import Position
import threading

class NetworkManager:
    RECV_DATA_BYTES = 1024
    BOOL = 1

    def __init__(self, host):
        self.host_ = host
        self.udpSocket_ = None
        self.agentTcpSocket_ = None
        self.pluginTcpSocket_ = None
        self.addr_ = None

    def __ParsePlayerData(self, data: bytes) -> tuple[str, tuple[float, float, float]]:
        nameLength = struct.unpack('i', data[:4])
        name = data[4:4+int(nameLength[0])].decode('utf-8')
        x, y, z = struct.unpack('ddd', data[4+int(nameLength[0]):4+int(nameLength[0])+24])
        return name, (x, y, z)
    
    def UdpServerOpen(self, port):
        self.udpSocket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udpSocket_.bind((self.host_, port))

    def TcpServerOpen(self, host, port):
        self.agentTcpSocket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.agentTcpSocket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.agentTcpSocket_.bind((host, port))
        self.agentTcpSocket_.listen(1)

    def __SendTargetPosition(self, x: float, y: float, z: float):
        data = struct.pack('!ddd', x, y, z)
        self.addr_[0].sendall(data)
        
        res : bool = self.addr_[0].recv(self.BOOL)

        return res

        
    def AcceptConnection(self):
        self.addr_ = self.agentTcpSocket_.accept()

    def SendTargetPosition(self, x: float, y: float, z: float):
        self.__SendTargetPosition(x,y,z)

    def GetPlayerPosition(self) -> PlayerInformation:
        self.udpSocket_.setblocking(False)

        try:
            while True:
                data, clientAddr = self.udpSocket_.recvfrom(self.RECV_DATA_BYTES)
        except BlockingIOError:
            pass
        finally:
            self.udpSocket_.setblocking(True)

        data, clientAddr = self.udpSocket_.recvfrom(self.RECV_DATA_BYTES)
        
        name, (x, y, z) = self.__ParsePlayerData(data)
        pi = PlayerInformation(name, Position(x, y, z))

        return pi


    def Close(self):
        self.socket_.close()

if __name__ == "__main__":
    nm = NetworkManager('localhost')
    nm.UdpServerOpen(8986)
    nm.TcpServerOpen('localhost', 18986)
    nm.AcceptConnection()

    import time

    while 1:
        playerInformation = nm.GetPlayerPosition()

        print(f'Player Name: {playerInformation.name_}, Position: ({playerInformation.position_.x_}, {playerInformation.position_.y_}, {playerInformation.position_.z_})')

        input("Press Enter to send target position...")
        x = float(input("Enter x: "))
        y = float(input("Enter y: "))
        z = float(input("Enter z: "))

        time.sleep(1)

        nm.SendTargetPosition(x, y, z)

