from dataclasses import dataclass

@dataclass
class Position:
    x_: float
    y_: float
    z_: float

@dataclass
class Rotation:
    yaw_: float
    pitch_: float

@dataclass
class PlayerInformation:
    playerId_ : int
    position_ : Position
    rotation_ : Rotation


class PlayerInformationCollector:
    playerList_ : list[PlayerInformation] = []

    def __init__(self):
        self.playerList_ = []

    def AddPlayer(self, playerId: int, x: float, y: float, z: float, yaw: float, pitch: float):
        pos = Position(x, y, z)
        rot = Rotation(yaw, pitch)
        playerInfo = PlayerInformation(playerId, pos, rot)
        self.playerList_.append(playerInfo)

    def GetPlayerPosition(self, playerId: int) -> Position | None:
        for player in self.playerList_:
            if player.playerId_ == playerId:
                return player.position_
            
        return None
    
    def ClearPlayers(self):
        self.playerList_.clear()