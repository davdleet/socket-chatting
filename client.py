# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys
import tkinter
from tkinter import *
import threading
from threading import Thread


gui = None
sock=None
threads = []
chatting = False
errorcode = 0

def chat():
    try:
        while True:
            send_msg = str(input("enter something to send: "))
            send_msg = send_msg.encode('ascii')
            sock.send(send_msg)
            recv_msg = sock.recv(1024)
            print(recv_msg)
            if recv_msg == b'Server Closed':
                print("connection with server was lost")
                break
    except Exception as e:
        print(e)

def connect_to_server():
    global sock
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
                # sock.close()
                sock = None
                continue
            except socket.error as e:
                print("socket")
            # break for loop if connection was made for IPv4 or IPv6
            break
        # If sock is still None after for loop, connection to server failed
        if sock is None:
            print('could not open socket')
            return 2

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
                return 1

            # send username to server
            encoded_username = username.encode('ascii')
            sock.send(encoded_username)

            t = Thread(target=chat)
            t.start()
            # while True:
            #     send_msg = str(input("enter something to send: "))
            #     if send_msg == '/quit':
            #         print("quit chatting from the server")
            #         break
            #     send_msg = send_msg.encode('ascii')
            #     sock.send(send_msg)
            #     recv_msg = sock.recv(1024)
            #     print(recv_msg)
            #     if recv_msg == b'Server Closed':
            #         print("connection with server was lost")
            #         break
            return 0
            # chat(sock)

    except socket.error as e:
        print("outer error")
        print(e)
    except KeyboardInterrupt as e:
        print("client closed by user")


def open_chat_gui():
    chatgui = ChatGui()
    chatgui.start()


class JoinGui:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.geometry("450x300")
        self.window['background'] = '#252229'
        self.window.resizable(True, True)
        self.window.title("Socket Chatting Client")
        self.title = tkinter.Label(self.window, bg='#252229', fg='white', font=("Lucida Grande", 25),
                                   text="Join a chatting server!",
                                   relief="solid")
        self.title.pack(pady=20)

        self.label1 = Label(self.window, bg='#252229', fg='white', relief="solid")
        self.label1.pack(fill="both", padx=20)

        self.server_ip = Label(self.label1, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Server IP: ",
                               relief="solid")
        self.server_ip.pack(side="left")

        self.server_ip_value = Entry(self.label1, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18))
        self.server_ip_value.pack(side="right")

        self.label2 = Label(self.window, bg='#252229', fg='white', relief="solid")
        self.label2.pack(fill="both", padx=20)

        self.port = Label(self.label2, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Port: ",
                          relief="solid")
        self.port.pack(side="left")

        self.port_value = Entry(self.label2, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18))
        self.port_value.pack(side="right")

        self.label3 = Label(self.window, bg='#252229', fg='white', relief="solid")
        self.label3.pack(fill="x", padx=20)

        self.password = Label(self.label3, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Password: ",
                              relief="solid")
        self.password.pack(side="left")

        self.password_value = Entry(self.label3, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18))
        self.password_value.pack(side="right")

        self.label4 = Label(self.window, bg='#252229', fg='white', relief="solid")
        self.label4.pack(fill="x", padx=20)

        self.username = Label(self.label4, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Username: ",
                              relief="solid")
        self.username.pack(side="left")

        self.username_value = Entry(self.label4, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18))
        self.username_value.pack(side="right")

        self.label5 = tkinter.Label(self.window, height=80)
        self.label5.pack(side="right", padx=20, pady=20, fill="x")

        self.start_button = tkinter.Button(self.label5, font=("Lucida Grande", 18), command=self.press_start_button,
                                           width=3, height=1,
                                           text="Join")
        self.start_button.pack(side="right", ipadx=3, ipady=3)

        self.reset_button = tkinter.Button(self.label5, font=("Lucida Grande", 18), command=self.reset_input, width=3,
                                           height=1,
                                           text="Reset")
        self.reset_button.pack(side="right", padx=20, ipadx=3, ipady=3)

    def press_start_button(self):
        result = connect_to_server()
        if result == 1:
            print("Your password was wrong")
        elif result > 0:
            print("There was some error in connecting")
        elif result == 0:
            print("connection was successful")
            self.window.destroy()
            open_chat_gui()

    def reset_input(self):
        self.server_ip_value.delete(0, END)
        self.port_value.delete(0, END)
        self.password_value.delete(0, END)
        self.username_value.delete(0, END)

    def start(self):
        self.window.mainloop()


class ChatGui:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.geometry("700x700")
        self.window['background'] = '#252229'
        self.window.resizable(True, True)
        self.window.title("Socket Chatting Client")
        self.title = tkinter.Label(self.window, bg='#252229', fg='white', font=("Lucida Grande", 25),
                                   text="Join a chatting server!",
                                   relief="solid")
        self.title.pack(pady=20)

    def start(self):
        self.window.mainloop()


def main():
    global gui
    gui = JoinGui()
    gui.start()
    # connect_to_server()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
