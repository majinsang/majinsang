#pragma once

struct Rotation {
    enum ROTATION_TYPE : uint8_t {
        NONE,
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
    enum POSITION_TYPE : uint8_t {
        NONE,
        REL,
        ABS
    };

    static constexpr double THRESHOLD = 0.5;

    double x = 0.0;
    double y = 0.0;
    double z = 0.0;
    
    

    bool operator==(const Position& other) const {
        double dx = x - other.x;
        double dy = y - other.y;
        double dz = z - other.z;

        return (dx * dx + dy * dy + dz * dz) <= (THRESHOLD * THRESHOLD);
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

#pragma pack(push, 1)
struct PositionInformation {
    Position::POSITION_TYPE type_{};
    Position position_{};
};
#pragma pack(pop)

using PositionInformationPtr = PositionInformation*;

#pragma pack(push, 1)
struct RotationInformation {
    Rotation::ROTATION_TYPE type_{};
    Rotation rotation_{};
};
#pragma pack(pop)

using RotationInformationPtr = RotationInformation*;

#pragma pack(push, 1)
struct PlayerInformation {
    uint64_t playerId_{};
    Position position_{};
    Rotation rotation_{};
};
#pragma pack(pop)

using PlayerInformationPtr = PlayerInformation*;


namespace NETWORK {
    enum OPERATION : uint8_t {
        POSITION,
        ROTATION,
        ALL,
    };

#pragma pack(push, 1)
    struct CommandHeader {
        OPERATION opCode_{};
        PositionInformation targetPi_{};
        RotationInformation targetRi_{};
    };
#pragma pack(pop)

	using CommandHeaderPtr = CommandHeader*;
};
