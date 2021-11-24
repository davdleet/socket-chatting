
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys
import tkinter

HOST = '221.155.194.15'
PORT = 50007
window = tkinter.Tk()


class joinGui:
    window.geometry("")
    window['background'] = '#252229'
    window.resizable(True, True)
    window.title("Socket Chatting Client")
    title = tkinter.Label(window, bg='#252229', fg='white', font=("Lucida Grande", 25), text="Join a chatting server!",
                          relief="solid")
    def start(self):
        window.mainloop()

class chatGui:
    window.geometry("")
    window['background'] = '#252229'
    window.resizable(True, True)
    window.title("Socket Chatting Client")
    title = tkinter.Label(window, bg='#252229', fg='white', font=("Lucida Grande", 25), text="Join a chatting server!",
                          relief="solid")

    def start(self):
        window.mainloop()


def connect_to_server():
    try:
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            # create socket
            try:
                sock = socket.socket(af, socktype, proto)
            except OSError as msg:
                print(msg)
                sock = None
                continue
            # connect to server socket
            try:
                sock.connect(sa)
            except OSError as msg:
                print(msg)
                sock.close()
                sock = None
                continue
            except socket.error as e:
                print("socket")
            # break for loop if connection was made for IPv4 or IPv6
            break
        # If sock is still None after for loop, connection to server failed
        if sock is None:
            print('could not open socket')
            sys.exit(1)

        # after successfully connecting to the server socket
        with sock:
            while True:
                send_msg = str(input("enter something to send: "))
                send_msg = send_msg.encode('ascii')
                sock.send(send_msg)
                recv_msg = sock.recv(1024)
                print(recv_msg)
                if recv_msg == b'':
                    print("connection with server was lost")
                    break

    except socket.error as e:
        print("outer error")
        print(e)
    except KeyboardInterrupt as e:
        print("client closed by user")



def main():
    None



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
