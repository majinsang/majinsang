package majinsang.collectorPlugin;

import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.Location;
import org.bukkit.block.Block;
import org.jetbrains.annotations.NotNull;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/*
 * =====================================================
 * Updated Protocol - 2025.12.29
 * - 3 Packet Types: Player(0x01), Inventory(0x02), Nearby(0x03)
 * - Using uint32_t ID instead of UUID
 * =====================================================
 */

/* ================= PACKET 0x01: PLAYER INFORMATION (45 bytes) ================= */
class PlayerInformation {
    private static final byte PACKET_ID = 0x01;
    
    private final int playerId;
    private final double x;
    private final double y;
    private final double z;
    private final double yaw;
    private final double pitch;

    public PlayerInformation(Player player) {
        // UUID를 int로 변환 (해시 사용)
        this.playerId = player.getUniqueId().hashCode();
        this.x = player.getX();
        this.y = player.getY();
        this.z = player.getZ();
        this.yaw = player.getYaw();
        this.pitch = player.getPitch();
    }

    public ByteBuffer serialize() {
        ByteBuffer buffer = ByteBuffer.allocate(45);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        buffer.put(PACKET_ID);      // 1 byte
        buffer.putInt(playerId);    // 4 bytes
        buffer.putDouble(x);        // 8 bytes
        buffer.putDouble(y);        // 8 bytes
        buffer.putDouble(z);        // 8 bytes
        buffer.putDouble(yaw);      // 8 bytes
        buffer.putDouble(pitch);    // 8 bytes

        return buffer;
    }
}

/* ================= PACKET 0x02: INVENTORY INFORMATION (25 bytes) ================= */
class InventoryInformation {
    private static final byte PACKET_ID = 0x02;
    
    private final int playerId;
    private final int logCount;
    private final int planksCount;
    private final int stickCount;
    private final int pickaxeCount;
    private final int craftingTableCount;

    public InventoryInformation(Player player) {
        this.playerId = player.getUniqueId().hashCode();
        this.logCount = countItems(player, Material.OAK_LOG);
        this.planksCount = countItems(player, Material.OAK_PLANKS);
        this.stickCount = countItems(player, Material.STICK);
        this.pickaxeCount = countPickaxes(player);
        this.craftingTableCount = countItems(player, Material.CRAFTING_TABLE);
    }

    private int countItems(Player player, Material material) {
        int count = 0;
        for (ItemStack item : player.getInventory().getContents()) {
            if (item != null && item.getType() == material) {
                count += item.getAmount();
            }
        }
        return count;
    }

    private int countPickaxes(Player player) {
        int count = 0;
        for (ItemStack item : player.getInventory().getContents()) {
            if (item != null && item.getType().name().endsWith("_PICKAXE")) {
                count += item.getAmount();
            }
        }
        return count;
    }

    public ByteBuffer serialize() {
        ByteBuffer buffer = ByteBuffer.allocate(25);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        buffer.put(PACKET_ID);              // 1 byte
        buffer.putInt(playerId);            // 4 bytes
        buffer.putInt(logCount);            // 4 bytes
        buffer.putInt(planksCount);         // 4 bytes
        buffer.putInt(stickCount);          // 4 bytes
        buffer.putInt(pickaxeCount);        // 4 bytes
        buffer.putInt(craftingTableCount);  // 4 bytes

        return buffer;
    }
}

/* ================= PACKET 0x03: NEARBY INFORMATION (51 bytes) ================= */
class NearbyInformation {
    private static final byte PACKET_ID = 0x03;
    
    private final int playerId;
    private final byte nearOak;
    private final double oakX;
    private final double oakY;
    private final double oakZ;
    private final byte nearCraftingTable;
    private final double tableX;
    private final double tableY;
    private final double tableZ;

    public NearbyInformation(Player player) {
        this.playerId = player.getUniqueId().hashCode();
        
        // 임시 변수 사용
        byte tempNearOak;
        double tempOakX, tempOakY, tempOakZ;
        byte tempNearCraftingTable;
        double tempTableX, tempTableY, tempTableZ;
        
        try {
            // 가장 가까운 오크나무 찾기 (반경 20블록)
            Location oakLoc = findNearestBlock(player, Material.OAK_LOG, 20);
            if (oakLoc != null) {
                tempNearOak = 1;
                tempOakX = oakLoc.getX();
                tempOakY = oakLoc.getY();
                tempOakZ = oakLoc.getZ();
            } else {
                tempNearOak = 0;
                tempOakX = 0.0;
                tempOakY = 0.0;
                tempOakZ = 0.0;
            }
            
            // 가장 가까운 작업대 찾기 (반경 20블록)
            Location tableLoc = findNearestBlock(player, Material.CRAFTING_TABLE, 20);
            if (tableLoc != null) {
                tempNearCraftingTable = 1;
                tempTableX = tableLoc.getX();
                tempTableY = tableLoc.getY();
                tempTableZ = tableLoc.getZ();
            } else {
                tempNearCraftingTable = 0;
                tempTableX = 0.0;
                tempTableY = 0.0;
                tempTableZ = 0.0;
            }
        } catch (Exception e) {
            System.err.println("[NearbyInformation ERROR] " + e.getMessage());
            e.printStackTrace();
            // 실패 시 기본값
            tempNearOak = 0;
            tempOakX = 0.0;
            tempOakY = 0.0;
            tempOakZ = 0.0;
            tempNearCraftingTable = 0;
            tempTableX = 0.0;
            tempTableY = 0.0;
            tempTableZ = 0.0;
        }
        
        // final 필드에 한 번만 할당
        this.nearOak = tempNearOak;
        this.oakX = tempOakX;
        this.oakY = tempOakY;
        this.oakZ = tempOakZ;
        this.nearCraftingTable = tempNearCraftingTable;
        this.tableX = tempTableX;
        this.tableY = tempTableY;
        this.tableZ = tempTableZ;
    }

    private Location findNearestBlock(Player player, Material material, int radius) {
        Location playerLoc = player.getLocation();
        Location nearest = null;
        double minDistance = Double.MAX_VALUE;

        int px = playerLoc.getBlockX();
        int py = playerLoc.getBlockY();
        int pz = playerLoc.getBlockZ();

        for (int x = px - radius; x <= px + radius; x++) {
            for (int y = Math.max(py - radius, player.getWorld().getMinHeight()); 
                 y <= Math.min(py + radius, player.getWorld().getMaxHeight()); y++) {
                for (int z = pz - radius; z <= pz + radius; z++) {
                    Block block = player.getWorld().getBlockAt(x, y, z);
                    if (block.getType() == material) {
                        double distance = playerLoc.distance(block.getLocation());
                        if (distance < minDistance) {
                            minDistance = distance;
                            nearest = block.getLocation();
                        }
                    }
                }
            }
        }
        return nearest;
    }

    public ByteBuffer serialize() {
        ByteBuffer buffer = ByteBuffer.allocate(55);  // 1+4+1+24+1+24 = 55 bytes
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        buffer.put(PACKET_ID);              // 1 byte
        buffer.putInt(playerId);            // 4 bytes
        buffer.put(nearOak);                // 1 byte
        buffer.putDouble(oakX);             // 8 bytes
        buffer.putDouble(oakY);             // 8 bytes
        buffer.putDouble(oakZ);             // 8 bytes
        buffer.put(nearCraftingTable);      // 1 byte
        buffer.putDouble(tableX);           // 8 bytes
        buffer.putDouble(tableY);           // 8 bytes
        buffer.putDouble(tableZ);           // 8 bytes

        return buffer;
    }
}
