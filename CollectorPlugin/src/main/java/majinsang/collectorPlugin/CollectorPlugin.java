package majinsang.collectorPlugin;

import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;


public final class CollectorPlugin extends JavaPlugin {

    @Override
    public void onEnable() {
        // Plugin startup logic
        NetworkManager nm = new NetworkManager("127.0.0.1", 7777);

        getLogger().info("Plugin loaded");

        Bukkit.getScheduler().runTaskTimerAsynchronously(this, () -> {
            for (Player player : Bukkit.getOnlinePlayers()) {
                ByteBuffer buf = ByteBuffer.allocate(24).order(ByteOrder.LITTLE_ENDIAN);

                String test = String.valueOf(player.getX());
                player.sendMessage(test);

                test = String.valueOf(player.getY());
                player.sendMessage(test);

                test = String.valueOf(player.getZ());
                player.sendMessage(test);

                buf.putDouble(player.getX());
                buf.putDouble(player.getY());
                buf.putDouble(player.getZ());

                buf.flip();

                nm.send(buf);
            }

        }, 0L, 2L);
    }

    @Override
    public void onDisable() {
        // Plugin shutdown logic
    }
}
