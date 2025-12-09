#pragma once

#include <windows.h>
#include <string>

// 키보드 입력 전송
void SendKeyInput(WORD vKey, bool isKeyDown);

// 마우스 이동
void SendMouseMove(int dx, int dy);

// 마우스 클릭
void SendMouseClick(const std::string& button, bool isDown);
