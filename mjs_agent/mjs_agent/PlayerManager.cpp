#include "pch.h"

#include "PlayerManager.h"

using namespace std;

PlayerManager::PlayerManager(string version) {
	inputManager_ = new InputManager(version);
}

PlayerManager::~PlayerManager() {
		delete inputManager_;
}

int PlayerManager::GetID() {
	return currentPlayerInformation_.playerId_;
}

void PlayerManager::SetID(const uint32_t id) {
	std::unique_lock<std::mutex> lck(mtx_);

	currentPlayerInformation_.playerId_ = id;
}

Position PlayerManager::GetPosition() {
    return currentPlayerInformation_.position_;
}

Position PlayerManager::GetTargetPosition() {
	return targetPositionInformation_.position_;
}	

void PlayerManager::SetPosition(const Position& pos) { 
	std::unique_lock<std::mutex> lck(mtx_);

	currentPlayerInformation_.position_ = pos;
}

void PlayerManager::SetTargetPosition(Position& pos, Position::POSITION_TYPE type, double threshold) {
	targetPositionInformation_.type_ = type;
	targetPositionInformation_.position_ = pos;

	if (currentPlayerInformation_.position_ == pos) return;

	switch (type) {
		case Position::POSITION_TYPE::ABSOULUTE: {
			while (pos != currentPlayerInformation_.position_) {
				double dx = pos.x - currentPlayerInformation_.position_.x;
				double dz = pos.z - currentPlayerInformation_.position_.z;
			
				double targetYaw = atan2(-dx, dz) * (YAW_180_DEGREE / PI);
			
				double currentYaw = currentPlayerInformation_.rotation_.yaw;
				double relativeYaw = targetYaw - currentYaw;
			
				while (relativeYaw > YAW_180_DEGREE) relativeYaw -= YAW_180_DEGREE * 2;
				while (relativeYaw < -YAW_180_DEGREE) relativeYaw += YAW_180_DEGREE * 2;
			
				if (relativeYaw >= -FORWARD_ANGLE_DEGREE && relativeYaw <= FORWARD_ANGLE_DEGREE) {
					inputManager_->move(InputManager::MOVE_TYPE::FORWARD, true);
				}
				else if (relativeYaw > FORWARD_ANGLE_DEGREE && relativeYaw <= BACKWARD_ANGLE_DEGREE) {
					inputManager_->move(InputManager::MOVE_TYPE::FORWARD, true);
					inputManager_->move(InputManager::MOVE_TYPE::RIGHT, true);
				}
				else if (relativeYaw < -FORWARD_ANGLE_DEGREE && relativeYaw >= -BACKWARD_ANGLE_DEGREE) {
					inputManager_->move(InputManager::MOVE_TYPE::FORWARD, true);
					inputManager_->move(InputManager::MOVE_TYPE::LEFT, true);
				}
				else {
					inputManager_->move(InputManager::MOVE_TYPE::BACKWARD, true);
				}
			}
			break;
		}
		case Position::POSITION_TYPE::RELATION: {

			break;
		}			  
		default:
			cerr << "Unknown POSITION_TYPE" << endl;
			break;
	}
}

Rotation PlayerManager::GetRotation() {
	return currentPlayerInformation_.rotation_;
}

Rotation PlayerManager::GetTargetRotation() {
	return targetRotationInformation_.rotation_;
}

void PlayerManager::SetRotation(const Rotation& rot) {
	std::unique_lock<std::mutex> lck(mtx_);

	currentPlayerInformation_.rotation_ = rot;
}

void PlayerManager::SetTargetRotation(Rotation& rot, Rotation::ROTATION_TYPE type, double threshold) {
	targetRotationInformation_.type_ = type;
	targetRotationInformation_.rotation_ = rot;
	switch (type) {
	case Rotation::ROTATION_TYPE::YAW: {
		while (currentPlayerInformation_.rotation_.yaw != rot.yaw) {
			if ((currentPlayerInformation_.rotation_.yaw - rot.yaw) > 0) {
				inputManager_->rotate(InputManager::ROTATE_TYPE::YAW_RIGHT);
			}
			else {
				inputManager_->rotate(InputManager::ROTATE_TYPE::YAW_LEFT);
			}
		}
		break;
	}
	case Rotation::ROTATION_TYPE::PITCH: {

		break;
	}
	default:
		cerr << "Unknown ROTATION_TYPE" << endl;
		break;
	}
}