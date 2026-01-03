
import socket
import struct

from common import *

class NetworkManager:
    RECV_DATA_BYTES = 1024
    BOOL = 1

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

    def __MakePositionInformation(self, type : POSITION_TYPE, x: float, y: float, z: float) -> PositionInformation:
        pi = PositionInformation(type, x, y, z)
        return pi
    
    def __MakeRotationInformation(self, type : ROTATION_TYPE, yaw: float, pitch: float) -> RotationInformation:
        ri = RotationInformation(type, Rotation(yaw, pitch))
        return ri
    
    def __MakeCommandHeader(self, operationType : OPERATION_TYPE, targetPi : PositionInformation, targetRi : RotationInformation) -> CommandHeader:
        ch = CommandHeader(operationType, targetPi, targetRi)
        return ch
        
    def AcceptConnection(self):
        self.addr_ = self.agentTcpSocket_.accept()

    def SendTargetRotation(self, type : ROTATION_TYPE, yaw: float, pitch: float) -> bool:
        targetRotationInformation = self.__MakeRotationInformation(type, yaw, pitch)

        try:
            self.addr_[0].sendall(targetRotationInformation.ToBytes())
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            print("Connection closed by client")
            return False

        return True 

    def SendTargetPosition(self, type : "NetworkManager.POSITION_TYPE", x: float, y: float, z: float) -> bool:
        targetPositionInformation = self.__MakePositionInformation(type, x, y, z)

        try:
            self.addr_[0].sendall(targetPositionInformation.ToBytes())
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            print("Connection closed by client")
            return False

        return True

    def SendCommand(self, operationType : OPERATION_TYPE, **kwargs) -> bool:
        x = kwargs.get('x', 0.0)
        y = kwargs.get('y', 0.0)
        z = kwargs.get('z', 0.0)
        yaw = kwargs.get('yaw', 0.0)
        pitch = kwargs.get('pitch', 0.0)

        targetPi = self.__MakePositionInformation(POSITION_TYPE.ABSOLUTE, x, y, z)
        targetRi = self.__MakeRotationInformation(ROTATION_TYPE.NONE, yaw, pitch)
        commandHeader = self.__MakeCommandHeader(operationType, targetPi, targetRi)

        try:
            self.addr_[0].sendall(commandHeader.ToBytes())
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            print("Connection closed by client")
            return False

        return True

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
    TCP_PORT = 8888

    nm = NetworkManager('localhost')
    nm.UdpServerOpen(UDP_PORT)

    while True:
        pi = nm.GetPlayerInformation()
        print(f'Player ID: {pi.playerId_}, Position: ({pi.position_.x_}, {pi.position_.y_}, {pi.position_.z_}), Rotation: (Yaw: {pi.rotation_.yaw_}, Pitch: {pi.rotation_.pitch_})')

def main():
    UDP_PORT = 8986
    TCP_PORT = 8888

    nm = NetworkManager('localhost')
    nm.UdpServerOpen(UDP_PORT)
    nm.TcpServerOpen('localhost', TCP_PORT)

    nm.AcceptConnection()

    import time

    while True:
        input("Target Position Send...")
        time.sleep(5)
        
        if not nm.SendCommand(OPERATION_TYPE.POSITION, x=10.0, y=-60.0, z=10.0, yaw=0.0, pitch=0.0):
            print("Retry AcceptConnection...")
            nm.AcceptConnection()


if __name__ == "__main__":
    main()