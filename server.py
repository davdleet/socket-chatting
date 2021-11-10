# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys
import urllib.request
import ssl
import tkinter
ssl._create_default_https_context = ssl._create_unverified_context
external_ip = urllib.request.urlopen('https://ident.me/').read().decode('utf8')
print(external_ip)


HOST = None
PORT = 50007
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
window = tkinter.Tk()
window.geometry("700x700")
window.mainloop()
def setup():
    sock = None
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, cannonname, sa = res
        try:
            sock = socket.socket(af, socktype, proto)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as msg:
            sock = None
            continue
        # socket is created successfully
        try:
            sock.bind(sa)
            sock.listen(1)
        except OSError as msg:
            sock.close()
            sock = None
            continue
        break
    return sock

def start_socket(sock):
    conn, addr = sock.accept()
    with conn:
        print('connected by', addr)
        while True:
            data = conn.recv(1024)
            parsed = data.decode('ascii')
            print(parsed)
            if not data:
                print("breaking!")
                break
            conn.send(b"success")

def main():
    window.mainloop()
    sock = setup()
    if sock is None:
        print("could not open socket")
        sys.exit(1)
    start_socket(sock)
    # window.title("Chatting Program")
    # window.mainloop()
    # try:
    #     sock = None
    #     for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    #         af, socktype, proto, cannonname, sa = res
    #         try:
    #             sock = socket.socket(af, socktype, proto)
    #             sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         except OSError as msg:
    #             sock = None
    #             continue
    #         # socket is created successfully
    #         try:
    #             sock.bind(sa)
    #             sock.listen(1)
    #         except OSError as msg:
    #             sock.close()
    #             sock = None
    #             continue
    #         break
    #     if sock is None:
    #         print("could not open socket")
    #         sys.exit(1)
    #     print("HOST,PORT: " + str(HOST), str(PORT))
    #     print("waiting to accept..")
    #     conn, addr = sock.accept()
    #     with conn:
    #         print('connected by', addr)
    #         while True:
    #             data = conn.recv(1024)
    #             parsed = data.decode('ascii')
    #             print(parsed)
    #             if not data:
    #                 print("breaking!")
    #                 break
    #             conn.send(b"success")
    # except KeyboardInterrupt as e:
    #     print("server ended by user")
    # except socket.error as e:
    #     print("some error occurred")


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#    main()
