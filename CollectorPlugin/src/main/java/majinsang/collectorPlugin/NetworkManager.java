package majinsang.collectorPlugin;

import java.net.DatagramSocket;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.io.*;
import java.net.Socket;
import java.nio.ByteBuffer;


public class NetworkManager extends Thread implements AutoCloseable {
    private Socket clientSock_;
    private DataInputStream in_;
    private DataOutputStream out_;

    private DatagramSocket socket_;
    private InetAddress serverAddr_;
    private int serverPort_;

    private PositionListner positionListner_;

    public NetworkManager(String host, int port) {
        init(host, port);
    }

    @FunctionalInterface
    public interface PositionListner {
        void onReceive(Common.PlayerPosition pos);
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

    public void TcpClientInit(String host, int port) {
        try {
            clientSock_ = new Socket(host, port);
            in_ = new DataInputStream(new BufferedInputStream(clientSock_.getInputStream()));
            out_ = new DataOutputStream(new BufferedOutputStream(clientSock_.getOutputStream()));
        }catch(Exception e) {
            e.printStackTrace();
        }
    }

    public void setPositionListener(PositionListner listener) {
        this.positionListner_ = listener;
    }

    @Override
    public void run() {
        try {
            while(true) {
                double x = in_.readDouble();
                double y = in_.readDouble();
                double z = in_.readDouble();

                Common.PlayerPosition pos =  new Common.PlayerPosition(x, y, z);

                if(positionListner_ != null) positionListner_.onReceive(pos);

                out_.writeBoolean(true);
                out_.flush();
            }
        }catch(IOException e) {
            e.printStackTrace();
        }
    }

    public void SendUdpPosition(ByteBuffer data) {
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
