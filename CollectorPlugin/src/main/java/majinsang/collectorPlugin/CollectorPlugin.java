package majinsang.collectorPlugin;

import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;


public final class CollectorPlugin extends JavaPlugin {

    @Override
    public void onEnable() {
        // Plugin startup logic
        NetworkManager nm = new NetworkManager("127.0.0.1", 8986);

        getLogger().info("Plugin loaded");

        Bukkit.getScheduler().runTaskTimerAsynchronously(this, () -> {
            for (Player player : Bukkit.getOnlinePlayers()) {
                String name = player.getName();
                byte[] nameBytes = name.getBytes(StandardCharsets.UTF_8);

                // 4(name length int) + nameBytes + 8*3(좌표)
                ByteBuffer buf = ByteBuffer.allocate(4 + nameBytes.length + 24).order(ByteOrder.LITTLE_ENDIAN);

                // UTF-8 바이트 길이 전송
                buf.putInt(nameBytes.length);

                // 현재 position에서 그대로 추가
                buf.put(nameBytes);

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
