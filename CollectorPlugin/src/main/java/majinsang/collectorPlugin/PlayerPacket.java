package majinsang.collectorPlugin;

import org.bukkit.entity.Player;
import org.jetbrains.annotations.NotNull;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.UUID;

/**
 * 플레이어 정보 패킷 (0x01)
 * - packetID: byte (0x01)
 * - id: uint32_t (4 bytes) - 플레이어 ID
 * - X: double (8 bytes) - Current X
 * - Y: double (8 bytes) - Current Y
 * - Z: double (8 bytes) - Current Z
 * - YAW: double (8 bytes) - Current Yaw
 * - PITCH: double (8 bytes) - Current Pitch
 * 
 * 총 크기: 1 + 4 + 8*5 = 45 bytes
 */
class PlayerPacket extends GamePacket {
    private static final byte PACKET_ID = 0x01;

    @NotNull private final UUID playerId;
    private final double x;
    private final double y;
    private final double z;
    private final double yaw;
    private final double pitch;

    PlayerPacket(Player player) {
        this.playerId = player.getUniqueId();
        this.x = player.getLocation().getX();
        this.y = player.getLocation().getY();
        this.z = player.getLocation().getZ();
        this.yaw = player.getLocation().getYaw();
        this.pitch = player.getLocation().getPitch();
    }

    @Override
    protected byte getPacketID() {
        return PACKET_ID;
    }

    @Override
    public ByteBuffer serialize() {
        ByteBuffer buffer = ByteBuffer.allocate(45);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        // 패킷 ID
        buffer.put(PACKET_ID);

        // 플레이어 ID (UUID → uint32_t로 변환)
        buffer.putInt(playerId.hashCode());

        // 위치 정보
        buffer.putDouble(x);
        buffer.putDouble(y);
        buffer.putDouble(z);

        // 회전 정보
        buffer.putDouble(yaw);
        buffer.putDouble(pitch);

        return buffer;
    }
}
