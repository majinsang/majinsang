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
                print("Usage:")
                print("  키보드: <KEY> <DURATION>")
                print("    예시: W 2  (3초 후 W키를 2초 동안 누름)")
                print("    키: W, A, S, D, X (space)")
                print("  마우스 이동: M <DX> <DY>")
                print("    예시: M 10 -5  (오른쪽 10, 위로 5)")
                print("  마우스 클릭: ML <DURATION> 또는 MR <DURATION>")
                print("    예시: ML 0.5  (좌클릭 0.5초)")
                print("    예시: MR 1  (우클릭 1초)\n")
                
                while True:
                    try:
                        user_input = input("> ").strip()
                        if not user_input:
                            continue
                        
                        parts = user_input.split()
                        if len(parts) < 2:
                            print("Error: 형식이 잘못되었습니다.")
                            continue
                        
                        cmd = parts[0].upper()
                        
                        if cmd == 'M':
                            if len(parts) != 3:
                                print("Error: 형식이 잘못되었습니다. 예시: M 10 -5")
                                continue
                            try:
                                dx = int(parts[1])
                                dy = int(parts[2])
                            except ValueError:
                                print("Error: 이동량은 정수여야 합니다.")
                                continue
                            
                            print(f"3초 후 마우스를 ({dx}, {dy})만큼 이동합니다...")
                            for i in range(3, 0, -1):
                                print(f"{i}...")
                                time.sleep(1)
                            print("실행!")
                            
                            send_command(conn, f"M_M_{dx}_{dy}")
                            print(f"완료: 마우스 이동 ({dx}, {dy})\n")
                            continue
                        
                        if cmd in ['ML', 'MR']:
                            if len(parts) != 2:
                                print("Error: 형식이 잘못되었습니다. 예시: ML 0.5")
                                continue
                            try:
                                duration = float(parts[1])
                            except ValueError:
                                print("Error: 시간은 숫자여야 합니다.")
                                continue
                            
                            button = 'L' if cmd == 'ML' else 'R'
                            button_name = '좌클릭' if cmd == 'ML' else '우클릭'
                            
                            print(f"3초 후 {button_name}을 {duration}초 동안 누릅니다...")
                            for i in range(3, 0, -1):
                                print(f"{i}...")
                                time.sleep(1)
                            print("실행!")
                            
                            send_command(conn, f"M_{button}_Down")
                            time.sleep(duration)
                            send_command(conn, f"M_{button}_Up")
                            print(f"완료: {button_name} {duration}초\n")
                            continue
                        
                        if len(parts) != 2:
                            print("Error: 형식이 잘못되었습니다. 예시: W 2")
                            continue
                        
                        key = cmd
                        try:
                            duration = float(parts[1])
                        except ValueError:
                            print("Error: 시간은 숫자여야 합니다.")
                            continue
                        
                        valid_keys = ['W', 'A', 'S', 'D', 'X']
                        if key not in valid_keys:
                            print(f"Error: 유효하지 않은 키입니다. 사용 가능: {', '.join(valid_keys)}")
                            continue
                        
                        print(f"3초 후 {key} 키를 {duration}초 동안 누릅니다...")
                        for i in range(3, 0, -1):
                            print(f"{i}...")
                            time.sleep(1)
                        print("실행!")
                        
                        send_command(conn, f"{key}_DOWN")
                        
                        time.sleep(duration)
                        
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
