#pragma once

namespace NETWORK {
    enum OPERATION {
        POSITION,
        ROTATION,
    };
}

struct Rotation {
    enum ROTATION_TYPE {
        YAW,
        PITCH
	};

	double yaw = 0.0;
	double pitch = 0.0;

    bool operator==(const Rotation& other) const {
        return int(yaw) == int(other.yaw) && int(pitch) == int(other.pitch);
	}

    bool operator!=(const Rotation& other) const {
        return !(*this == other);
    }
    Rotation& operator=(const Rotation& other) {
        if (this != &other) {
            yaw = other.yaw;
            pitch = other.pitch;
        }
        return *this;
    }

    Rotation(const Rotation& other) : yaw(other.yaw), pitch(other.pitch) {}
	Rotation() = default;
};

using RotationPtr = Rotation*;

struct Position {
    enum POSITION_TYPE {
        RELATION,
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

struct PositionInformation {
    Position::POSITION_TYPE type_{};
    Position position_{};
};

using PositionInformationPtr = PositionInformation*;

struct RotationInformation {
    Rotation::ROTATION_TYPE type_{};
    Rotation rotation_{};
};

using RotationInformationPtr = RotationInformation*;

struct PlayerInformation {
    uint32_t playerId_{};
    PositionInformation posInfo_{};
    RotationInformation rotInfo_{};
};

using PlayerInformationPtr = PlayerInformation*;