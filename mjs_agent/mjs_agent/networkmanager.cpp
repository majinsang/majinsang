#include "pch.h"

#include "NetworkManager.h"

using namespace std;

NetworkManager::NetworkManager(PlayerManagerPtr pm) {
    udpSocket_ = INVALID_SOCKET;
    tcpSocket_ = INVALID_SOCKET;

    playerManager_ = pm;

    buffer_.resize(BUFFER_SIZE);

    if (!init()) throw runtime_error("Failed to initialize NetworkManager");
}

NetworkManager::~NetworkManager() {
    closesocket(udpSocket_);
    closesocket(tcpSocket_);
}

bool NetworkManager::init() {
    udpSocket_ = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket_ == INVALID_SOCKET) {
        cerr << "UDP socket creation failed: " << WSAGetLastError() << endl;
        return false;
    }

    sockaddr_in udpAddr;
    udpAddr.sin_family = AF_INET;
    udpAddr.sin_port = htons(UDP_PORT);
    udpAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(udpSocket_, (sockaddr*)&udpAddr, sizeof(udpAddr)) == SOCKET_ERROR) {
        cerr << "UDP bind failed: " << WSAGetLastError() << endl;
        closesocket(udpSocket_);
        udpSocket_ = INVALID_SOCKET;
        return false;
    }

    udpThread_ = thread(&NetworkManager::RecvCurrentPosition, this);

    tcpSocket_ = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (tcpSocket_ == INVALID_SOCKET) {
        cerr << "Socket creation failed: " << WSAGetLastError() << endl;
        return false;
    }

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    serverAddr.sin_addr.s_addr = ADDR_ANY;

    if (connect(tcpSocket_, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        cerr << "Connect failed: " << WSAGetLastError() << endl;
        return false;
    }
}

void NetworkManager::UdpBufferClear() {
    u_long bytesAvailable = 0;
    ioctlsocket(udpSocket_, FIONREAD, &bytesAvailable);
    while (bytesAvailable > 0) {
        char discardBuffer[sizeof(Position)];
        recvfrom(udpSocket_, discardBuffer, sizeof(discardBuffer), 0, NULL, NULL);
        ioctlsocket(udpSocket_, FIONREAD, &bytesAvailable);
	}
}

void NetworkManager::Signal() {
    send(tcpSocket_, reinterpret_cast<const char*>(&SUCCESS_SIGNAL), sizeof(SUCCESS_SIGNAL), 0);
}

void NetworkManager::RecvCurrentPosition() {
    while(1) {
        Position pos{};

        /*UdpBufferClear();*/

        int bytesReceived = recvfrom(udpSocket_, reinterpret_cast<char*>(&pos), sizeof(Position), 0, NULL, NULL);

        if (bytesReceived == SOCKET_ERROR) { 
            cerr << "UDP RecvFrom failed: " << WSAGetLastError() << endl; 
            continue;
        }

        playerManager_->SetPosition(pos);
		std::this_thread::sleep_for(std::chrono::milliseconds(INTERVAL_MS));
    }

}

void NetworkManager::RecvCommands() {
    recv(tcpSocket_, buffer_.data(), buffer_.size(), NULL);

    Signal();
}

//return and clear buffer
vector<char> NetworkManager::GetBuffer() {
    vector<char> ret(buffer_.begin(), buffer_.end());

    buffer_.clear();

    return ret;
}
