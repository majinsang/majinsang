#pragma once

#include "common.hpp"

#include "PlayerManager.h"

class NetworkManager {
private:
    enum OPERATION {
        POSITION,
        DIRECTION,
    };

    constexpr static uint16_t SERVER_PORT = 8888;
    constexpr static uint16_t UDP_PORT = 7777;

    constexpr static uint8_t MAX_RETRY_ATTEMPTS = 5;
	constexpr static uint32_t RETRY_DELAY_MS = 5000;

    constexpr static bool SUCCESS_SIGNAL = true;

	constexpr static size_t BUFFER_SIZE = 1024;
	constexpr static uint32_t INTERVAL_MS = 50;

    SOCKET udpSocket_{}, tcpSocket_{};
    std::vector<char> tcpBuffer_{};

    std::thread udpThread_{};

    PlayerManagerPtr playerManager_{};

    void UdpBufferClear();
    
    void cleanup();
    bool init();

public:
    NetworkManager(PlayerManagerPtr pm);
	~NetworkManager();

    std::vector<char> GetBuffer();

    void RecvCurrentPlayerInformation();
    void RecvCommands();

    void Signal();
};

using NetworkManagerPtr = NetworkManager*;