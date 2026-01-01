#pragma once

#include "common.hpp"
#include "InputManager.h"

class PlayerManager {
private:
	constexpr static double PI = 3.14159265358979323846;
	constexpr static double YAW_180_DEGREE = 180.0;
	constexpr static double FORWARD_ANGLE_DEGREE = 45;
	constexpr static double BACKWARD_ANGLE_DEGREE = 135;


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
	Position GetTargetPosition();

	void SetPosition(const Position& pos);
	void SetTargetPosition(Position& pos, Position::POSITION_TYPE type, double threshold = 0.5);

	Rotation GetRotation();
	Rotation GetTargetRotation();

	void SetRotation(const Rotation& rot);
	void SetTargetRotation(Rotation& rot, Rotation::ROTATION_TYPE type, double threshold = 1.0);
};

using PlayerManagerPtr = PlayerManager*;