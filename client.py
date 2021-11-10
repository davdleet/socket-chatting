
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys

HOST = '221.155.194.202'
PORT = 50007

def main():
    try:
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            print(res)
            print(sa)
            try:
                sock = socket.socket(af, socktype, proto)
            except OSError as msg:
                sock = None
                continue
            try:
                print("connecting..")
                sock.connect(sa)
                print("after connect")
            except OSError as msg:
                print(msg)
                sock.close()
                sock = None
                continue
            except socket.error as e:
                print("socket")
            break
        if sock is None:
            print('could not open socket')
            sys.exit(1)
        with sock:
            print("with sock!")
            sock.sendall(b"hello world")
            data = sock.recv(1024)
            print("received ", repr(data))

    except socket.error as e:
        print("outer error")
        print(e)
    except KeyboardInterrupt as e:
        print("client closed by user")



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
