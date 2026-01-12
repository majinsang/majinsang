package majinsang.collectorPlugin;

import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

public final class CollectorPlugin extends JavaPlugin {
    NetworkManager serverNetworkManager;
    NetworkManager agentNetworkManager;

    void InitConfig() {
        saveDefaultConfig();
        reloadConfig();

        String serverHost = getConfig().getString("server.host", "127.0.0.1");
        int serverPort = getConfig().getInt("server.port", 8986);

        String agentHost = getConfig().getString("agent.host", "127.0.0.1");
        int agentPort = getConfig().getInt("agent.port", 7777);

        getLogger().info("serverHost : " + serverHost + " serverPort : " + serverPort);
        getLogger().info("agentHost : " + agentHost + " agentPort : " + agentPort);

        serverNetworkManager = new NetworkManager(serverHost, serverPort);
        agentNetworkManager = new NetworkManager(agentHost, agentPort);
    }

    void PlayerInformationFunction() {
        for(Player player : Bukkit.getOnlinePlayers()) {
            InventoryPacket inventoryPacket = new InventoryPacket(player);
            BlockPacket blockPacket = new BlockPacket(player);
                         
//            serverNetworkManager.send(playerPacket.serialize());
//            serverNetworkManager.send(inventoryPacket.serialize());
//            serverNetworkManager.send(blockPacket.serialize());

            PlayerInformation pi = new PlayerInformation(player);
            serverNetworkManager.send(pi.serialize());
            agentNetworkManager.send(pi.serialize());
        }
    }

    @Override
    public void onEnable() {
        // Plugin startup logic
        InitConfig();
        Bukkit.getScheduler().runTaskTimer(this, this::PlayerInformationFunction, 0L, 1L);
    }

    @Override
    public void onDisable() {
        // Plugin shutdown logic
        agentNetworkManager.close();
        serverNetworkManager.close();
    }
}

