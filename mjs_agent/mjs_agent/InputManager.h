#pragma once

#include <windows.h>
#include <string>

class InputManager {
	constexpr static char TITLE[] = "Minecraft ";
	constexpr static int MOUSE_SENSITIVITY = 5;

	HWND hwnd_{};

	void SetFocus();
	HWND GetFocus();

	void Key(WORD vKey, bool isKeyDown);
	void Mouse(int dx, int dy);
	void SendMouseClick(const std::string& button, bool isDown);
public:
	enum MOVE_TYPE {
		FORWARD,
		BACKWARD,
		LEFT,
		RIGHT
	};

	enum ROTATE_TYPE {
		YAW_LEFT,
		YAW_RIGHT,
		PITCH_UP,
		PITCH_DOWN
	};

	InputManager(std::string version);
	~InputManager() = default;

	void move(MOVE_TYPE type, bool keyDown);
	void rotate(ROTATE_TYPE type);
};

using InputManagerPtr = InputManager*;

