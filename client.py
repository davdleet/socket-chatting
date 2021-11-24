# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys
import tkinter
from tkinter import *
import threading
from threading import Thread
window = tkinter.Tk()

gui=None


def connect_to_server():
    HOST = gui.server_ip_value.get()
    PORT = gui.port_value.get()
    password = gui.password_value.get()
    username = gui.username_value.get()
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
            return

        # after successfully connecting to the server socket
        with sock:
            pw_verified = False

            # check password
            encoded_password = password.encode('ascii')
            sock.send(encoded_password)
            pw_check_msg = sock.recv(1024)
            decoded_pw_check_msg = pw_check_msg.decode('ascii')
            if decoded_pw_check_msg == 'connection successful':
                pw_verified = True
            if not pw_verified:
                print(decoded_pw_check_msg)
                return

            # send username to server
            encoded_username = username.encode('ascii')
            sock.send(encoded_username)

            while True:
                send_msg = str(input("enter something to send: "))
                send_msg = send_msg.encode('ascii')
                sock.send(send_msg)
                recv_msg = sock.recv(1024)
                print(recv_msg)
                if recv_msg == b'Server Closed':
                    print("connection with server was lost")
                    break

    except socket.error as e:
        print("outer error")
        print(e)
    except KeyboardInterrupt as e:
        print("client closed by user")

class JoinGui:
    server_ip_value = None
    port_value = None
    password_value = None
    username_value = None


    window.geometry("450x300")
    window['background'] = '#252229'
    window.resizable(True, True)
    window.title("Socket Chatting Client")
    title = tkinter.Label(window, bg='#252229', fg='white', font=("Lucida Grande", 25),
                          text="Join a chatting server!",
                          relief="solid")
    title.pack(pady=20)

    label1 = Label(window, bg='#252229', fg='white', relief="solid")
    label1.pack(fill="both", padx=20)

    server_ip = Label(label1, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Server IP: ",
                      relief="solid")
    server_ip.pack(side="left")

    server_ip_value = Entry(label1, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18))
    server_ip_value.pack(side="right")

    label2 = Label(window, bg='#252229', fg='white', relief="solid")
    label2.pack(fill="both", padx=20)

    port = Label(label2, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Port: ", relief="solid")
    port.pack(side="left")

    port_value = Entry(label2, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18))
    port_value.pack(side="right")

    label3 = Label(window, bg='#252229', fg='white', relief="solid")
    label3.pack(fill="x", padx=20)

    password = Label(label3, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Password: ",
                     relief="solid")
    password.pack(side="left")

    password_value = Entry(label3, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18))
    password_value.pack(side="right")

    label4 = Label(window, bg='#252229', fg='white', relief="solid")
    label4.pack(fill="x", padx=20)

    username = Label(label4, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Username: ",
                     relief="solid")
    username.pack(side="left")

    username_value = Entry(label4, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18))
    username_value.pack(side="right")

    label5 = tkinter.Label(window, height=80)
    label5.pack(side="right", padx=20, pady=20, fill="x")

    start_button = tkinter.Button(label5, font=("Lucida Grande", 18), command=connect_to_server, width=3, height=1,
                                  text="Join")
    start_button.pack(side="right", ipadx=3, ipady=3)

    stop_button = tkinter.Button(label5, font=("Lucida Grande", 18), command=None, width=3, height=1,
                                 text="Reset")
    stop_button.pack(side="right", padx=20, ipadx=3, ipady=3)

    def start(self):
        window.mainloop()


class ChatGui:
    def setup(self):
        window.geometry("700x700")
        window['background'] = '#252229'
        window.resizable(True, True)
        window.title("Socket Chatting Client")
        title = tkinter.Label(window, bg='#252229', fg='white', font=("Lucida Grande", 25),
                              text="Join a chatting server!",
                              relief="solid")
        title.pack(pady=20)

    def start(self):
        window.mainloop()



def main():
    global gui
    gui = JoinGui()
    gui.start()
    # connect_to_server()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
