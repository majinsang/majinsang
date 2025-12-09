package majinsang.collectorPlugin;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.Biome;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.*;

public class PlayerInfoManager {
    private final JavaPlugin plugin;
    private final Map<UUID, PlayerData> dataMap = new HashMap<>();

    public PlayerInfoManager(JavaPlugin plugin) {
        this.plugin = plugin;
        startUpdater();
    }

    private void startUpdater() {
        // 1초마다 플레이어 데이터 갱신
        Bukkit.getScheduler().runTaskTimer(plugin, () -> {
            for (Player player : Bukkit.getOnlinePlayers()) {
                PlayerData data = dataMap.computeIfAbsent(player.getUniqueId(), k -> new PlayerData(player));

                // 인벤토리
                data.setInventory(player.getInventory().getContents());

                // 주변 엔티티
                data.setVisibleEntities(player.getNearbyEntities(10, 10, 10));

                // 주변 블럭 (반경 5)
                data.setVisibleBlocks(getNearbyBlocks(player, 5));

                // 바이옴
                World world = player.getWorld();
                data.setCurrentBiome(world.getBiome(player.getLocation().getBlockX(),
                        player.getLocation().getBlockY(),
                        player.getLocation().getBlockZ()));

                // 월드 시간
                data.setWorldTime(world.getTime());
            }
        }, 0L, 20L); // 20틱 = 1초
    }

    private List<Block> getNearbyBlocks(Player player, int radius) {
        List<Block> blocks = new ArrayList<>();
        Location loc = player.getLocation();
        World world = player.getWorld();

        for (int x = loc.getBlockX() - radius; x <= loc.getBlockX() + radius; x++) {
            for (int y = loc.getBlockY() - radius; y <= loc.getBlockY() + radius; y++) {
                for (int z = loc.getBlockZ() - radius; z <= loc.getBlockZ() + radius; z++) {
                    blocks.add(world.getBlockAt(x, y, z));
                }
            }
        }
        return blocks;
    }

    public PlayerData getPlayerData(Player player) {
        return dataMap.get(player.getUniqueId());
    }

    // 내부 클래스: PlayerData
    public class PlayerData {
        private final Player player;
        private List<Block> visibleBlocks = new ArrayList<>();
        private List<Entity> visibleEntities = new ArrayList<>();
        private ItemStack[] inventory = new ItemStack[36];
        private Biome currentBiome;
        private long worldTime;

        public PlayerData(Player player) {
            this.player = player;
        }

        // Getter / Setter
        public Player getPlayer() { return player; }

        public List<Block> getVisibleBlocks() { return visibleBlocks; }
        public void setVisibleBlocks(List<Block> visibleBlocks) { this.visibleBlocks = visibleBlocks; }

        public List<Entity> getVisibleEntities() { return visibleEntities; }
        public void setVisibleEntities(List<Entity> visibleEntities) { this.visibleEntities = visibleEntities; }

        public ItemStack[] getInventory() { return inventory; }
        public void setInventory(ItemStack[] inventory) { this.inventory = inventory; }

        public Biome getCurrentBiome() { return currentBiome; }
        public void setCurrentBiome(Biome currentBiome) { this.currentBiome = currentBiome; }

        public long getWorldTime() { return worldTime; }
        public void setWorldTime(long worldTime) { this.worldTime = worldTime; }
    }
}
