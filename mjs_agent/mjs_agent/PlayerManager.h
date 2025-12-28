#pragma once

#include "common.hpp"
#include "InputManager.h"

class PlayerManager {
private:
	//PlayerController -> PlayerManager
	InputManagerPtr inputManager_{};

	/*Position currentPosition_{};*/
	PlayerInformation currentPlayerInformation_{};

	std::mutex mtx_{};

	PositionInformation targetPositionInformation_{};
	RotationInformation targetRotationInformation_{};

public:
	PlayerManager(std::string version);
	~PlayerManager();

	int GetID();
	void SetID(const uint32_t id);

	Position GetPosition();
	void SetPosition(const Position& pos);
	void SetTargetPosition(Position& pos, Position::POSITION_TYPE type, double threshold = 0.5);

	Rotation GetRotation();
	void SetRotation(const Rotation& rot);
	void SetTargetRotation(Rotation& rot, Rotation::ROTATION_TYPE type, double threshold = 1.0);
};

using PlayerManagerPtr = PlayerManager*;