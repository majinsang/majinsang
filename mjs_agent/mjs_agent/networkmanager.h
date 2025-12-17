#pragma once

#include <iostream>

#define WIN32_LEAN_AND_MEAN
#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include <windows.h>
#include <winsock2.h>
#include <thread>
#include <atomic>
#include <mutex>

#include "movement.h"

//전역 변수
constexpr char SERVER_IP[] = "127.0.0.1";
constexpr int SERVER_PORT = 8888;
constexpr int UDP_PORT = 7777;

const int MAX_RETRY_ATTEMPTS = 5;
const int RETRY_DELAY_MS = 5000;

struct Position {
    enum POSITION_TYPE {
        RELATION = 1,
        ABSOULUTE
    };

    double x = 0.0;
    double y = 0.0;
    double z = 0.0;

	/*Position() = default;
	Position(double x, double y, double z) : x(x), y(y), z(z) {}*/

    bool operator==(const Position& other) const {
        /*if (x >= other.x - 0.5 && x <= other.x + 0.5 &&
            y >= other.y - 0.5 && y <= other.y + 0.5 &&
            z >= other.z - 0.5 && z <= other.z + 0.5) {
            return true;
		}*/

		/*std::cout << "z : " << z << " other.z : " << other.z << std::endl;*/

		return int(x) == int(other.x) && int(y) == int(other.y) && int(z) == int(other.z);
	}
};

class Movement;

class NetworkManager {
private:
    void UdpReceiverThread();
    SOCKET udpSock = INVALID_SOCKET;
    std::thread udpThread;
    std::atomic<bool> udpRunning{ false };
    Position position{};
    std::mutex udpMtx;

    void TcpReceiverThread();
    SOCKET tcpSock = INVALID_SOCKET;
    std::thread tcpThread;
    std::atomic<bool> tcpRunning{ false };

    //스마트 포인터, 아니면 애초에 참조자
    Movement* movement;
    //std::mutex positionMtx;

public:
    NetworkManager();
	~NetworkManager();

    void UdpStart();
    void UdpStop();
    Position GetPosition();
    bool IsUdpRunning() const { return udpRunning; }

    void TcpStart();
    void TcpStop();
    void SendDone();
    bool IsTcpRunning() const { return tcpRunning; }
};
