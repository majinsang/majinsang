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

        if (movingX && std::abs(moveX) < threshold) {
            InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
            movingX = false;
        }
        if (movingZ && std::abs(moveZ) < threshold) {
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

void Movement::MoveRelation(char target, double relativeX, double relativeZ, NetworkManager* networkmanager, double threshold)
{
    // 모든 키 초기화
    InputManager::SendKeyInput('W', false);
    InputManager::SendKeyInput('A', false);
    InputManager::SendKeyInput('S', false);
    InputManager::SendKeyInput('D', false);

    // 현재 위치 가져오기
    Position currentPosition = networkmanager->GetPosition();
    
    // 상대 좌표를 절대 좌표로 변환
    double targetX = currentPosition.x + relativeX;
    double targetZ = currentPosition.z + relativeZ;
    
    std::cout << "Relative Move - Target: " << (int)target 
              << " | Relative: X=" << relativeX << " Z=" << relativeZ 
              << " | Absolute: X=" << targetX << " Z=" << targetZ << std::endl;

    bool movingX = false;
    bool movingZ = false;

    // target에 따라 이동할 축 결정
    // 0: X만, 2: Z만, 3: 둘 다
    bool moveXAxis = (target == 0 || target == 3);
    bool moveZAxis = (target == 2 || target == 3);

    // X만 이동하는 경우 목표 Z를 현재 위치로 설정
    if (target == 0) {
        targetZ = currentPosition.z;
    }
    // Z만 이동하는 경우 목표 X를 현재 위치로 설정
    else if (target == 2) {
        targetX = currentPosition.x;
    }

    while (networkmanager->IsUdpRunning()) {
        currentPosition = networkmanager->GetPosition();

        double moveX = targetX - currentPosition.x;
        double moveZ = targetZ - currentPosition.z;
        
        // 이동해야 할 축만 계산
        double distance = 0.0;
        if (moveXAxis) distance += moveX * moveX;
        if (moveZAxis) distance += moveZ * moveZ;
        distance = std::sqrt(distance);

        if (distance < threshold) {
            std::cout << "Reached relative position!" << std::endl;
            networkmanager->SendDone();
            break;
        }

        // X축 이동 처리
        if (moveXAxis) {
            if (movingX && std::abs(moveX) < threshold) {
                InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
                movingX = false;
            }

            if (!movingX) {
                if (std::abs(moveX) > threshold) {
                    InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', true);
                    movingX = true;
                }
                else {
                    InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
                    movingX = false;
                }
            }
        }

        // Z축 이동 처리
        if (moveZAxis) {
            if (movingZ && std::abs(moveZ) < threshold) {
                InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', false);
                movingZ = false;
            }

            if (!movingZ) {
                if (std::abs(moveZ) > threshold) {
                    InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', true);
                    movingZ = true;
                }
                else {
                    InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', false);
                    movingZ = false;
                }
            }
        }

        Sleep(50);
    }

    // 모든 키 해제
    InputManager::SendKeyInput('W', false);
    InputManager::SendKeyInput('A', false);
    InputManager::SendKeyInput('S', false);
    InputManager::SendKeyInput('D', false);
}
