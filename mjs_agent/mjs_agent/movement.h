#pragma once
#include "networkmanager.h"

class NetworkManager;

class Movement {
public:
	void MoveToPosition(double targetX, double targetZ, NetworkManager* networkmanager, double threshold);
	void MoveRelation(double targetX, double y, double targetZ, NetworkManager* networkmanager, double threshold);

	bool movingX = false;
	bool movingZ = false;
};


