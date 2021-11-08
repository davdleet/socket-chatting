
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys

HOST = '127.0.0.1'
PORT = 50007

def main():
    try:
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                sock = socket.socket(af, socktype, proto)
            except OSError as msg:
                sock = None
                continue
            try:
                sock.connect(sa)
            except OSError as msg:
                sock.close()
                sock = None
                continue
            break
        if sock is None:
            print('could not open socket')
            sys.exit(1)
        with sock:
            sock.sendall(b"hello world")
            data = sock.recv(1024)
        print("received", repr(data))
    except socket.error as e:
        print(e)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
