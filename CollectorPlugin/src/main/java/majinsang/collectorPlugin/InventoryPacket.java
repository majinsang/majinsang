package majinsang.collectorPlugin;

import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.jetbrains.annotations.NotNull;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.UUID;

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
class InventoryPacket extends GamePacket {
    private static final byte PACKET_ID = 0x02;

    @NotNull private final UUID playerId;
    private final int logCount;
    private final int planksCount;
    private final int stickCount;
    private final int pickaxeCount;
    private final int craftingTableCount;

    InventoryPacket(Player player) {
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

    @Override
    protected byte getPacketID() {
        return PACKET_ID;
    }

    @Override
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
