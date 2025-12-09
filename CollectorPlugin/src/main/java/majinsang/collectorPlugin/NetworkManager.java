package majinsang.collectorPlugin;

import java.net.DatagramSocket;
import java.net.DatagramPacket;
import java.net.InetAddress;

import java.nio.ByteBuffer;
import java.util.ArrayList;

public class NetworkManager implements AutoCloseable {
    private DatagramSocket socket_;
    private InetAddress serverAddr_;
    private int serverPort_;

    public NetworkManager(String host, int port) {
        init(host, port);
    }

    public void init(String host, int port) {
        try {
            socket_ = new DatagramSocket();
            serverAddr_ = InetAddress.getByName(host);
            serverPort_ = port;
        }catch(Exception e) {
            e.printStackTrace();
        }
    }

    public void send(ByteBuffer data) {
        try {
            DatagramPacket packet = new DatagramPacket(data.array(), data.remaining(), serverAddr_, serverPort_);
            socket_.send(packet);
        }catch(Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public void close() {
        try {
            socket_.close();
        }catch(Exception e) {
            e.printStackTrace();
        }
    }
}
