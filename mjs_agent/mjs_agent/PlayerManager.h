#pragma once

#include "common.hpp"
#include "InputManager.h"

class PlayerManager {
private:
	struct PositionInformation {
		Position::POSITION_TYPE type_{};
		Position position_{};
	};

	InputManager inputManager_{};

	Position currentPosition_{};
	std::mutex positionMutex_{};
	std::unique_lock<std::mutex> positionLck_{};

	PositionInformation targetPositionInformation_{};

public:
	PlayerManager();
	~PlayerManager() = default;

	Position GetPosition();
	void SetPosition(const Position& pos);

	void SetTargetPosition(Position& pos, Position::POSITION_TYPE type, double threshold = 0.5);
};

using PlayerManagerPtr = PlayerManager*;