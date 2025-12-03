import socket
import time
import sys
import random

TARGET_PORT = 16261
PACKET_COUNT = 200
RATE_DELAY = 0.005

def resolve_hostname(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{hostname}'. Check your DDNS settings or internet connection.")
        sys.exit(1)

def start_load_test():
    if len(sys.argv) > 1:
        target_host = sys.argv[1]
    else:
        raise ValueError("Usage: python load.py <target_host>")

    print(f"Resolving {target_host}...")
    target_ip = resolve_hostname(target_host)

    print(f"--- Starting DDoS Simulation ---")
    print(f"Target Host: {target_host}")
    print(f"Target IP:   {target_ip}:{TARGET_PORT}")
    print(f"Sending {PACKET_COUNT} packets with {RATE_DELAY}s delay...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        for i in range(PACKET_COUNT):
            message = f"LoadTestPacket_{i}".encode()
            sock.sendto(message, (target_ip, TARGET_PORT))
            
            if i % 50 == 0:
                print(f"Sent {i} packets...")
                
            # TODO: poisson process with exp()
            time.sleep(RATE_DELAY)
            
        print(f"--- Simulation Complete ---")
        print("If successful, the target proxy should have logged a blocking event.")
        
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_load_test()
