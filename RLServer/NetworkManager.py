import enum
from dataclasses import dataclass
import socket
import struct

from PlayerInformationCollector import PlayerInformation
from PlayerInformationCollector import Position

class NetworkManager:
    RECV_DATA_BYTES = 1024
    BOOL = 1

    class POSITION_TYPE(enum.Enum):
        NONE = 0,
        RELATIVE = 1,
        ABSOLUTE = 2

    @dataclass
    class POSITION_INFORMATION:
        type_ : "NetworkManager.POSITION_TYPE"
        x_: float
        y_: float
        z_: float

        def ToBytes(self):
            return struct.pack(
                '<b d d d',
                self.type_.value,
                self.x_,
                self.y_,
                self.z_
            )


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

    def __MakePositionInformation(self, type : "NetworkManager.POSITION_TYPE", x: float, y: float, z: float) -> POSITION_INFORMATION:
        pi = NetworkManager.POSITION_INFORMATION(type, x, y, z)
        return pi
        
    def AcceptConnection(self):
        self.addr_ = self.agentTcpSocket_.accept()

    def SendTargetPosition(self, type : "NetworkManager.POSITION_TYPE", x: float, y: float, z: float):
        targetPositionInformation = self.__MakePositionInformation(type, x, y, z)

        self.addr_[0].sendall(targetPositionInformation.ToBytes())
        res : bool = self.addr_[0].recv(self.BOOL)
        print(f'SendTargetPosition Ack: {bool(struct.unpack("b", res)[0])}')

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
    nm.TcpServerOpen('localhost', 8888)
    nm.AcceptConnection()

    import time

    while 1:
        playerInformation = nm.GetPlayerPosition()

        print(f'Player Name: {playerInformation.name_}, Position: ({playerInformation.position_.x_}, {playerInformation.position_.y_}, {playerInformation.position_.z_})')

        input("Press Enter to send target position...")
        x = float(input("Enter x: "))
        y = float(input("Enter y: "))
        z = float(input("Enter z: "))

        time.sleep(3)

        nm.SendTargetPosition(NetworkManager.POSITION_TYPE.ABSOLUTE, x, y, z)

