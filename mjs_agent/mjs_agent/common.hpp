#pragma once

namespace NETWORK {
    enum OPERATION {
        POSITION,
        DIRECTION,
    };
}

struct Position {
    enum POSITION_TYPE {
        RELATION = 1,
        ABSOULUTE
    };

    double x = 0.0;
    double y = 0.0;
    double z = 0.0;

    bool operator==(const Position& other) const {
        return int(x) == int(other.x) && int(y) == int(other.y) && int(z) == int(other.z);
    }

    bool operator!=(const Position& other) const {
        return !(*this == other);
    }

    Position& operator=(const Position& other) {
        if (this != &other) {
            x = other.x;
            y = other.y;
            z = other.z;
        }
        return *this;
    }

    Position(const Position& other) : x(other.x), y(other.y), z(other.z) {}
    Position() = default;
};

using PositionPtr = Position*;