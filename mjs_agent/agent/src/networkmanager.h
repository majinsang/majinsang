#pragma once

#define WIN32_LEAN_AND_MEAN
#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include "movement.h"
#include <windows.h>
#include <winsock2.h>
#include <thread>
#include <atomic>
#include <mutex>

struct Position {
    double x = 0.0;
    double y = 0.0;
    double z = 0.0;
};

constexpr char SERVER_IP[] = "127.0.0.1";
constexpr int SERVER_PORT = 8888;
constexpr int UDP_PORT = 7777;

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

    Movement* movement;

public:
    void UdpStart();
    void UdpStop();
    Position GetPosition();
    bool IsUdpRunning() const { return udpRunning; }

    void TcpStart();
    void TcpStop();
    void SendDone();
    bool IsTcpRunning() const { return tcpRunning; }
};
