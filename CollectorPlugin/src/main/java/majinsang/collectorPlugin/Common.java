package majinsang.collectorPlugin;

/*
 * =====================================================
 * Player Model
 * - Visitor Pattern
 * - Operation Code
 * - JSON-like Serialization
 * =====================================================
 */

/* ================= OPERATION CODE ================= */

import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.jetbrains.annotations.NotNull;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.UUID;

enum OperationCode {
    POSITION,
    ROTATION
}

/* ================= POSITION ================= */
class Position {
    private final double x;
    private final double y;
    private final double z;

    public Position(double x, double y, double z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    public double GetX() { return x; };
    public double GetY() { return y; };
    public double GetZ() { return z; };

    public String serialize() {
        return String.format(
                "\"position\":{" +
                        "\"x\":%.3f,\"y\":%.3f,\"z\":%.3f}",
                x, y, z
        );
    }
}

/* ================= ROTATION ================= */
class Rotation {
    private final double yaw;
    private final double pitch;

    public Rotation(double yaw, double pitch) {
        this.yaw = yaw;
        this.pitch = pitch;
    }

    public double GetYaw() { return yaw; };
    public double GetPitch() { return pitch; };

    public String serialize() {
        return String.format(
                "\"rotation\":{" +
                        "\"yaw\":%.3f,\"pitch\":%.3f}",
                yaw, pitch
        );
    }
}

class PlayerInformation {

    @NotNull UUID playerId_;
    Position pi_;
    Rotation ri_;

    PlayerInformation(Player player) {
        playerId_ = player.getUniqueId();
        pi_ = new Position(player.getX(), player.getY(), player.getZ());
        ri_ = new Rotation(player.getYaw(), player.getPitch());
    }

    public ByteBuffer serialize() {
        ByteBuffer buffer = ByteBuffer.allocate(48);
        buffer.order(ByteOrder.LITTLE_ENDIAN); // C/C++ 연동 기준

        // UUID → 8바이트 (long)
        buffer.putLong(playerId_.getMostSignificantBits());

        buffer.putDouble(pi_.GetX());
        buffer.putDouble(pi_.GetY());
        buffer.putDouble(pi_.GetZ());

        buffer.putDouble(ri_.GetYaw());
        buffer.putDouble(ri_.GetPitch());

        return buffer;
    }
}
