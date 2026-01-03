package majinsang.collectorPlugin;

import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.jetbrains.annotations.NotNull;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.UUID;

/**
 * 건축 정보 패킷 (0x03)
 * - packetID: byte (0x03)
 * - id: uint32_t (4 bytes) - 플레이어 ID
 * - near_oak: byte (1 byte) - 나무 발견 여부 (0/1)
 * - oak_X: double (8 bytes) - 가장 가까운 나무 X
 * - oak_Y: double (8 bytes) - 가장 가까운 나무 Y
 * - oak_Z: double (8 bytes) - 가장 가까운 나무 Z
 * - near_crafting_table: byte (1 byte) - 작업대 발견 여부 (0/1)
 * - table_X: double (8 bytes) - 가장 가까운 작업대 X
 * - table_Y: double (8 bytes) - 가장 가까운 작업대 Y
 * - table_Z: double (8 bytes) - 가장 가까운 작업대 Z
 * 
 * 총 크기: 1 + 4 + 1 + 8*3 + 1 + 8*3 = 54 bytes
 */
class BuildingPacket extends GamePacket {
    private static final byte PACKET_ID = 0x03;
    private static final int SEARCH_RADIUS = 32; // 탐색 반경

    @NotNull private final UUID playerId;
    private final byte nearOak;
    private final double oakX;
    private final double oakY;
    private final double oakZ;
    private final byte nearCraftingTable;
    private final double tableX;
    private final double tableY;
    private final double tableZ;

    BuildingPacket(Player player) {
        this.playerId = player.getUniqueId();
        
        Location playerLoc = player.getLocation();
        World world = player.getWorld();
        
        // 가장 가까운 참나무 찾기
        Location nearestOak = findNearestBlock(world, playerLoc, 
            Material.OAK_LOG, Material.DARK_OAK_LOG, Material.SPRUCE_LOG,
            Material.BIRCH_LOG, Material.JUNGLE_LOG, Material.ACACIA_LOG);
        
        if (nearestOak != null) {
            this.nearOak = 1;
            this.oakX = nearestOak.getX();
            this.oakY = nearestOak.getY();
            this.oakZ = nearestOak.getZ();
        } else {
            this.nearOak = 0;
            this.oakX = 0.0;
            this.oakY = 0.0;
            this.oakZ = 0.0;
        }
        
        // 가장 가까운 작업대 찾기
        Location nearestTable = findNearestBlock(world, playerLoc, Material.CRAFTING_TABLE);
        
        if (nearestTable != null) {
            this.nearCraftingTable = 1;
            this.tableX = nearestTable.getX();
            this.tableY = nearestTable.getY();
            this.tableZ = nearestTable.getZ();
        } else {
            this.nearCraftingTable = 0;
            this.tableX = 0.0;
            this.tableY = 0.0;
            this.tableZ = 0.0;
        }
    }

    /**
     * 플레이어 주변에서 특정 블록 타입 중 가장 가까운 것 찾기
     */
    private Location findNearestBlock(World world, Location center, Material... materials) {
        Location nearest = null;
        double minDistance = Double.MAX_VALUE;
        
        int centerX = center.getBlockX();
        int centerY = center.getBlockY();
        int centerZ = center.getBlockZ();
        
        // Y 좌표 범위 제한 (성능 최적화)
        int minY = Math.max(world.getMinHeight(), centerY - SEARCH_RADIUS);
        int maxY = Math.min(world.getMaxHeight() - 1, centerY + SEARCH_RADIUS);
        
        for (int x = centerX - SEARCH_RADIUS; x <= centerX + SEARCH_RADIUS; x++) {
            for (int y = minY; y <= maxY; y++) {
                for (int z = centerZ - SEARCH_RADIUS; z <= centerZ + SEARCH_RADIUS; z++) {
                    Block block = world.getBlockAt(x, y, z);
                    Material blockType = block.getType();
                    
                    // 찾고자 하는 블록 타입인지 확인
                    for (Material targetMaterial : materials) {
                        if (blockType == targetMaterial) {
                            Location blockLoc = block.getLocation();
                            double distance = center.distanceSquared(blockLoc);
                            
                            if (distance < minDistance) {
                                minDistance = distance;
                                nearest = blockLoc;
                            }
                            break;
                        }
                    }
                }
            }
        }
        
        return nearest;
    }

    @Override
    protected byte getPacketID() {
        return PACKET_ID;
    }

    @Override
    public ByteBuffer serialize() {
        ByteBuffer buffer = ByteBuffer.allocate(55);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        // 패킷 ID
        buffer.put(PACKET_ID);

        // 플레이어 ID
        buffer.putInt(playerId.hashCode());

        // 참나무 정보
        buffer.put(nearOak);
        buffer.putDouble(oakX);
        buffer.putDouble(oakY);
        buffer.putDouble(oakZ);

        // 작업대 정보
        buffer.put(nearCraftingTable);
        buffer.putDouble(tableX);
        buffer.putDouble(tableY);
        buffer.putDouble(tableZ);

        return buffer;
    }
}
