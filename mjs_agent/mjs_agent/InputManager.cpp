#include "pch.h"

#include "InputManager.h"

using namespace std;

InputManager::InputManager(string version) {
    string windowName = TITLE + version;

#if _RELASE
    hwnd_ = FindWindowA(windowName.c_str(), NULL);
    if (!hwnd_) throw runtime_error("Failed to get hwnd");
#endif

}

void InputManager::SetFocus() {
    SetForegroundWindow(hwnd_);
}

HWND InputManager::GetFocus() {
    return GetForegroundWindow();
}

void InputManager::Key(WORD vKey, bool isKeyDown) {
    INPUT input = { 0 }; 

    input.type = INPUT_KEYBOARD;
    input.ki.wVk = vKey;

    if (!isKeyDown) input.ki.dwFlags = KEYEVENTF_KEYUP;

    SendInput(1, &input, sizeof(INPUT));
}

void InputManager::Mouse(int x, int y) {
    INPUT input = { 0 };
    input.type = INPUT_MOUSE;

    input.mi.dx = x;
    input.mi.dy = y;
    input.mi.dwFlags = MOUSEEVENTF_MOVE;

    SendInput(1, &input, sizeof(INPUT));
}

bool InputManager::move(InputManager::MOVE_TYPE type, bool keyDown) {
    
    switch (type) {
    case FORWARD:
        Key('W', keyDown);
        cout << "W" << keyDown << endl;
        break;
    case BACKWARD:
        Key('S', keyDown);
        cout << "S" << keyDown << endl;
        break;
    case LEFT:
        Key('A', keyDown);
        cout << "A" << keyDown << endl;
        break;
    case RIGHT:
        Key('D', keyDown);
        cout << "D" << keyDown << endl;
        break;
    default:
        cerr << "[InputManager] Somethings wrong" << endl;
        return false;
        break;
    }

    return true;
}

void InputManager::rotate(InputManager::ROTATE_TYPE type) {
    switch (type) {
    case YAW_LEFT:
        Mouse(-MOUSE_SENSITIVITY, 0);
        break;
    case YAW_RIGHT:
        Mouse(MOUSE_SENSITIVITY, 0);
        break;
    case PITCH_UP:
        Mouse(0, MOUSE_SENSITIVITY);
        break;
    case PITCH_DOWN:
        Mouse(0, -MOUSE_SENSITIVITY);
        break;
    default:
        break;
    }
}