#include "pch.h"

#include "PlayerManager.h"

using namespace std;

PlayerManager::PlayerManager() {
	positionLck_ = unique_lock<mutex>(positionMutex_);
}

Position PlayerManager::GetPosition() {
    return currentPosition_;
}

void PlayerManager::SetPosition(const Position& pos) { 
    positionLck_.lock();

    currentPosition_ = pos; currentPosition_.z += pos.z; 
}

void PlayerManager::SetTargetPosition(Position& pos, Position::POSITION_TYPE type, double threshold) {
	targetPositionInformation_.type_ = type;
	targetPositionInformation_.position_ = pos;
}

//void Movement::MoveToPosition(double targetX, double targetZ, NetworkManager* networkmanager, double threshold)
//{
//    InputManager::SendKeyInput('W', false);
//    InputManager::SendKeyInput('A', false);
//    InputManager::SendKeyInput('S', false);
//    InputManager::SendKeyInput('D', false);
//
//    bool movingX = false;
//    bool movingZ = false;
//    while (networkmanager->IsUdpRunning()) {
//        Position currentPosition = networkmanager->GetPosition();
//
//        double moveX = targetX - currentPosition.x;
//        double moveZ = targetZ - currentPosition.z;
//        double distance = sqrt(moveX * moveX + moveZ * moveZ);
//
//        if (distance < threshold) {
//            cout << "Reached!" << endl;
//            networkmanager->SendDone();
//            break;
//        }
//
//        if (movingX && abs(moveX) < threshold) {
//            InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
//            movingX = false;
//        }
//        if (movingZ && abs(moveZ) < threshold) {
//            InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', false);
//            movingZ = false;
//        }
//
//        if (!movingX)
//        {
//            if (abs(moveX) > threshold) {
//                InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', true);
//                movingX = true;
//            }
//            else
//            {
//                InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
//                movingX = false;
//            }
//        }
//        if (!movingZ)
//        {
//            if (abs(moveZ) > threshold) {
//                InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', true);
//                movingZ = true;
//            }
//            else
//            {
//                InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', false);
//                movingZ = false;
//            }
//        }
//        Sleep(50);
//    }
//    InputManager::SendKeyInput('W', false);
//    InputManager::SendKeyInput('A', false);
//    InputManager::SendKeyInput('S', false);
//    InputManager::SendKeyInput('D', false);
//}
//
//void Movement::MoveRelation(double relativeX, double relativeY, double relativeZ, NetworkManager* networkmanager, double threshold)
//{
//    InputManager::SendKeyInput('W', false);
//    InputManager::SendKeyInput('A', false);
//    InputManager::SendKeyInput('S', false);
//    InputManager::SendKeyInput('D', false);
//
//    Position currentPosition = networkmanager->GetPosition();
//    
//    double targetX = currentPosition.x + relativeX;
//    double targetZ = currentPosition.z + relativeZ;
//    
//    cout << "Relative Move - Relative: X=" << relativeX << " Z=" << relativeZ 
//              << " | Absolute: X=" << targetX << " Z=" << targetZ << endl;
//
//    bool movingX = false;
//    bool movingZ = false;
//
//    while (networkmanager->IsUdpRunning()) {
//        currentPosition = networkmanager->GetPosition();
//
//        double moveX = targetX - currentPosition.x;
//        double moveZ = targetZ - currentPosition.z;
//        double distance = sqrt(moveX * moveX + moveZ * moveZ);
//
//        if (distance < threshold) {
//            cout << "Reached relative position!" << endl;
//            networkmanager->SendDone();
//            break;
//        }
//
//        if (movingX && abs(moveX) < threshold) {
//            InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
//            movingX = false;
//        }
//
//        if (!movingX) {
//            if (abs(moveX) > threshold) {
//                InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', true);
//                movingX = true;
//            }
//            else {
//                InputManager::SendKeyInput(moveX < 0 ? 'A' : 'D', false);
//                movingX = false;
//            }
//        }
//
//        if (movingZ && abs(moveZ) < threshold) {
//            InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', false);
//            movingZ = false;
//        }
//
//        if (!movingZ) {
//            if (abs(moveZ) > threshold) {
//                InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', true);
//                movingZ = true;
//            }
//            else {
//                InputManager::SendKeyInput(moveZ < 0 ? 'W' : 'S', false);
//                movingZ = false;
//            }
//        }
//
//        Sleep(50);
//    }
//
//    InputManager::SendKeyInput('W', false);
//    InputManager::SendKeyInput('A', false);
//    InputManager::SendKeyInput('S', false);
//    InputManager::SendKeyInput('D', false);
//}
