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
            Location loc = player.getLocation();

            PlayerInformation pi = new PlayerInformation(player);

            serverNetworkManager.send(pi.serialize());
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

