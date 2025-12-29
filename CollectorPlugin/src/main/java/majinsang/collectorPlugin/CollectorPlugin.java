package majinsang.collectorPlugin;

import org.bukkit.Location;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;

public final class CollectorPlugin extends JavaPlugin {
    NetworkManager serverNetworkManager = new NetworkManager("127.0.0.1", 8986);
    NetworkManager agentNetworkManager = new NetworkManager("127.0.0.1", 7777);

    void PlayerInformationFunction() {
        for(Player player : Bukkit.getOnlinePlayers()) {
            try {
                // 패킷 0x01: 플레이어 위치/회전 정보
                PlayerInformation playerInfo = new PlayerInformation(player);
                serverNetworkManager.send(playerInfo.serialize());
                agentNetworkManager.send(playerInfo.serialize());

                // 패킷 0x02: 인벤토리 정보
                InventoryInformation invInfo = new InventoryInformation(player);
                serverNetworkManager.send(invInfo.serialize());
                agentNetworkManager.send(invInfo.serialize());

                // 패킷 0x03: 근처 블록 정보
                NearbyInformation nearbyInfo = new NearbyInformation(player);
                serverNetworkManager.send(nearbyInfo.serialize());
                agentNetworkManager.send(nearbyInfo.serialize());
            } catch (Exception e) {
                getLogger().severe("[ERROR] Failed to send packets for player " + player.getName());
                e.printStackTrace();
            }
        }
    }

    @Override
    public void onEnable() {
        // Plugin startup logic
        Bukkit.getScheduler().runTaskTimer(this, this::PlayerInformationFunction, 0L, 1L);
    }

    @Override
    public void onDisable() {
        // Plugin shutdown logic
        agentNetworkManager.close();
        serverNetworkManager.close();
    }
}

