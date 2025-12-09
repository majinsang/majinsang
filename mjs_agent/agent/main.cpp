#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <string>
#include <thread>
#include "types.h"
#include "network.h"
#include "command_parser.h"

#pragma comment(lib, "ws2_32.lib")

PlayerState g_playerState;
std::atomic<bool> g_running(true);

int main()
{
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        std::cerr << "WSAStartup error: " << result << std::endl;
        return 1;
    }
    std::cout << "=== MJS Agent Started ===" << std::endl;
    std::cout << "TCP Command Port: " << SERVER_PORT << std::endl;
    std::cout << "UDP Game Info Port: " << UDP_PORT << std::endl;

    std::thread udpThread(UdpReceiverThread);

    SOCKET clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (clientSocket == INVALID_SOCKET) {
        std::cerr << "Socket creation failed: " << WSAGetLastError() << std::endl;
        g_running = false;
        udpThread.join();
        WSACleanup();
        return 1;
    }
    std::cout << "TCP socket created" << std::endl;

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    serverAddr.sin_addr.s_addr = inet_addr(SERVER_IP);

    std::cout << "Connecting to command server: " << SERVER_IP << ":" << SERVER_PORT << std::endl;
    if (connect(clientSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        std::cerr << "Connect failed: " << WSAGetLastError() << std::endl;
        closesocket(clientSocket);
        g_running = false;
        udpThread.join();
        WSACleanup();
        return 1;
    }

    std::cout << "Connected to command server!" << std::endl;

    char buffer[1024];
    while (true) {
        int bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
        
        if (bytesReceived > 0) {
            buffer[bytesReceived] = '\0';
            std::string command(buffer);
            
            command.erase(command.find_last_not_of("\r\n") + 1);
            
            ProcessCommand(command);
        }
        else if (bytesReceived == 0) {
            std::cout << "Server disconnected." << std::endl;
            break;
        }
        else {
            std::cerr << "Recv failed: " << WSAGetLastError() << std::endl;
            break;
        }
    }

    closesocket(clientSocket);
    
    g_running = false;
    udpThread.join();
    WSACleanup();

    std::cout << "=== Program terminated ===" << std::endl;
    return 0;
}
