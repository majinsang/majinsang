#include "pch.h"

#include "common.hpp"
#include "NetworkManager.h"
#include "PlayerManager.h"

using namespace std;
using namespace NETWORK;

void banner();
void init();

int main(int argc, char* argv[]) {
	init();

	try {
		PlayerManager pm("1.21.8");
		NetworkManager nm(&pm);

		while (1) {
			nm.RecvCommands();

			auto buf = nm.GetBuffer();
			CommandHeaderPtr commandHeader = reinterpret_cast<CommandHeaderPtr>(buf.data());

			cout << "========================================" << endl;
			cout << "Received Command Log:" << endl;
			cout << "  OpCode: " << static_cast<int>(commandHeader->opCode_) << endl;
			cout << "  Target Position: ("
				<< commandHeader->targetPi_.position_.x << ", "
				<< commandHeader->targetPi_.position_.y << ", "
				<< commandHeader->targetPi_.position_.z << ")" << endl;
			cout << "  Position Type: " << static_cast<int>(commandHeader->targetPi_.type_) << endl;
			cout << "  Target Rotation: ("
				<< commandHeader->targetRi_.rotation_.pitch << ", "
				<< commandHeader->targetRi_.rotation_.yaw << ")" << endl;
			cout << "  Rotation Type: " << static_cast<int>(commandHeader->targetRi_.type_) << endl;
			cout << "  Buffer Size: " << buf.size() << " bytes" << endl;
			cout << "========================================" << endl;



			switch (commandHeader->opCode_) {
			case OPERATION::POSITION: {
				pm.SetTargetPosition(commandHeader->targetPi_.position_, commandHeader->targetPi_.type_);
				break;
			}
			case OPERATION::ROTATION: {
				pm.SetTargetRotation(commandHeader->targetRi_.rotation_, commandHeader->targetRi_.type_);
				break;
			}
			case OPERATION::ALL: {
				cout << "====SetTargetRotation====" << endl;
				pm.SetTargetRotation(commandHeader->targetRi_.rotation_, commandHeader->targetRi_.type_);
				cout << "====SetTargetPosition====" << endl;
				pm.SetTargetPosition(commandHeader->targetPi_.position_, commandHeader->targetPi_.type_);
				cout << "=========================" << endl;
				break;
			}
			default:
				cerr << "Unknown operation code received." << endl;
				break;
			}

			nm.Signal();
		}
	}
	catch (const exception& e) {
		cerr << "Exception: " << e.what() << endl;
	}

	WSACleanup();
}

void banner() {
	cout << "MJS_AGENT v0.1" << endl;
}

void init() {
	WSADATA wsaData;

	int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (result != 0) {
		std::cerr << "WSAStartup error: " << result << std::endl;
		exit(1);
	}

	banner();
}
