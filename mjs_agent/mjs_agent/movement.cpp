#include "movement.h"
#include "input.h"
#include <windows.h>
#include <iostream>
#include <cmath>


void Movement::MoveToPosition(double targetX, double targetZ, NetworkManager* networkmanager, double threshold)
{
    InputManager::SendKeyInput('W', false);
    InputManager::SendKeyInput('A', false);
    InputManager::SendKeyInput('S', false);
    InputManager::SendKeyInput('D', false);
    bool movingX = false;
    bool movingZ = false;
    while (networkmanager->IsUdpRunning()) {
        Position currentPosition = networkmanager->GetPosition();

        double moveX = targetX - currentPosition.x;
        double moveZ = targetZ - currentPosition.z;
        double distance = std::sqrt(moveX * moveX + moveZ * moveZ);

        if (distance < threshold) {
            std::cout << "Reached!" << std::endl;
            networkmanager->SendDone();
            break;
        }

        if (movingX && abs(moveX) < threshold) {
            InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
            movingX = false;
        }
        if (movingZ && abs(moveZ) < threshold) {
            InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', false);
            movingZ = false;
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
                InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', true);
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
