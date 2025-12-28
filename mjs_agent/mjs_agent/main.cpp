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

		while(1) {
			auto pos = pm.GetPosition();
			auto rot = pm.GetRotation();

			cout << "ID { " << pm.GetID() << " }" << endl;
			cout << "Position { " << pos.x << ", " << pos.y << ", " << pos.z << " }" << endl;
			cout << "Rotation { " << rot.yaw << ", " << rot.pitch << " }" << endl;

			Sleep(1000);
		}

		/*while (1) {
			nm.RecvCommands();

			CommandHeaderPtr commandHeader = reinterpret_cast<CommandHeaderPtr>(nm.GetBuffer().data());

			switch (commandHeader->opCode_) {
				case OPERATION::POSITION: {
					pm.SetTargetPosition(commandHeader->targetPi_.position_, commandHeader->targetPi_.type_);
					break;
				}
				case OPERATION::ROTATION: {
					pm.SetTargetRotation(commandHeader->targetRi_.rotation_, commandHeader->targetRi_.type_);
					break;
				}
				default:
					cerr << "Unknown operation code received." << endl;
					break;
			}

			nm.Signal();
		}*/
	
	}catch(const exception& e) {
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
