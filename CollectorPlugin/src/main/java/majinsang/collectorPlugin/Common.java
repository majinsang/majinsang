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
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.jetbrains.annotations.NotNull;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.UUID;

enum OperationCode {
    POSITION,
    ROTATION,
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

/**
 * 인벤토리 정보 패킷 (0x02)
 * - packetID: byte (0x02)
 * - id: uint32_t (4 bytes) - 플레이어 ID
 * - log_count: uint32_t (4 bytes) - 원목 개수
 * - planks_count: uint32_t (4 bytes) - 판자 개수
 * - stick_count: uint32_t (4 bytes) - 막대기 개수
 * - pickage_count: uint32_t (4 bytes) - 곡괭이 개수
 * - crafting_table_count: uint32_t (4 bytes) - 작업대 개수
 *
 * 총 크기: 1 + 4*6 = 25 bytes
 */

class InventroyInformation {
    @NotNull private final UUID playerId;
    private final int logCount;
    private final int planksCount;
    private final int stickCount;
    private final int pickaxeCount;
    private final int craftingTableCount;

    InventroyInformation(Player player) {
        this.playerId = player.getUniqueId();

        // 인벤토리 아이템 카운트
        ItemStack[] contents = player.getInventory().getContents();

        int logs = 0;
        int planks = 0;
        int sticks = 0;
        int pickaxes = 0;
        int craftingTables = 0;

        for (ItemStack item : contents) {
            if (item == null) continue;

            Material type = item.getType();
            int amount = item.getAmount();

            // 원목 (모든 종류의 원목)
            if (type.name().contains("LOG") && !type.name().contains("STRIPPED")) {
                logs += amount;
            }
            // 판자 (모든 종류의 판자)
            else if (type.name().contains("PLANKS")) {
                planks += amount;
            }
            // 막대기
            else if (type == Material.STICK) {
                sticks += amount;
            }
            // 곡괭이 (모든 종류의 곡괭이)
            else if (type.name().contains("PICKAXE")) {
                pickaxes += amount;
            }
            // 작업대
            else if (type == Material.CRAFTING_TABLE) {
                craftingTables += amount;
            }
        }

        this.logCount = logs;
        this.planksCount = planks;
        this.stickCount = sticks;
        this.pickaxeCount = pickaxes;
        this.craftingTableCount = craftingTables;
    }

    protected byte getPacketID() {
        return PACKET_ID;
    }

    public ByteBuffer serialize() {
        ByteBuffer buffer = ByteBuffer.allocate(25);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        // 패킷 ID
        buffer.put(PACKET_ID);

        // 플레이어 ID
        buffer.putInt(playerId.hashCode());

        // 인벤토리 개수
        buffer.putInt(logCount);
        buffer.putInt(planksCount);
        buffer.putInt(stickCount);
        buffer.putInt(pickaxeCount);
        buffer.putInt(craftingTableCount);

        return buffer;
    }
}

