package majinsang.collectorPlugin;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

public class NetworkManager implements AutoCloseable {

    private final DatagramSocket socket;
    private final InetAddress serverAddr;
    private final int serverPort;

    public NetworkManager(String host, int port) {
        try {
            this.socket = new DatagramSocket();
            this.serverAddr = InetAddress.getByName(host);
            this.serverPort = port;
        } catch (Exception e) {
            throw new RuntimeException("UDP init failed", e);
        }
    }

    /**
     * PlayerInformation UDP 전송
     */
    public void send(ByteBuffer buffer) {
        try {
            buffer.flip(); // write → read 모드 전환

            byte[] payload = new byte[buffer.remaining()];
            buffer.get(payload);

            DatagramPacket packet = new DatagramPacket(
                    payload,
                    payload.length,
                    serverAddr,
                    serverPort
            );

            socket.send(packet);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public void close() {
        socket.close();
    }
}
