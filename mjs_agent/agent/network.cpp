#include "network.h"
#include "types.h"
#include <winsock2.h>
#include <iostream>
#include <string>

void UdpReceiverThread()
{
    SOCKET udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket == INVALID_SOCKET) {
        std::cerr << "UDP socket creation failed: " << WSAGetLastError() << std::endl;
        return;
    }

    sockaddr_in udpAddr;
    udpAddr.sin_family = AF_INET;
    udpAddr.sin_port = htons(UDP_PORT);
    udpAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(udpSocket, (sockaddr*)&udpAddr, sizeof(udpAddr)) == SOCKET_ERROR) {
        std::cerr << "UDP bind failed: " << WSAGetLastError() << std::endl;
        closesocket(udpSocket);
        return;
    }

    std::cout << "UDP receiver listening on port " << UDP_PORT << std::endl;

    char buffer[1024];
    sockaddr_in senderAddr;
    int senderAddrSize = sizeof(senderAddr);

    while (g_running) {
        int bytesReceived = recvfrom(udpSocket, buffer, sizeof(buffer), 0,
                                      (sockaddr*)&senderAddr, &senderAddrSize);
        
        if (bytesReceived > 0) {
            double* coords = reinterpret_cast<double*>(buffer);
            
            std::lock_guard<std::mutex> lock(g_playerState.mtx);
            g_playerState.x = coords[0];  // 첫 8바이트: X
            g_playerState.y = coords[1];  // 다음 8바이트: Y
            g_playerState.z = coords[2];  // 마지막 8바이트: Z
            
            // std::cout << "Player position: X=" << g_playerState.x 
            //           << ", Y=" << g_playerState.y
            //           << ", Z=" << g_playerState.z << std::endl;
        }
    }

    closesocket(udpSocket);
}
