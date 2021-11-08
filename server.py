# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys

HOST = ''
PORT = 50007
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
print(local_ip)
def main():
    print("server")
    try:
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            af, socktype, proto, cannonname, sa = res
            try:
                sock = socket.socket(af, socktype, proto)
            except OSError as msg:
                sock = None
                continue
            # socket is created successfully
            try:
                print("sa is: " + str(sa))
                sock.bind(sa)
                sock.listen(1)
            except OSError as msg:
                sock.close()
                sock = None
                continue
            break
        if sock is None:
            print("could not open socket")
            sys.exit(1)
        print("HOST,PORT: " + str(HOST), str(PORT))
        print("waiting to accept..")
        conn, addr = sock.accept()
        with conn:
            print('connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    print("breaking!")
                    break
                #conn.send(data)
                print(repr(data))
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
        print(HOST, PORT)
        # print(HOST)
        sock.bind((HOST, PORT))
    except KeyboardInterrupt as e:
        print("server ended by user")
    except socket.error as e:
        print("some error occurred")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
