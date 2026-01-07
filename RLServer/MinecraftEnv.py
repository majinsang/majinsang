import gymnasium as gym
from gymnasium import spaces
import numpy as np

from common import *
from NetworkManager import NetworkManager

class MinecraftEnv(gym.Env):
    networkManager_ : NetworkManager = None
    currentPlayerInformation_ : PlayerInformation = None
    targetPlayerInformation_ : PlayerInformation = None
    

    def __init__(self, targetPosition):
        super().__init__()
        self.currentPlayerInformation_ = PlayerInformation(
            playerId_ = 0,
            position_ = Position(0.0, 0.0, 0.0),
            rotation_ = Rotation(0.0, 0.0)
        )

        self.targetPlayerInformation_ = PlayerInformation(
            playerId_ = 0,
            position_ = Position(*targetPosition),
            rotation_ = Rotation(0.0, 0.0)
        )

        self.observation_space = spaces.Box(
            low = np.array([-1000, -10000, -1000, -180, -90, -180, -90], dtype=np.float32),
            high= np.array([1000, 1000, 1000, 180, 90, 180, 90], dtype=np.float32),
            dtype=np.float32
        )

        self.action_space = spaces.Discrete(8)

        self.prevDist_ = None

        self.networkManager_ = NetworkManager('localhost')
        self.networkManager_.UdpServerOpen(8986)
        self.networkManager_.TcpServerOpen('localhost', 8888)
        self.networkManager_.AcceptConnection()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.__SetPlayerPosition(0, -60, 0)
        self.__SetPlayerRotation(0, 0)

        self.__SendCommand(
            *self.__GetPlayerPosition().ToArray(),
            *self.__GetPlayerRotation().ToArray()
        )

        self.__UpdatePlayerInformation()

        self.prevDist_ = np.linalg.norm(self.__GetPlayerPosition().ToArray() - self.__GetTargetPosition().ToArray())

        
        obs = self.__GetObservation()
        return obs, {}
    
    def step(self, action):
        self.SendAction(action)

        self.__UpdatePlayerInformation()

        currentPos = self.__GetPlayerPosition().ToArray()
        targetPos = self.__GetTargetPosition().ToArray()

        dist = np.linalg.norm(currentPos - targetPos)

        reward = self.prevDist_ - dist
        self.prevDist_ = dist

        terminated = dist < 1.0
        if terminated:
            reward += 100

        obs = self.__GetObservation()

        return obs, reward, terminated, False, {}

    def SendAction(self, action):
        step = 1.0
        yawStep = 15.0
        pitchStep = 15.0

        pos = self.__GetPlayerPosition()
        rot = self.__GetPlayerRotation()

        x, y, z = pos.x_, pos.y_, pos.z_
        yaw, pitch = rot.yaw_, rot.pitch_

        if action == 0:   # Move Forward
            z += step
        elif action == 1: # Move Backward
            z -= step
        elif action == 2: # Move Left
            x -= step
        elif action == 3: # Move Right
            x += step
        elif action == 4: # Yaw Left
            yaw -= yawStep
        elif action == 5: # Yaw Right
            yaw += yawStep
        elif action == 6: # Pitch Up
            pitch = np.clip(pitch + pitchStep, -90, 90)
        elif action == 7: # Pitch Down
            pitch = np.clip(pitch - pitchStep, -90, 90)

        yaw = ((yaw + 180) % 360) - 180

        self.__SendCommand(x, y, z, yaw, pitch)

    def __CalcRotationToTarget(self):
        direction = self.__GetTargetPosition().ToArray() - self.__GetPlayerPosition().ToArray()
        distanceXZ = np.sqrt(direction[0] ** 2 + direction[2] ** 2)

        yaw = np.degrees(np.arctan2(-direction[0], direction[2]))
        pitch = np.degrees(np.arctan2(-direction[1], distanceXZ))

        return yaw, pitch
    
    def __GetObservation(self):
        relativePos = self.__GetTargetPosition().ToArray() - self.__GetPlayerPosition().ToArray()
        rot = self.__GetPlayerRotation()
        targetYaw, targetPitch = self.__CalcRotationToTarget()
        
        return np.concatenate([relativePos, [rot.yaw_, rot.pitch_], [targetYaw, targetPitch]]).astype(np.float32)

    def __UpdatePlayerInformation(self):
        self.currentPlayerInformation_ = self.networkManager_.GetPlayerInformation()

    def __GetPlayerPosition(self):
        return self.currentPlayerInformation_.position_
    
    def __GetPlayerRotation(self):
        return self.currentPlayerInformation_.rotation_
    
    def __GetTargetPosition(self):
        return self.targetPlayerInformation_.position_
    
    def __GetTargetRotation(self):
        return self.targetPlayerInformation_.rotation_
    
    def __SetPlayerPosition(self, x, y, z):
        self.currentPlayerInformation_.position_ = np.array([x, y, z], dtype=np.float32)

    def __SetPlayerRotation(self, yaw, pitch):
        self.currentPlayerInformation_.rotation_ = np.array([yaw, pitch], dtype=np.float32)

    def __SetTargetPosition(self, x, y, z):
        self.targetPlayerInformation_.position_ = np.array([x, y, z], dtype=np.float32)

    def __SetTargetRotation(self, yaw, pitch):
        self.targetPlayerInformation_.rotation_ = np.array([yaw, pitch], dtype=np.float32)

    def __SendCommand(self, x, y, z, yaw, pitch):
        self.networkManager_.SendCommand(OPERATION_TYPE.ALL, x, y, z, yaw, pitch)