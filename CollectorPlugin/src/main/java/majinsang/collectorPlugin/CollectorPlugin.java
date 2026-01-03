package majinsang.collectorPlugin;

import org.bukkit.Location;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;

public final class CollectorPlugin extends JavaPlugin {
    NetworkManager serverNetworkManager = new NetworkManager("127.0.0.1", 8888);
    NetworkManager agentNetworkManager = new NetworkManager("127.0.0.1", 7777);

    void PlayerInformationFunction() {
        for(Player player : Bukkit.getOnlinePlayers()) {
            // 서버(8888)로는 새로운 프로토콜의 3가지 패킷 전송
            PlayerPacket playerPacket = new PlayerPacket(player);
            InventoryPacket inventoryPacket = new InventoryPacket(player);
            BlockPacket blockPacket = new BlockPacket(player);
            
            serverNetworkManager.send(playerPacket.serialize());
            serverNetworkManager.send(inventoryPacket.serialize());
            serverNetworkManager.send(blockPacket.serialize());

            // 에이전트(7777)로는 기존 PlayerInformation 전송
            PlayerInformation pi = new PlayerInformation(player);
            agentNetworkManager.send(pi.serialize());
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

