#pragma once

#include "pch.h"

#include "common.hpp"

void CommandParse(std::vector<char>& commandPacket) {
	NETWORK::OPERATION opCode = *reinterpret_cast<NETWORK::OPERATION*>(commandPacket.data());

	switch (opCode) {
	case NETWORK::OPERATION::POSITION: {
		Position* pos = reinterpret_cast<Position*>(commandPacket.data() + sizeof(NETWORK::OPERATION));
		break;
	}
	case NETWORK::OPERATION::ROTATION: {
		break;
	}
	default:
		std::cerr << "Unknown operation code received!" << std::endl;
		break;
	}
}