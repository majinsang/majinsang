import enum
from dataclasses import dataclass
import socket
import struct

from PlayerInformationCollector import PlayerInformation, Rotation
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

    def __ParsePlayerData(self, data: bytes) -> tuple[str, tuple[float, float, float], tuple[float, float]]:
        uuid = data[:8].hex()
        x, y, z = struct.unpack('ddd', data[8:32])
        yaw, pitch = struct.unpack('dd', data[32:48])
        return uuid, (x, y, z), (yaw, pitch)
    
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

    def GetPlayerInformation(self) -> PlayerInformation:
        self.udpSocket_.setblocking(False)

        try:
            while True:
                data, clientAddr = self.udpSocket_.recvfrom(self.RECV_DATA_BYTES)
        except BlockingIOError:
            pass
        finally:
            self.udpSocket_.setblocking(True)

        data, clientAddr = self.udpSocket_.recvfrom(self.RECV_DATA_BYTES)
        
        playerId, (x, y, z), (yaw, pitch) = self.__ParsePlayerData(data)
        pi = PlayerInformation(playerId, Position(x, y, z), Rotation(yaw, pitch))

        return pi


    def Close(self):
        self.socket_.close()

def udp_test():
    UDP_PORT = 8986

    nm = NetworkManager('localhost')
    nm.UdpServerOpen(UDP_PORT)

    import time

    while 1:
        playerInformation = nm.GetPlayerInformation()

        print(f'Player ID: {playerInformation.playerId_} '
              f'Position: ({playerInformation.position_.x_}, {playerInformation.position_.y_}, {playerInformation.position_.z_}) '
              f'Rotation: (Yaw: {playerInformation.rotation_.yaw_}, Pitch: {playerInformation.rotation_.pitch_})')
        time.sleep(0.1)


if __name__ == "__main__":
    udp_test()