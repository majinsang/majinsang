#include "pch.h"

#include "InputManager.h"

using namespace std;

void InputManager::SendKeyInput(WORD vKey, bool isKeyDown) {
    INPUT input = { 0 }; 

    input.type = INPUT_KEYBOARD;
    input.ki.wVk = vKey;

    if (!isKeyDown)
    {
        input.ki.dwFlags = KEYEVENTF_KEYUP;
    }
    SendInput(1, &input, sizeof(INPUT));
}


void InputManager::SendMouseMove(int dx, int dy) {
    INPUT input = { 0 };

    input.type = INPUT_MOUSE;
    input.mi.dx = dx;
    input.mi.dy = dy;
    input.mi.dwFlags = MOUSEEVENTF_MOVE;
    
    SendInput(1, &input, sizeof(INPUT));
}

void InputManager::SendMouseClick(const std::string& button, bool isDown) {
    INPUT input = { 0 };
    input.type = INPUT_MOUSE;
    
    if (button == "LEFT") {
        input.mi.dwFlags = isDown ? MOUSEEVENTF_LEFTDOWN : MOUSEEVENTF_LEFTUP;
    }
    else if (button == "RIGHT") {
        input.mi.dwFlags = isDown ? MOUSEEVENTF_RIGHTDOWN : MOUSEEVENTF_RIGHTUP;
    }
    
    SendInput(1, &input, sizeof(INPUT));
}
