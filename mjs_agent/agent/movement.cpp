#include "movement.h"
#include "types.h"
#include "input_handler.h"
#include <windows.h>
#include <iostream>
#include <cmath>

void MoveToBlock(int targetBlockX, int targetBlockZ)
{
    MoveToPosition(static_cast<double>(targetBlockX), static_cast<double>(targetBlockZ), 0.5);
}

void MoveToPosition(double targetX, double targetZ, double threshold)
{
    std::cout << "Moving to target: X=" << targetX << ", Z=" << targetZ 
              << " (threshold=" << threshold << ")" << std::endl;
    
    bool movingX = false, movingZ = false;
    
    while (g_running) {
        double currentX, currentY, currentZ;
        {
            std::lock_guard<std::mutex> lock(g_playerState.mtx);
            currentX = g_playerState.x;
            currentY = g_playerState.y;
            currentZ = g_playerState.z;
        }
        
        double dx = targetX - currentX;
        double dz = targetZ - currentZ;
        double distance = std::sqrt(dx * dx + dz * dz);
        
        std::cout << "Current: (" << currentX << ", " << currentY << ", " << currentZ << ") "
                  << "Distance: " << distance << std::endl;
        
        if (distance < threshold) {
            if (movingX) {
                SendKeyInput(dx > 0 ? 'D' : 'A', false);
                movingX = false;
            }
            if (movingZ) {
                SendKeyInput(dz > 0 ? 'S' : 'W', false);
                movingZ = false;
            }
            std::cout << "Target reached!" << std::endl;
            break;
        }
        
        if (std::abs(dx) > threshold) {
            if (!movingX) {
                if (dx > 0) {
                    SendKeyInput('D', true);
                    movingX = true;
                } else {
                    SendKeyInput('A', true);
                    movingX = true;
                }
            }
        } else if (movingX) {
            SendKeyInput(dx > 0 ? 'D' : 'A', false);
            movingX = false;
        }
        
        if (std::abs(dz) > threshold) {
            if (!movingZ) {
                if (dz > 0) {
                    SendKeyInput('W', true);  // Z 증가 = 앞으로
                    movingZ = true;
                } else {
                    SendKeyInput('S', true);  // Z 감소 = 뒤로
                    movingZ = true;
                }
            }
        } else if (movingZ) {
            SendKeyInput(dz > 0 ? 'W' : 'S', false);
            movingZ = false;
        }
        
        Sleep(50);
    }
    
    // 혹시 루프를 빠져나올 때 키가 눌린 상태면 모두 해제
    SendKeyInput('W', false);
    SendKeyInput('A', false);
    SendKeyInput('S', false);
    SendKeyInput('D', false);
}

void MoveDirection(char direction, int blocks)
{
    double startX, startY, startZ;
    {
        std::lock_guard<std::mutex> lock(g_playerState.mtx);
        startX = g_playerState.x;
        startY = g_playerState.y;
        startZ = g_playerState.z;
    }
    
    double targetX = startX;
    double targetZ = startZ;
    
    switch (direction) {
        case 'W': targetZ -= blocks; break;
        case 'S': targetZ += blocks; break;
        case 'A': targetX -= blocks; break;
        case 'D': targetX += blocks; break;
    }
    
    std::cout << "Moving " << direction << " for " << blocks << " blocks" << std::endl;
    std::cout << "Start: (" << startX << ", " << startZ << ")" << std::endl;
    std::cout << "Target: (" << targetX << ", " << targetZ << ")" << std::endl;
    
    MoveToPosition(targetX, targetZ, 0.5);
}
