from dataclasses import dataclass
import struct
import enum
import numpy as np

class PACKET_ID(enum.IntEnum):
    PLAYER_INFORMATION = 0x01
    INVENTORY_INFORMATION = 0x02
    NEAR_BY_INFORMATION = 0x03

class POSITION_TYPE(enum.IntEnum):
        NONE = 0
        RELATIVE = 1
        ABSOLUTE = 2

@dataclass
class Position:
    x_: float
    y_: float
    z_: float

    def ToArray(self):
        return np.array([self.x_, self.y_, self.z_], dtype=np.float32)

@dataclass
class PlayerInventory:
    playerId_: int
    log_: int
    planks_: int
    stick_: int
    pickaxe_: int
    crafting_table_: int

@dataclass
class PlayerNearby:
    playerId_: int
    near_tree_: bool
    tree_pos_: Position
    near_table_: bool
    table_pos_: Position

@dataclass
class PositionInformation:
    type_ : POSITION_TYPE
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
    
class ROTATION_TYPE(enum.IntEnum):
    NONE = 0
    YAW = 1
    PITCH = 2

@dataclass
class Rotation:
    yaw_: float
    pitch_: float

    def ToArray(self):
        return np.array([self.yaw_, self.pitch_], dtype=np.float32)

@dataclass
class RotationInformation:
    type_ : ROTATION_TYPE
    rotation_ : Rotation

@dataclass
class PlayerInformation:
    playerId_ : int
    position_ : Position
    rotation_ : Rotation

class OPERATION_TYPE(enum.IntEnum):
    NONE = 0
    POSITION = 1
    ROTATION = 2
    ALL = 3

@dataclass
class CommandHeader:
    opCode_ : OPERATION_TYPE
    targetPi_ : PositionInformation
    targetRi_ : RotationInformation

    def ToBytes(self) -> bytes:
        return struct.pack(
            '<B B d d d B d d', 
            int(self.opCode_),
            int(self.targetPi_.type_),
            float(self.targetPi_.x_),
            float(self.targetPi_.y_),
            float(self.targetPi_.z_),
            int(self.targetRi_.type_),
            float(self.targetRi_.rotation_.yaw_),
            float(self.targetRi_.rotation_.pitch_),
        )