#define WIN32_LEAN_AND_MEAN
#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <string>
#include "networkmanager.h"


#pragma comment(lib, "ws2_32.lib")

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

    NetworkManager netManager;
    netManager.UdpStart();
    netManager.TcpStart();

    WSACleanup();
    std::cout << "=== Program terminated ===" << std::endl;
    return 0;
}
