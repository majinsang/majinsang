#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <string>

#pragma comment(lib, "ws2_32.lib")

const char* SERVER_IP = "127.0.0.1";
const int SERVER_PORT = 8888;

void SendKeyInput(WORD vKey, bool isKeyDown)
{
    INPUT input = { 0 }; 
    input.type = INPUT_KEYBOARD;
    input.ki.wVk = vKey;

    if (!isKeyDown)
    {
        input.ki.dwFlags = KEYEVENTF_KEYUP;
    }

    SendInput(1, &input, sizeof(INPUT));
}

void ProcessCommand(const std::string& command)
{
    std::cout << "Command received: " << command << std::endl;

    char key = command[0];
    bool isDown = (command.find("DOWN") != std::string::npos);

    WORD vKey = 0;

    switch (key) {
        case 'W':
        case 'w':
            vKey = 'W';
            break;
        case 'A':
        case 'a':
            vKey = 'A';
            break;
        case 'S':
        case 's':
            vKey = 'S';
            break;
        case 'D':
        case 'd':
            vKey = 'D';
            break;
        case 'X':
        case 'x':
        case ' ':
            vKey = VK_SPACE;
            break;
        default:
            std::cout << "Unknown key: " << key << std::endl;
            return;
    }

    SendKeyInput(vKey, isDown);
    std::cout << "Key input:" << key << "\n Action=" << (isDown ? "DOWN" : "UP") << std::endl;
}

int main()
{
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        std::cerr << "WSAStartup error: " << result << std::endl;
        return 1;
    }
    std::cout << "Socket start" << std::endl;

    SOCKET clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (clientSocket == INVALID_SOCKET) {
        std::cerr << "Socket creation failed: " << WSAGetLastError() << std::endl;
        WSACleanup();
        return 1;
    }
    std::cout << "Socket created" << std::endl;

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    serverAddr.sin_addr.s_addr = inet_addr(SERVER_IP);

    std::cout << "Connecting IP: " << SERVER_IP << "Port :" << SERVER_PORT << std::endl;
    if (connect(clientSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        std::cerr << "Connect failed: " << WSAGetLastError() << std::endl;
        closesocket(clientSocket);
        WSACleanup();
        return 1;
    }

    std::cout << "Connected to server" << std::endl;

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
    WSACleanup();

    std::cout << "Program terminated." << std::endl;
    return 0;
}
