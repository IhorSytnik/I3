import socket
import ssl
import threading
#untested prototype
#should first generate keys i guess openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem
def receive_messages(ssl_sock, label):
    while True:
        try:
            msg = ssl_sock.recv(1024).decode()
            if not msg:
                break
            print(f"\n[{label}] {msg}\nYou: ", end="")
        except:
            print(f"\n[!] {label} connection lost.")
            break

def start_server(listen_port, certfile, keyfile):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    bindsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bindsock.bind(('0.0.0.0', listen_port))
    bindsock.listen(1)
    print(f"[Server] Listening with TLS on port {listen_port}...")

    newsock, addr = bindsock.accept()
    ssl_sock = context.wrap_socket(newsock, server_side=True)
    print(f"[Server] TLS connection established from {addr}")
    return ssl_sock

def start_client(friend_ip, friend_port):
    context = ssl.create_default_context()
    # Optional: load friend's cert here using context.load_verify_locations()

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((friend_ip, friend_port))
            ssl_sock = context.wrap_socket(sock, server_hostname=friend_ip)
            print(f"[Client] TLS connection established with {friend_ip}:{friend_port}")
            return ssl_sock
        except:
            print("[Client] Retrying connection...")
            import time
            time.sleep(2)

def main():
    my_port = int(input("Your listening port: "))
    friend_ip = input("Friend's IP address: ").strip()
    friend_port = int(input("Friend's listening port: "))
    certfile = "cert.pem"
    keyfile = "key.pem"

    # Start server in a thread
    def server_thread():
        server_sock = start_server(my_port, certfile, keyfile)
        receive_messages(server_sock, "Incoming")

    threading.Thread(target=server_thread, daemon=True).start()

    # Start client connection
    client_sock = start_client(friend_ip, friend_port)
    threading.Thread(target=receive_messages, args=(client_sock, "Outgoing"), daemon=True).start()

    # Sending loop
    while True:
        try:
            msg = input("You: ")
            if msg.lower() in ("exit", "quit"):
                print("[*] Closing connection.")
                client_sock.close()
                break
            client_sock.send(msg.encode())
        except Exception as e:
            print(f"[!] Error sending message: {e}")
            break

if __name__ == "__main__":
    main()
