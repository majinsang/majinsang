#pragma once

#include "pch.h"

#include "common.hpp"

void CommandParse(std::vector<char>& commandPacket) {
	NETWORK::CommaneHeaderPtr commandHeader = reinterpret_cast<NETWORK::CommaneHeaderPtr>(commandPacket.data());

	
}