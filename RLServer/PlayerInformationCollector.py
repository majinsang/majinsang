from dataclasses import dataclass

@dataclass
class Position:
    x_: float
    y_: float
    z_: float

@dataclass
class PlayerInformation:
    name_ : str
    position_ : Position


class PlayerInformationCollector:
    playerList_ : list[PlayerInformation] = []

    def __init__(self):
        self.playerList_ = []

    def AddPlayer(self, name: str, x: float, y: float, z: float):
        pos = Position(x, y, z)
        playerInfo = PlayerInformation(name, pos)
        self.playerList_.append(playerInfo)

    def GetPlayerPosition(self, name: str) -> Position | None:
        for player in self.playerList_:
            if player.name_ == name:
                return player.position_
            
        return None
    
    def ClearPlayers(self):
        self.playerList_.clear()