#include "movement.h"
#include "input.h"
#include <windows.h>
#include <iostream>
#include <cmath>


void Movement::MoveToPosition(double targetX, double targetZ, NetworkManager* networkmanager, double threshold)
{
    // 현재 위치 받기 -> 그 위치와 목표 위치 계산 -> 그만큼 이동
    // 대각선도 가능 HOW?
    // 그냥 키 누르기? 
    // 3 , 3
    // -2 , 2
    while (networkmanager->IsUdpRunning()) {
        Position currentPosition = networkmanager->GetPosition();

        double moveX = targetX - currentPosition.x;
        double moveZ = targetZ - currentPosition.z;
        double distance = std::sqrt(moveX * moveX + moveZ * moveZ);

        if (distance < threshold) {
            if (movingX) {
                InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
                moveX = false;
            }
            if (movingZ) {
                InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', false);
                movingZ = false;
            }
            std::cout << "Reached!" << std::endl;
            networkmanager->SendDone();
            break;
        }
        if (!movingX)
        {
            if (std::abs(moveX) > threshold) {
                InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', true);
                movingX = true;
            }
            else
            {
                InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
                movingX = false;
            }
        }
        if (!movingZ)
        {
            if (std::abs(moveZ) > threshold) {
                InputManager::SendKeyInput(moveZ < 0 ? 'A' : 'D', true);
                movingZ = true;
            }
            else
            {
                InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', false);
                movingZ = false;
            }
        }
        Sleep(50);
    }
    InputManager::SendKeyInput('W', false);
    InputManager::SendKeyInput('A', false);
    InputManager::SendKeyInput('S', false);
    InputManager::SendKeyInput('D', false);
}
