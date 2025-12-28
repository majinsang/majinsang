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

void PlayerManager::SetPosition(const Position& pos) { 
	std::unique_lock<std::mutex> lck(mtx_);

	currentPlayerInformation_.position_ = pos;
}

void PlayerManager::SetTargetPosition(Position& pos, Position::POSITION_TYPE type, double threshold) {
	targetPositionInformation_.type_ = type;
	targetPositionInformation_.position_ = pos;

	switch (type) {
		case Position::POSITION_TYPE::ABSOULUTE : {
			if (GetPosition() != pos) {
				
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

void PlayerManager::SetRotation(const Rotation& rot) {
	std::unique_lock<std::mutex> lck(mtx_);

	currentPlayerInformation_.rotation_ = rot;
}

void PlayerManager::SetTargetRotation(Rotation& rot, Rotation::ROTATION_TYPE type, double threshold) {
	targetRotationInformation_.type_ = type;
	targetRotationInformation_.rotation_ = rot;
	switch (type) {
		case Rotation::ROTATION_TYPE::YAW: {

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