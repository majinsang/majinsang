#include "networkmanager.h"
#include "movement.h"
#include <iostream>


NetworkManager::NetworkManager()
{
	movement = new Movement();
}

NetworkManager::~NetworkManager()
{
    UdpStop();
    TcpStop();
    delete movement;
}

void NetworkManager::UdpStart()
{
    if (udpRunning) {
        std::cout << "UDP receiver already running" << std::endl;
        return;
    }

    udpRunning = true;
    udpThread = std::thread(&NetworkManager::UdpReceiverThread, this);
    std::cout << "UDP receiver started" << std::endl;
}

void NetworkManager::UdpStop()
{
    if (!udpRunning) {
        return;
    }

    udpRunning = false;
    
    if (udpThread.joinable()) {
        udpThread.join();
    }
    
    if (udpSock != INVALID_SOCKET) {
        closesocket(udpSock);
        udpSock = INVALID_SOCKET;
    }
    
    std::cout << "UDP receiver stopped" << std::endl;
}

Position NetworkManager::GetPosition()
{
    std::lock_guard<std::mutex> lock(udpMtx);
    return position;
}

void NetworkManager::UdpReceiverThread()
{
    udpSock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSock == INVALID_SOCKET) {
        std::cerr << "UDP socket creation failed: " << WSAGetLastError() << std::endl;
        return;
    }

    sockaddr_in udpAddr;
    udpAddr.sin_family = AF_INET;
    udpAddr.sin_port = htons(UDP_PORT);
    udpAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(udpSock, (sockaddr*)&udpAddr, sizeof(udpAddr)) == SOCKET_ERROR) {
        std::cerr << "UDP bind failed: " << WSAGetLastError() << std::endl;
        closesocket(udpSock);
        udpSock = INVALID_SOCKET;
        return;
    }

    std::cout << "UDP receiver listening on port " << UDP_PORT << std::endl;

    double buffer[128];

    while (udpRunning) {
        int bytesReceived = recvfrom(udpSock, reinterpret_cast<char*>(buffer), sizeof(buffer), 0, NULL, NULL);
        
        if (bytesReceived >= sizeof(double) * 3) {
            std::lock_guard<std::mutex> lock(udpMtx);
            position.x = buffer[0];
            position.y = buffer[1];
            position.z = buffer[2];
            //std::cout << "[UDP] Position: X=" << position.x
            //    << " Y=" << position.y << " Z=" << position.z << std::endl;
        }
    }

    closesocket(udpSock);
    udpSock = INVALID_SOCKET;
}

void NetworkManager::TcpStart()
{
    if (tcpRunning) {
        std::cout << "TCP receiver already running" << std::endl;
        return;
    }

    tcpRunning = true;
    tcpThread = std::thread(&NetworkManager::TcpReceiverThread, this);
    std::cout << "TCP receiver started" << std::endl;
}

void NetworkManager::TcpStop()
{
    if (!tcpRunning) {
        return;
    }
    tcpRunning = false;
    if (tcpThread.joinable()) {
        tcpThread.join();
    }
    if (tcpSock != INVALID_SOCKET) {
        closesocket(tcpSock);
        tcpSock = INVALID_SOCKET;
        std::cout << "Tcp socket closed" << std::endl;
    }
}

void NetworkManager::TcpReceiverThread()
{
    while (tcpRunning) {

        tcpSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (tcpSock == INVALID_SOCKET) {
            std::cerr << "Socket creation failed: " << WSAGetLastError() << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(RETRY_DELAY_MS));
            continue;
        }
        std::cout << "TCP socket created" << std::endl;

        sockaddr_in serverAddr;
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(SERVER_PORT);
        serverAddr.sin_addr.s_addr = inet_addr(SERVER_IP);

        std::cout << "Connecting to command server: " << SERVER_IP << ":" << SERVER_PORT << std::endl;
        if (connect(tcpSock, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            std::cerr << "Connect failed: " << WSAGetLastError() << std::endl;
            closesocket(tcpSock);
            tcpSock = INVALID_SOCKET;
            std::cout << "Retrying in " << RETRY_DELAY_MS / 1000 << " seconds" << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(RETRY_DELAY_MS));
            continue;
        }
        std::cout << "Connected to command server!" << std::endl;

        double buffer[128];

        while (tcpRunning) {
            int bytesReceived = recv(tcpSock, reinterpret_cast<char*>(buffer), sizeof(buffer), 0);

            if (bytesReceived >= sizeof(double) * 3) {
                std::cout << "target received. \n X:" << buffer[0] << " Y: " << buffer[1] << " Z: " << buffer[2] << std::endl;
                movement->MoveToPosition(buffer[0], buffer[2], this, 0.5);

            }
            else if (bytesReceived == 0) {
                std::cout << "Server disconnected." << std::endl;
                break;
            }
            else if (bytesReceived == SOCKET_ERROR) {
                std::cerr << "TCP Recv failed: " << WSAGetLastError() << std::endl;
                break;
            }
        }
        closesocket(tcpSock);
        tcpSock = INVALID_SOCKET;
        
        if (!tcpRunning) {
            break;
        }
        
        std::cout << "Attempting to reconnect..." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(RETRY_DELAY_MS));
    }
}

void NetworkManager::SendDone()
{
    if (tcpSock != INVALID_SOCKET) {
        bool doneSignal = true;
        send(tcpSock, reinterpret_cast<const char*>(&doneSignal),sizeof(doneSignal), 0);
    }
}
