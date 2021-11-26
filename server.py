# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys
import threading
import urllib.request
import ssl
import tkinter
import os
from tkinter import *
from tkinter import messagebox
from threading import Thread
import tqdm


BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
ssl._create_default_https_context = ssl._create_unverified_context
external_ip = urllib.request.urlopen('https://ident.me/').read().decode('utf8')
# print(external_ip)

HOST = None
PORT = None
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
# window = tkinter.Tk()
sock = None
serverGui = None
threads = []
started = False
stop_server = False
listen_thread = None
clients = []
server_pw = None


def join_threads():
    for thread in threads:
        print("joining..")
        thread.join()



def setup():
    global sock
    global PORT
    global server_pw
    message = "nothing"
    try:
        PORT = serverGui.port_value.get()
        server_pw = str(serverGui.password_value.get())
        print("The server password is: " + str(server_pw))
        if PORT == "":
            raise Exception("Enter a valid port number")
        # if PORT is None:
        # raise Exception("Enter a valid port number")
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
    except Exception as e:
        messagebox.showerror("Error!", e)
        sys.exit(1)


def start_server():
    setup()
    if sock is None:
        print("could not open socket")
        return
        print("test")
    print("starting socket...")
    start_socket()
    return

def add_to_list(client_info):
    None


def listen_loop():
    try:
        while True:
            # connection from client
            conn, addr = sock.accept()
            print('connected by', addr)

            # password verification
            entered_pw = conn.recv(1024)
            decoded_entered_pw = entered_pw.decode('ascii')
            print("decoded pw: " + str(decoded_entered_pw))
            print("server pw: " + str(server_pw))
            if str(decoded_entered_pw) != str(server_pw):
                pw_msg = 'wrong password!'
                encoded_pw_msg = pw_msg.encode('ascii')
                conn.send(encoded_pw_msg)
                print('wrong password!')
                continue
            else:
                pw_msg = 'connection successful'
                encoded_pw_msg = pw_msg.encode('ascii')
                conn.send(encoded_pw_msg)

            # get a username from the user
            username = conn.recv(1024)
            decoded_username = username.decode('ascii')

            # list_entry = "{:<30}".format(str(addr[0])) + "{:<20}".format(str(addr[1]))
            list_entry = f"{addr[0] : <40}{addr[1] : <19}{decoded_username : <20}\n"
            serverGui.list.insert(END, list_entry)
            clients.append(conn)
            rcv_thread = Thread(target=receiver, args=(conn, addr, decoded_username))
            rcv_thread.start()
    except ConnectionAbortedError as e:
        print("Server closed by admin")


def start_socket():
    print("server open!")
    # messagebox.showinfo("Success", "Server was successfully started")
    global started
    global stop_server
    started = True
    listener = Thread(target=listen_loop)
    listener.start()
    while not stop_server:
        None
    broadcast(b"Server Closed")
    sock.close()
    print("server socket closed")
    started = False
    stop_server = False


def receiver(conn, addr, username):
    connected = True
    print(f"new connection {addr}")
    try:
        while started:
            message = conn.recv(1024)
            decoded_message = message.decode('ascii')
            received_header = decoded_message[0:5]
            received_message = decoded_message[5:]
            if received_header == "[MSG]":
                merged_message = (str(username) + ' : ' + received_message)
                reencoded_message = merged_message.encode('ascii')
                broadcast(reencoded_message)
            elif received_header == "[FRQ]":
                print("user requested file!")
            elif received_header == "[FSN]":
                print("user uploaded file!")
                recv_file(conn, received_message)

    except (ConnectionResetError, BrokenPipeError) as e:
        clients.remove(conn)
        print(username + ' has exited the chat')
    print(f"connection lost with {addr}")


def broadcast(message):
    for client in clients:
        client.send(message)


def send_file():
    None

def recv_file(conn, received):
    # receive the file infos
    # receive using client socket, not server socket
    # received = sock.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)

    with open(filename, "wb") as f:
        while True:
            print('recv')
            # read 1024 bytes from the socket (receive)
            bytes_read = conn.recv(BUFFER_SIZE)
            print(bytes_read)
            if bytes_read == b'-1':
                print('breaking!')
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
        f.close()

def get_new_thread():
    t = Thread(target=start_server)
    threads.append(t)
    return t


def start_threads():
    global threads
    global started
    global listen_thread
    if started:
        messagebox.showerror("error", "Server is already running!")
        return
    listen_thread = get_new_thread()
    listen_thread.start()


def stop_server_button():
    global stop_server
    stop_server = True


class Gui:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.geometry("700x700")
        self.window['background'] = '#252229'
        self.window.resizable(True, True)
        self.window.title("Socket Chatting Server")

        self.title = tkinter.Label(self.window, bg='#252229', fg='white', font=("Lucida Grande", 25), text="Start a chatting Server",
                              relief="solid")
        self.title.pack(pady=20)

        self.label1 = Label(self.window, bg='#252229', fg='white', relief="solid")
        self.label1.pack(fill="both", padx=20)

        self.server_ip = Label(self.label1, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Server IP: ", relief="solid")
        self.server_ip.pack(side="left")

        self.server_ip_value = Label(self.label1, bg='#252229', fg='white', font=("Lucida Grande", 18), text=external_ip,
                                relief="solid")
        self.server_ip_value.pack(side="left")

        self.label2 = Label(self.window, bg='#252229', fg='white', relief="solid")
        self.label2.pack(fill="both", padx=20)

        self.port = Label(self.label2, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Port: ", relief="solid")
        self.port.pack(side="left")

        self.port_value = Entry(self.label2, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18), text="Port: ")
        self.port_value.pack(side="left")

        self.label3 = Label(self.window, bg='#252229', fg='white', relief="solid")
        self.label3.pack(fill="x", padx=20)

        self.password = Label(self.label3, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Password: ", relief="solid")
        self.password.pack(side="left")

        self.password_value = Entry(self.label3, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18), text="Password: ")
        self.password_value.pack(side="left")

        self.label4 = Label(self.window, bg='#252229', fg='white', relief="solid", anchor="w", font=("Lucida Grande", 18),
                    text="Connected Clients")
        self.label4.pack(fill="x", padx=20, pady=10)

        self.label5 = Label(self.window, height=100, bg='#252229', fg='white', relief="solid")
        self.label5.pack(padx=20)

        self.list = Text(self.label5, bg='#252229', fg='white', width=69, height=22, wrap=None, font=("TkFixedFont", 14),
                    relief="solid")
        self.list.pack(side="left")

        self.top_row = "{:<43}".format("Address") + "{:<20}".format("Port") + "{:<30}".format("Username") + "\n\n"
        self.list.insert(tkinter.END, self.top_row)

        self.scroll = Scrollbar(self.label5, orient="vertical", command=self.list.yview)
        self.scroll.pack(side='right', fill=Y)

        self.list.config(yscrollcommand=self.scroll.set)

        self.label6 = tkinter.Label(self.window, height=80)
        self.label6.pack(side="right", padx=20, pady=20, fill="x")

        self.start_button = tkinter.Button(self.label6, font=("Lucida Grande", 18), command=start_threads, width=3, height=1,
                                      text="start")
        self.start_button.pack(side="right", ipadx=3, ipady=3)

        self.stop_button = tkinter.Button(self.label6, font=("Lucida Grande", 18), command=stop_server_button, width=3, height=1,
                                     text="stop")
        self.stop_button.pack(side="right", padx=20, ipadx=3, ipady=3)

    def start(self):
        self.window.mainloop()
        os._exit(0)


serverGui = Gui()


def add_to_list(client_info):
    serverGui.list.insert(tkinter.END, str(client_info))


def main():
    Gui.start(serverGui)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
