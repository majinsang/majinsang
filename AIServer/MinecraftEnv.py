import gymnasium as gym
from gymnasium import spaces
import numpy as np

from NetworkManager import NetworkManager

class MinecraftEnv(gym.Env):
    networkManager_ : NetworkManager = None

    def __init__(self):
        super().__init__()

        self.observation_space = spaces.Box(low=-1000, high=1000, shape=(3,), dtype=np.float32)
        self.action_space = spaces.Discrete(4)
        self.prevDist_ = None

        self.networkManager_ = NetworkManager('localhost')
        self.networkManager_.UdpServerOpen(8986)
        self.networkManager_.TcpServerOpen('localhost', 18986)
        self.networkManager_.AcceptConnection()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.networkManager_.SendTargetPosition(0.0, -60.0, 0.0)

        self.agentPos_ = self.GetPlayerPosition()
        self.targetPos_ = self.GetTargetPosition()

        self.prevDist_ = np.linalg.norm(self.agentPos_ - self.targetPos_)

        # obs = np.concatenate([self.agentPos_, self.targetPos_])
        obs = self.targetPos_ - self.agentPos_
        return obs, {}
    
    def step(self, action):
        self.SendAction(action)

        # time.sleep(0.05)

        self.agentPos_ = self.GetPlayerPosition()

        dist = np.linalg.norm(self.agentPos_ - self.targetPos_)

        reward = self.prevDist_ - dist
        self.prevDist_ = dist

        terminated = dist < 1.0
        if terminated:
            reward += 100

        # obs = np.concatenate([self.agentPos_, self.targetPos_])
        obs = self.targetPos_ - self.agentPos_

        return obs, reward, terminated, False, {}
    
    def GetPlayerPosition(self):
        playerPosition = self.networkManager_.GetPlayerPosition()

        return np.array([playerPosition.position_.x_, playerPosition.position_.y_, playerPosition.position_.z_], dtype=np.float32)
    
    def GetTargetPosition(self):
        return np.array([10.0, -60.0, 10.0], dtype=np.float32)
    
    def SendAction(self, action):
        step = 1.0
        x, y, z = self.agentPos_

        if action == 0:   # Move forward
            z += step
        elif action == 1: # Move backward
            z -= step
        elif action == 2: # Move left
            x -= step
        elif action == 3: # Move right
            x += step

        self.networkManager_.SendTargetPosition(x, y, z)

