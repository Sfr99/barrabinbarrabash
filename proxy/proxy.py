import socket
import threading
import logging
import sys
import time
import requests
import json

LISTEN_IP = "0.0.0.0"
TARGET_IP = "127.0.0.1"
LOG_FILE = "traffic.log"

BACKEND_BASE_URL = "http://127.0.0.1:5000"

DDOS_PPS_LIMIT = 50
DDOS_BLOCK_TIME = 30


PORT_MAPPINGS = {
    16261: 16300
}


start_src = 16262
start_dst = 16301
count = 11
for i in range(count):
    PORT_MAPPINGS[start_src + i] = start_dst + i


rate_lock = threading.Lock()
ip_traffic_stats = {}
blocked_ips = {}


logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def send_backend_alerts(ip, pps_rate):
    """
    Sends the specific API calls to the backend when an attack is detected.
    1. /ban
    2. /event
    """
    headers = {'Content-Type': 'application/json'}

    ban_payload = {
        "ip": ip,
        "reason": f"DoS Flood detected (Rate: {pps_rate} pps)"
    }

    event_payload = {
        "ip": ip,
        "action": "blocked",
        "description": f"High traffic flood detected: {pps_rate} packets/sec",
        "is_attack": True
    }

    try:
        url_ban = f"{BACKEND_BASE_URL}/ban"
        logging.debug(f"[API] Sending BAN request to {url_ban}...")
        requests.post(url_ban, params=ban_payload, timeout=2)

        url_event = f"{BACKEND_BASE_URL}/event"
        logging.debug(f"[API] Sending EVENT request to {url_event}...")
        requests.post(url_event, params=event_payload, timeout=2)

        logging.info(f"[API] ✅ Backend notified for IP {ip}")

    except requests.exceptions.ConnectionError:
        logging.error(f"[API] ❌ Connection Failed: Could not reach backend at {BACKEND_BASE_URL}")
    except Exception as e:
        logging.error(f"[API] ❌ Failed to send alerts: {e}")

def check_ddos(ip):
    """
    Checks if an IP is flooding. Returns True if traffic is ALLOWED.
    Returns False if traffic should be BLOCKED.
    """
    current_time = time.time()

    with rate_lock:
        if ip in blocked_ips:
            if current_time < blocked_ips[ip]:
                return False
            else:
                del blocked_ips[ip]
            logging.info(f"[DDoS] Unblocking IP: {ip}")

        stats = ip_traffic_stats.get(ip, {'count': 0, 'timestamp': int(current_time)})

        if int(current_time) > int(stats['timestamp']):
            stats['count'] = 1
            stats['timestamp'] = int(current_time)
        else:
            stats['count'] += 1

        ip_traffic_stats[ip] = stats

        if stats['count'] > DDOS_PPS_LIMIT:
            logging.warning(f"[DDoS] ⚠ FLOOD DETECTED from {ip}! Rate: {stats['count']} pps. Blocking for {DDOS_BLOCK_TIME}s.")
            blocked_ips[ip] = current_time + DDOS_BLOCK_TIME
            threading.Thread(target=send_backend_alerts, args=(ip, stats['count'])).start()
            return False

    return True

def handle_udp(src_port, dst_port):
    """Bi-directional UDP Proxy with DDoS Protection."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, src_port))

    known_client = None
    server_addr = (TARGET_IP, dst_port)

    logging.info(f"[UDP] Listening on {LISTEN_IP}:{src_port} <-> {TARGET_IP}:{dst_port}")

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            ip_source = addr[0]

            if ip_source == TARGET_IP and addr[1] == dst_port:
                # SERVER -> CLIENT
                if known_client:
                    sock.sendto(data, known_client)
            else:
                # CLIENT -> SERVER
                if not check_ddos(ip_source):
                    logging.debug(f"[DDoS] Dropped packet from {ip_source}")
                    continue

                known_client = addr
                sock.sendto(data, server_addr)

    except Exception as e:
        logging.error(f"[UDP] Error on port {src_port}: {e}")
    finally:
        sock.close()

def forward_tcp_data(source, destination, direction_label):
    try:
        while True:
            data = source.recv(4096)
            if not data: break
            destination.sendall(data)
    except:
        pass
    finally:
        source.close()
        destination.close()

def handle_tcp_client(client_socket, src_port, dst_port):
    try:
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect((TARGET_IP, dst_port))

        logging.info(f"[TCP] New Connection: {LISTEN_IP}:{src_port} -> {TARGET_IP}:{dst_port}")

        t1 = threading.Thread(target=forward_tcp_data, args=(client_socket, target_socket, "->"))
        t2 = threading.Thread(target=forward_tcp_data, args=(target_socket, client_socket, "<-"))
        t1.start()
        t2.start()
    except Exception as e:
        logging.error(f"[TCP] Connection failed on port {src_port}: {e}")
        client_socket.close()

def handle_tcp(src_port, dst_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((LISTEN_IP, src_port))
        sock.listen(5)
        while True:
            client_sock, addr = sock.accept()
            if not check_ddos(addr[0]):
                client_sock.close()
                continue

            client_thread = threading.Thread(target=handle_tcp_client, args=(client_sock, src_port, dst_port))
            client_thread.daemon = True
            client_thread.start()
    except Exception as e:
        logging.error(f"[TCP] Error on port {src_port}: {e}")
    finally:
        sock.close()

def main():
    print(f"--- Traffic Forwarder V2.2 (Backend Reporting) Started ---")
    print(f"Logging to: {LOG_FILE}")
    print(f"Reporting Bans to: {BACKEND_BASE_URL}")
    print(f"DDoS Limit: {DDOS_PPS_LIMIT} pps")

    threads = []
    for src, dst in PORT_MAPPINGS.items():
        t_udp = threading.Thread(target=handle_udp, args=(src, dst))
        t_udp.daemon = True
        t_udp.start()
        threads.append(t_udp)

        t_tcp = threading.Thread(target=handle_tcp, args=(src, dst))
        t_tcp.daemon = True
        t_tcp.start()
        threads.append(t_tcp)

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping forwarder...")

if __name__ == "__main__":
    main()
