#include "pch.h"

#include "PlayerManager.h"

using namespace std;

PlayerManager::PlayerManager(string version) {
	inputManager_ = new InputManager(version);
}

PlayerManager::~PlayerManager() {
		delete inputManager_;
}

void PlayerManager::ResetInputedSate(const DIRECTION_TYPE& dt) {
	switch (dt) {
		case DIRECTION_TYPE::FORWARD: {
			inputManager_->move(InputManager::MOVE_TYPE::FORWARD, false);
			break;
		}
		case DIRECTION_TYPE::FORWARD_RIGHT: {
			inputManager_->move(InputManager::MOVE_TYPE::FORWARD, false);
			inputManager_->move(InputManager::MOVE_TYPE::RIGHT, false);

			break;
		}
		case DIRECTION_TYPE::FORWARD_LEFT: {
			inputManager_->move(InputManager::MOVE_TYPE::FORWARD, false);
			inputManager_->move(InputManager::MOVE_TYPE::LEFT, false);

			break;
		}
		case DIRECTION_TYPE::BACKWARD: {
			inputManager_->move(InputManager::MOVE_TYPE::BACKWARD, false);

			break;
		}
	}
}

int PlayerManager::GetID() {
	return currentPlayerInformation_.playerId_;
}

void PlayerManager::SetID(const uint32_t id) {
	std::unique_lock<std::mutex> lck(mtx_);

	currentPlayerInformation_.playerId_ = id;
}

Position PlayerManager::GetPosition() {
    return currentPlayerInformation_.position_;
}

Position PlayerManager::GetTargetPosition() {
	return targetPositionInformation_.position_;
}	

void PlayerManager::SetPosition(const Position& pos) { 
	std::unique_lock<std::mutex> lck(mtx_);

	currentPlayerInformation_.position_ = pos;
}

void PlayerManager::SetTargetPosition(Position& pos, Position::POSITION_TYPE type, double threshold) {
	targetPositionInformation_.type_ = type;
	targetPositionInformation_.position_ = pos;

	if (currentPlayerInformation_.position_ == pos) return;

	switch (type) {
    case Position::POSITION_TYPE::ABS: {
        double prevDegree = 0.0;
		bool inputed{};

        while (!(pos == currentPlayerInformation_.position_)) {
            double dx = pos.x - currentPlayerInformation_.position_.x;
            double dz = pos.z - currentPlayerInformation_.position_.z;

            double targetYaw = atan2(-dx, dz) * (YAW_180_DEGREE / PI);

            double currentYaw = currentPlayerInformation_.rotation_.yaw;
            double relativeYaw = targetYaw - currentYaw;

            while (relativeYaw > YAW_180_DEGREE) relativeYaw -= YAW_180_DEGREE * 2;
            while (relativeYaw < -YAW_180_DEGREE) relativeYaw += YAW_180_DEGREE * 2;

            if (relativeYaw >= -FORWARD_ANGLE_DEGREE && relativeYaw <= FORWARD_ANGLE_DEGREE) {
				if (currentDirectionType_ != DIRECTION_TYPE::FORWARD) ResetInputedSate(currentDirectionType_);

				if (inputManager_->move(InputManager::MOVE_TYPE::FORWARD, true)) currentDirectionType_ = DIRECTION_TYPE::FORWARD;

				currentDirectionType_ = DIRECTION_TYPE::FORWARD;
            }else if (relativeYaw > FORWARD_ANGLE_DEGREE && relativeYaw <= BACKWARD_ANGLE_DEGREE) {
				if (currentDirectionType_ != DIRECTION_TYPE::FORWARD_RIGHT) ResetInputedSate(currentDirectionType_);

				inputManager_->move(InputManager::MOVE_TYPE::FORWARD, true);
				inputManager_->move(InputManager::MOVE_TYPE::RIGHT, true);

				currentDirectionType_ = DIRECTION_TYPE::FORWARD_RIGHT;
            }else if (relativeYaw < -FORWARD_ANGLE_DEGREE && relativeYaw >= -BACKWARD_ANGLE_DEGREE) {
				if (currentDirectionType_ != DIRECTION_TYPE::FORWARD_LEFT) ResetInputedSate(currentDirectionType_);

				inputManager_->move(InputManager::MOVE_TYPE::FORWARD, true);
				inputManager_->move(InputManager::MOVE_TYPE::LEFT, true);

				currentDirectionType_ = DIRECTION_TYPE::FORWARD_LEFT;
            }else {
				if (currentDirectionType_ != DIRECTION_TYPE::BACKWARD) ResetInputedSate(currentDirectionType_);
				inputManager_->move(InputManager::MOVE_TYPE::BACKWARD, true);

				currentDirectionType_ = DIRECTION_TYPE::BACKWARD;
            }

            prevDegree = relativeYaw;

            std::this_thread::sleep_for(std::chrono::milliseconds(MOVE_INTERVAL_MS));
        }

		if (currentDirectionType_) {
			ResetInputedSate(currentDirectionType_);
			currentDirectionType_ = DIRECTION_TYPE::NONE;
		}

        cout << "Reached target position." << endl;

        break;
    }
		case Position::POSITION_TYPE::REL: {

			break;
		}			  
		default:
			cerr << "Unknown POSITION_TYPE" << endl;
			break;
	}
}

Rotation PlayerManager::GetRotation() {
	return currentPlayerInformation_.rotation_;
}

Rotation PlayerManager::GetTargetRotation() {
	return targetRotationInformation_.rotation_;
}

void PlayerManager::SetRotation(const Rotation& rot) {
	std::unique_lock<std::mutex> lck(mtx_);

	currentPlayerInformation_.rotation_ = rot;
}

void PlayerManager::SetTargetRotation(Rotation& rot, Rotation::ROTATION_TYPE type, double threshold) {
	targetRotationInformation_.type_ = type;
	targetRotationInformation_.rotation_ = rot;
	switch (type) {
		case Rotation::ROTATION_TYPE::YAW: {
			const double eps = 0.5;

			while (true) {
				double currentYaw = currentPlayerInformation_.rotation_.yaw;
				double targetYaw = rot.yaw;

				double dYaw = targetYaw - currentYaw;

				while (dYaw <= -180.0) dYaw += 360.0;
				while (dYaw > 180.0)  dYaw -= 360.0;

				/*std::cout << "dYaw(shortest): " << dYaw
					<< " (cur=" << currentYaw << ", target=" << targetYaw << ")\n";*/

				if (std::abs(dYaw) <= eps) break;

				if (dYaw > 0) {
					inputManager_->rotate(InputManager::ROTATE_TYPE::YAW_RIGHT);
				}
				else {
					inputManager_->rotate(InputManager::ROTATE_TYPE::YAW_LEFT);
				}

				std::this_thread::sleep_for(std::chrono::milliseconds(MOVE_INTERVAL_MS));
			}
			break;
		}
		case Rotation::ROTATION_TYPE::PITCH: {
			while (true) {
				double currentPitch = currentPlayerInformation_.rotation_.pitch;
				double targetPitch = rot.pitch;
				double dPitch = targetPitch - currentPitch;
				/*std::cout << "dPitch: " << dPitch
					<< " (cur=" << currentPitch << ", target=" << targetPitch << ")\n";*/
				if (std::abs(dPitch) <= threshold) break;
				if (dPitch > 0) {
					inputManager_->rotate(InputManager::ROTATE_TYPE::PITCH_DOWN);
				}
				else {
					inputManager_->rotate(InputManager::ROTATE_TYPE::PITCH_UP);
				}
				std::this_thread::sleep_for(std::chrono::milliseconds(MOVE_INTERVAL_MS));
			}
			break;
		}
		case Rotation::ROTATION_TYPE::ALL: {
			const double epsYaw = 0.5;                 // yaw 허용 오차(도)
			const double epsPitch = (threshold > 0.0) ? threshold : 0.5; // pitch 허용 오차(도)

			// (선택) 안전장치: 너무 오래 걸리면 탈출
			const int maxIter = 5000; // MOVE_INTERVAL_MS 기준으로 적당히
			int iter = 0;

			while (true) {
				// 공유 데이터 읽기(여기서도 락 걸어주는 게 안전)
				double currentYaw, currentPitch;
				{
					std::unique_lock<std::mutex> lck(mtx_);
					currentYaw = currentPlayerInformation_.rotation_.yaw;
					currentPitch = currentPlayerInformation_.rotation_.pitch;
				}

				double targetYaw = rot.yaw;
				double targetPitch = rot.pitch;

				// pitch 범위 clamp (MC는 보통 -90~90)
				if (targetPitch > 90.0)  targetPitch = 90.0;
				if (targetPitch < -90.0) targetPitch = -90.0;

				// yaw 최단 회전각(-180, 180]
				double dYaw = targetYaw - currentYaw;
				while (dYaw <= -180.0) dYaw += 360.0;
				while (dYaw > 180.0)  dYaw -= 360.0;

				// pitch 차이
				double dPitch = targetPitch - currentPitch;

				const bool yawDone = (std::abs(dYaw) <= epsYaw);
				const bool pitchDone = (std::abs(dPitch) <= epsPitch);

				if (yawDone && pitchDone) break;

				// 동시에 조작: 한 루프에서 yaw/pitch 둘 다 필요한 경우 둘 다 입력
				if (!yawDone) {
					if (dYaw > 0) inputManager_->rotate(InputManager::ROTATE_TYPE::YAW_RIGHT);
					else          inputManager_->rotate(InputManager::ROTATE_TYPE::YAW_LEFT);
				}

				if (!pitchDone) {
					// 네 구현 기준: dPitch > 0 => PITCH_DOWN
					if (dPitch > 0) inputManager_->rotate(InputManager::ROTATE_TYPE::PITCH_DOWN);
					else            inputManager_->rotate(InputManager::ROTATE_TYPE::PITCH_UP);
				}

				std::this_thread::sleep_for(std::chrono::milliseconds(MOVE_INTERVAL_MS));

				if (++iter >= maxIter) {
					std::cerr << "[WARN] SetTargetRotation(ALL) maxIter reached. "
						<< "cur(yaw=" << currentYaw << ", pitch=" << currentPitch << ") "
						<< "target(yaw=" << rot.yaw << ", pitch=" << rot.pitch << ")\n";
					break;
				}
			}

			break;
		}
		default:
			cerr << "Unknown ROTATION_TYPE" << endl;
			break;
		}
}