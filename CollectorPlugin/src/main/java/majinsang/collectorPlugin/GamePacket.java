package majinsang.collectorPlugin;

import java.nio.ByteBuffer;

/**
 * 추상 게임 패킷 클래스
 * 모든 패킷은 이 클래스를 상속받아 구현
 */
abstract class GamePacket {
    /**
     * 패킷 ID 반환 (0x01, 0x02, 0x03 등)
     */
    protected abstract byte getPacketID();

    /**
     * 패킷 데이터를 직렬화하여 ByteBuffer로 반환
     */
    public abstract ByteBuffer serialize();
}
