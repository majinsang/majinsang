#include "pch.h"

#include "NetworkManager.h"
#include "PlayerManager.h"

#include "util.hpp"

using namespace std;

void banner();
void init();

int main(int argc, char* argv[]) {
	init();

	try {
		PlayerManager pm("1.21.8");
		NetworkManager nm(&pm);

		while (1) {
			nm.RecvCommands();
			nm.GetBuffer();
		}
	
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
