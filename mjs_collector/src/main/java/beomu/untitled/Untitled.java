package beomu.untitled;

import com.mojang.brigadier.Command;
import com.mojang.brigadier.tree.LiteralCommandNode;
import io.papermc.paper.command.brigadier.CommandSourceStack;
import io.papermc.paper.command.brigadier.Commands;
import io.papermc.paper.plugin.lifecycle.event.types.LifecycleEvents;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.Listener;
import org.bukkit.plugin.java.JavaPlugin;

import java.nio.ByteBuffer;


public final class Untitled extends JavaPlugin implements Listener {

    private PlayerInfoManager infoManager;

    private LiteralCommandNode<CommandSourceStack> TestCommand() {
        return Commands.literal("test").executes(ctx -> {
            if ((ctx.getSource().getSender() instanceof Player player)) {
                PlayerInfoManager.PlayerData pd = infoManager.getPlayerData(player);

                player.sendMessage("§a현재 월드 시간: " + pd.getWorldTime());
                player.sendMessage("§a현재 바이옴: " + pd.getCurrentBiome());
                player.sendMessage("§a현재 블럭 수: " + pd.getVisibleBlocks());
                player.sendMessage("§a현재 인벤토리:" + pd.getInventory());
                player.sendMessage("§a현재 엔티티:" + pd.getVisibleEntities());
            }


            return Command.SINGLE_SUCCESS;
        }).build();
    }

    @Override
    public void onEnable() {
        getLogger().info("[Untitled] Plugin Enabled");
        infoManager = new PlayerInfoManager(this);

        getLifecycleManager().registerEventHandler(LifecycleEvents.COMMANDS, cmd -> {
            cmd.registrar().register(TestCommand());
        });

        NetworkManager nm = new NetworkManager("127.0.0.1", 8986);



        Bukkit.getScheduler().runTaskTimerAsynchronously(this, () -> {

            for (Player player : Bukkit.getOnlinePlayers()) {
                ByteBuffer buf = ByteBuffer.allocate(24);

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
        getLogger().info("[Untitled] Plugin Disabled");
    }
}
