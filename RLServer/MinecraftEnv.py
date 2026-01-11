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

        # Observation: [relative_x, relative_y, relative_z, current_yaw, current_pitch, target_yaw, target_pitch]
        self.observation_space = spaces.Box(
            low = np.array([-1000, -10000, -1000, -180, -90, -180, -90], dtype=np.float32),
            high= np.array([1000, 1000, 1000, 180, 90, 180, 90], dtype=np.float32),
            dtype=np.float32
        )

        # Continuous action space: [dx, dy, dz, dyaw, dpitch]
        # This allows simultaneous movement and rotation
        self.action_space = spaces.Box(
            low=np.array([-2.0, -2.0, -2.0, -30.0, -30.0], dtype=np.float32),
            high=np.array([2.0, 2.0, 2.0, 30.0, 30.0], dtype=np.float32),
            dtype=np.float32
        )

        self.prevDist_ = None
        self.prevAngleDiff_ = None
        self.stepCount_ = 0
        self.maxSteps_ = 1000

        self.networkManager_ = NetworkManager('0.0.0.0')
        self.networkManager_.UdpServerOpen(8986)
        self.networkManager_.TcpServerOpen('0.0.0.0', 8888)
        self.networkManager_.AcceptConnection()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self._SetPlayerPosition(0, -60, 0)
        self._SetPlayerRotation(0, 0)

        self._SendCommand(
            *self._GetPlayerPosition().ToArray(),
            *self._GetPlayerRotation().ToArray()
        )

        self._UpdatePlayerInformation()

        self.prevDist_ = np.linalg.norm(
            self._GetPlayerPosition().ToArray() - self._GetTargetPosition().ToArray()
        )
        
        targetYaw, targetPitch = self._CalcRotationToTarget()
        currentRot = self._GetPlayerRotation()
        self.prevAngleDiff_ = self._CalcAngleDifference(
            currentRot.yaw_, currentRot.pitch_, targetYaw, targetPitch
        )
        
        self.stepCount_ = 0
        
        obs = self._GetObservation()
        return obs, {}
    
    def step(self, action):
        self.stepCount_ += 1
        
        self.SendAction(action)
        self._UpdatePlayerInformation()

        currentPos = self._GetPlayerPosition().ToArray()
        targetPos = self._GetTargetPosition().ToArray()

        dist = np.linalg.norm(currentPos - targetPos)
        
        # Calculate angle alignment
        targetYaw, targetPitch = self._CalcRotationToTarget()
        currentRot = self._GetPlayerRotation()
        angleDiff = self._CalcAngleDifference(
            currentRot.yaw_, currentRot.pitch_, targetYaw, targetPitch
        )

        # Reward calculation
        # 1. Distance reward
        distReward = (self.prevDist_ - dist) * 10.0
        
        # 2. Angle alignment reward
        angleReward = (self.prevAngleDiff_ - angleDiff) * 0.5
        
        # 3. Proximity bonus (when close to target)
        proximityBonus = 0
        if dist < 5.0:
            proximityBonus = (5.0 - dist) * 2.0
        
        # 4. Angle alignment bonus when close 
        alignmentBonus = 0
        if dist < 10.0 and angleDiff < 10.0:
            alignmentBonus = (10.0 - angleDiff) * 0.5
        
        reward = distReward + angleReward + proximityBonus + alignmentBonus
        
        # Small penalty for each step to encourage efficiency
        reward -= 0.01
        
        # Update previous values
        self.prevDist_ = dist
        self.prevAngleDiff_ = angleDiff

        # Termination conditions
        terminated = dist < 1.0
        truncated = self.stepCount_ >= self.maxSteps_
        
        if terminated:
            reward += 500  # Large success bonus
            print(f"SUCCESS! Reached target at step {self.stepCount_}")
        elif truncated:
            reward -= 50  # Penalty for timeout
            print(f"TIMEOUT at step {self.stepCount_}, distance: {dist:.2f}")

        obs = self._GetObservation()

        return obs, reward, terminated, truncated, {}

    # TODO
    # 상대 좌표 구현 필요
    # def SendAction(self, action):
    #     """
    #     Send continuous action: [dx, dy, dz, dyaw, dpitch]
    #     """
    #     pos = self._GetPlayerPosition()
    #     rot = self._GetPlayerRotation()

    #     # Apply position deltas
    #     x = pos.x_ + action[0]
    #     y = pos.y_ + action[1]
    #     z = pos.z_ + action[2]

    #     # Apply rotation deltas
    #     yaw = rot.yaw_ + action[3]
    #     pitch = rot.pitch_ + action[4]

    #     # Normalize yaw to [-180, 180]
    #     yaw = ((yaw + 180) % 360) - 180
        
    #     # Clip pitch to [-90, 90]
    #     pitch = np.clip(pitch, -90, 90)

    #     self._SendCommand(x, y, z, yaw, 0)

    # 절대 좌표 기준
    def SendAction(self, action):
        pos = self._GetPlayerPosition()

        dx, dy, dz = map(float, action[:3])
        x = pos.x_ + dx
        y = pos.y_ + dy
        z = pos.z_ + dz

        targetYaw, targetPitch = self._CalcRotationToTarget()
        self._SendCommand(x, y, z, float(targetYaw), float(targetPitch))

    def _CalcAngleDifference(self, yaw1, pitch1, yaw2, pitch2):
        """Calculate angular difference between two orientations"""
        # Yaw difference (handle wrapping)
        yawDiff = abs(yaw1 - yaw2)
        if yawDiff > 180:
            yawDiff = 360 - yawDiff
        
        # Pitch difference
        pitchDiff = abs(pitch1 - pitch2)
        
        # Combined angle difference
        return np.sqrt(yawDiff**2 + pitchDiff**2)

    def _CalcRotationToTarget(self):
        direction = self._GetTargetPosition().ToArray() - self._GetPlayerPosition().ToArray()
        distanceXZ = np.sqrt(direction[0] ** 2 + direction[2] ** 2)

        yaw = np.degrees(np.arctan2(-direction[0], direction[2]))
        pitch = np.degrees(np.arctan2(-direction[1], distanceXZ))

        return yaw, pitch
    
    def _GetObservation(self):
        relativePos = self._GetTargetPosition().ToArray() - self._GetPlayerPosition().ToArray()
        rot = self._GetPlayerRotation()
        targetYaw, targetPitch = self._CalcRotationToTarget()
        
        return np.concatenate([
            relativePos, 
            [rot.yaw_, rot.pitch_], 
            [targetYaw, targetPitch]
        ]).astype(np.float32)

    def _UpdatePlayerInformation(self):
        self.currentPlayerInformation_ = self.networkManager_.GetPlayerInformation()

    def _GetPlayerPosition(self):
        return self.currentPlayerInformation_.position_
    
    def _GetPlayerRotation(self):
        return self.currentPlayerInformation_.rotation_
    
    def _GetTargetPosition(self):
        return self.targetPlayerInformation_.position_
    
    def _GetTargetRotation(self):
        return self.targetPlayerInformation_.rotation_
    
    def _SetPlayerPosition(self, x, y, z):
        self.currentPlayerInformation_.position_ = Position(x, y, z)

    def _SetPlayerRotation(self, yaw, pitch):
        self.currentPlayerInformation_.rotation_ = Rotation(yaw, pitch)

    def _SetTargetPosition(self, x, y, z):
        self.targetPlayerInformation_.position_ = Position(x, y, z)

    def _SetTargetRotation(self, yaw, pitch):
        self.targetPlayerInformation_.rotation_ = Rotation(yaw, pitch)

    def _SendCommand(self, x, y, z, yaw, pitch):
        self.networkManager_.SendCommand(OPERATION_TYPE.ALL, x=x, y=y, z=z, yaw=yaw, pitch=pitch)
