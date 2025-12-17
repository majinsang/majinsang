#pragma once

#include "pch.h"

#include "common.hpp"

void CommandParse(std::vector<char>& commandPacket) { 
    NETWORK::OPERATION opCode = *reinterpret_cast<NETWORK::OPERATION*>(commandPacket.data());

    switch (opCode) {
        case NETWORK::OPERATION::POSITION: {
            Position* pos = reinterpret_cast<Position*>(commandPacket.data() + sizeof(NETWORK::OPERATION));
            std::cout << "Position Command Received - X: " << pos->x << " Y: " << pos->y << " Z: " << pos->z << std::endl;
            break;
		}
                                    case NETWORK::OPERATION::DIRECTION: {
            Position* dir = reinterpret_cast<Position*>(commandPacket.data() + sizeof(NETWORK::OPERATION));
            std::cout << "Direction Command Received - X: " << dir->x << " Y: " << dir->y << " Z: " << dir->z << std::endl;
            break;
        }
        default:
            std::cerr << "Unknown operation code received!" << std::endl;
			break;
    }
}