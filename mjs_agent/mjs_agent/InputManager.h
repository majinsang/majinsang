#pragma once

#include <windows.h>
#include <string>

class InputManager {
public:
	static void SendKeyInput(WORD vKey, bool isKeyDown);
	static void SendMouseMove(int dx, int dy);
	static void SendMouseClick(const std::string& button, bool isDown);
};

