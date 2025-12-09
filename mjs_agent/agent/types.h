#pragma once

#include <thread>
#include <mutex>
#include <atomic>

struct PlayerState {
    double x = 0.0;
    double y = 0.0;
    double z = 0.0;
    std::mutex mtx;
};


extern PlayerState g_playerState;
extern std::atomic<bool> g_running;

constexpr char SERVER_IP[] = "127.0.0.1";
constexpr int SERVER_PORT = 8888;
constexpr int UDP_PORT = 7777;
