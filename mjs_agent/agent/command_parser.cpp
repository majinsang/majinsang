#include "command_parser.h"
#include "input_handler.h"
#include "movement.h"
#include <windows.h>
#include <iostream>

void ProcessCommand(const std::string& command)
{
    std::cout << "\n=== Command received: " << command << " ===" << std::endl;

    if (command.empty()) {
        std::cout << "Empty command" << std::endl;
        return;
    }

    if (command.substr(0, 5) == "GOTO_") {
        size_t pos1 = command.find('_', 5);
        std::cout << "pos1: " << pos1;
        size_t pos2 = command.find('_', pos1 + 1);
        if (pos1 != std::string::npos && pos2 != std::string::npos) {
            double targetX = std::stod(command.substr(5, pos1 - 5));
            double targetZ = std::stod(command.substr(pos2 + 1));
            MoveToPosition(targetX, targetZ, 0.1);
            return;
        }
    }

    if (command[0] == 'M' && command.size() > 2 && command[1] == '_') {
        if (command[2] == 'M' && command[3] == '_') {
            size_t pos1 = 4;
            size_t pos2 = command.find('_', pos1);
            if (pos2 != std::string::npos) {
                int dx = std::stoi(command.substr(pos1, pos2 - pos1));
                int dy = std::stoi(command.substr(pos2 + 1));
                SendMouseMove(dx, dy);
                std::cout << "Mouse moved: " << dx << "," << dy << std::endl;
            }
            return;
        }

        else if ((command[2] == 'L' || command[2] == 'R') && command[3] == '_') {
            std::string button = (command[2] == 'L') ? "LEFT" : "RIGHT";
            bool isDown = (command.find("Down") != std::string::npos);
            SendMouseClick(button, isDown);
            std::cout << "Mouse " << button << " " << (isDown ? "DOWN" : "UP") << std::endl;
            return;
        }
        
        std::cout << "Unknown mouse command" << std::endl;
        return;
    }

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
