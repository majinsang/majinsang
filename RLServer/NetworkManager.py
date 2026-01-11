
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

    def __ParsePlayerData(self, data: bytes) -> tuple[bytes, tuple[float, float, float], tuple[float, float]]:
        uuid = data[1:5]
        x, y, z = struct.unpack('<ddd', data[5:29])
        yaw, pitch = struct.unpack('<dd', data[29:45])
        return uuid, (x, y, z), (yaw, pitch)
    
    def __ParsePlayerInventory(self, data: bytes) -> tuple[int, int, int, int, int, int]:
        """PACKET_ID(1) + PlayerID(4) + inventory(20) = 25 bytes"""
        player_id, log, planks, stick, pickaxe, table = struct.unpack('<IIIIII', data[1:25])
        return player_id, log, planks, stick, pickaxe, table
    
    def __ParsePlayerNearby(self, data: bytes) -> tuple[int, bool, tuple[float, float, float], bool, tuple[float, float, float]]:
        """PACKET_ID(1) + PlayerID(4) + nearby(50) = 55 bytes"""
        player_id = struct.unpack('<I', data[1:5])[0]
        near_tree = bool(data[5])
        tree_x, tree_y, tree_z = struct.unpack('<ddd', data[6:30])
        near_table = bool(data[30])
        table_x, table_y, table_z = struct.unpack('<ddd', data[31:55])
        
        return player_id, near_tree, (tree_x, tree_y, tree_z), near_table, (table_x, table_y, table_z)
    
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
        targetRi = self.__MakeRotationInformation(ROTATION_TYPE.YAW, yaw, pitch)
        commandHeader = self.__MakeCommandHeader(operationType, targetPi, targetRi)

        try:
            self.addr_[0].sendall(commandHeader.ToBytes())
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            print("Connection closed by client")
            return False

        return True

    def GetPackets(self) -> tuple[PlayerInformation, PlayerInventory, PlayerNearby]:
        self.udpSocket_.setblocking(False)
        
        latest_player = None
        latest_inventory = None
        latest_nearby = None
        
        try:
            while True:
                data, _ = self.udpSocket_.recvfrom(self.RECV_DATA_BYTES)
                packet_id = data[0]
                
                if packet_id == PACKET_ID.PLAYER_INFORMATION:
                    latest_player = data
                elif packet_id == PACKET_ID.INVENTORY_INFORMATION:
                    latest_inventory = data
                elif packet_id == PACKET_ID.NEAR_BY_INFORMATION:
                    latest_nearby = data
        except BlockingIOError:
            pass
        finally:
            self.udpSocket_.setblocking(True)
        
        # 파싱
        player_info = None
        if latest_player:
            playerId, (x, y, z), (yaw, pitch) = self.__ParsePlayerData(latest_player)
            player_info = PlayerInformation(playerId, Position(x, y, z), Rotation(yaw, pitch))
        
        inventory_info = None
        if latest_inventory:
            player_id, log, planks, stick, pickaxe, table = self.__ParsePlayerInventory(latest_inventory)
            inventory_info = PlayerInventory(player_id, log, planks, stick, pickaxe, table)
        
        nearby_info = None
        if latest_nearby:
            player_id, near_tree, tree_pos, near_table, table_pos = self.__ParsePlayerNearby(latest_nearby)
            nearby_info = PlayerNearby(player_id, near_tree, Position(*tree_pos), near_table, Position(*table_pos))
        
        return player_info, inventory_info, nearby_info

    def GetPlayerInformation(self) -> PlayerInformation:
        """PACKET_ID = 0x01: 플레이어 위치 수신"""
        self.udpSocket_.setblocking(False)

        latest_data = None
        try:
            while True:
                data, clientAddr = self.udpSocket_.recvfrom(self.RECV_DATA_BYTES)
                if data[0] == PACKET_ID.PLAYER_INFORMATION:
                    latest_data = data
        except BlockingIOError:
            pass
        finally:
            self.udpSocket_.setblocking(True)

        if latest_data is None:
            data, clientAddr = self.udpSocket_.recvfrom(self.RECV_DATA_BYTES)
        else:
            data = latest_data
        
        playerId, (x, y, z), (yaw, pitch) = self.__ParsePlayerData(data)
        pi = PlayerInformation(playerId, Position(x, y, z), Rotation(yaw, pitch))

        return pi

    # def GetPlayerInventory(self) -> PlayerInventory:
    #     """PACKET_ID = 0x02: 인벤토리 정보 수신"""
    #     self.udpSocket_.setblocking(False)

    #     latest_data = None
    #     try:
    #         while True:
    #             data, clientAddr = self.udpSocket_.recvfrom(self.RECV_DATA_BYTES)
    #             if data[0] == PACKET_ID.INVENTORY_INFORMATION:
    #                 latest_data = data
    #     except BlockingIOError:
    #         pass
    #     finally:
    #         self.udpSocket_.setblocking(True)

    #     if latest_data is None:
    #         return None
        
    #     player_id, log, planks, stick, pickaxe, table = self.__ParsePlayerInventory(latest_data)
    #     return PlayerInventory(player_id, log, planks, stick, pickaxe, table)

    # def GetPlayerNearby(self) -> PlayerNearby:
    #     """PACKET_ID = 0x03: 주변 정보 수신"""
    #     self.udpSocket_.setblocking(False)

    #     latest_data = None
    #     try:
    #         while True:
    #             data, clientAddr = self.udpSocket_.recvfrom(self.RECV_DATA_BYTES)
    #             if data[0] == PACKET_ID.NEAR_BY_INFORMATION:
    #                 latest_data = data
    #     except BlockingIOError:
    #         pass
    #     finally:
    #         self.udpSocket_.setblocking(True)

    #     if latest_data is None:
    #         return None
        
    #     player_id, near_tree, tree_pos, near_table, table_pos = self.__ParsePlayerNearby(latest_data)
    #     return PlayerNearby(
    #         player_id, 
    #         near_tree, 
    #         Position(*tree_pos), 
    #         near_table, 
    #         Position(*table_pos)
    #     )

    def Close(self):
        if self.udpSocket_:
            self.udpSocket_.close()
        if self.agentTcpSocket_:
            self.agentTcpSocket_.close()

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
        
        if not nm.SendCommand(OPERATION_TYPE.ROTATION, x=10.0, y=-60.0, z=10.0, yaw=-60.0, pitch=0.0):
            print("Retry AcceptConnection...")
            nm.AcceptConnection()


if __name__ == "__main__":
    main()