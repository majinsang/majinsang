import socket
import time

def send_command(conn, command):
    """클라이언트에 명령 전송"""
    conn.sendall(command.encode() + b'\n')
    print(f"Sent: {command}")
    time.sleep(0.1)

def main():
    # 서버 설정
    host = '0.0.0.0'  # 모든 인터페이스에서 수신
    port = 8888
    
    print("=== Python Command Server ===")
    print(f"Starting server on {host}:{port}...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((host, port))
            server_sock.listen(1)
            
            print(f"Server listening on port {port}")
            print("Waiting for agent connection...\n")
            
            conn, addr = server_sock.accept()
            with conn:
                print(f"Agent connected from {addr}\n")
                print("=== Manual Control Mode ===")
                print("Usage: <KEY> <DURATION>")
                print("Example: W 2  (3초 후 W키를 2초 동안 누름)")
                print("Keys: W, A, S, D, X (space)\n")
                
                # 수동 입력 모드
                while True:
                    try:
                        user_input = input("> ").strip()
                        if not user_input:
                            continue
                        
                        # 입력 파싱
                        parts = user_input.split()
                        if len(parts) != 2:
                            print("Error: 형식이 잘못되었습니다. 예시: W 2")
                            continue
                        
                        key = parts[0].upper()
                        try:
                            duration = float(parts[1])
                        except ValueError:
                            print("Error: 시간은 숫자여야 합니다.")
                            continue
                        
                        # 유효한 키 확인
                        valid_keys = ['W', 'A', 'S', 'D', 'X']
                        if key not in valid_keys:
                            print(f"Error: 유효하지 않은 키입니다. 사용 가능: {', '.join(valid_keys)}")
                            continue
                        
                        # 3초 카운트다운
                        print(f"3초 후 {key} 키를 {duration}초 동안 누릅니다...")
                        for i in range(3, 0, -1):
                            print(f"{i}...")
                            time.sleep(1)
                        print("실행!")
                        
                        # 키 누르기
                        send_command(conn, f"{key}_DOWN")
                        
                        # 지정된 시간 동안 대기
                        time.sleep(duration)
                        
                        # 키 떼기
                        send_command(conn, f"{key}_UP")
                        print(f"완료: {key} 키를 {duration}초 동안 눌렀습니다.\n")
                        
                    except KeyboardInterrupt:
                        print("\n\nInterrupted by user. Closing connection...")
                        break
                        
                print("\nConnection closed.")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
