# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys
import threading
import urllib.request
import ssl
import tkinter
from tkinter import *
from tkinter import messagebox
from threading import Thread

ssl._create_default_https_context = ssl._create_unverified_context
external_ip = urllib.request.urlopen('https://ident.me/').read().decode('utf8')
# print(external_ip)

HOST = None
PORT = None
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
window = tkinter.Tk()
sock = None
serverGui = None
threads = []
started = False
stop_server = False
listen_thread = None
clients = []


def join_threads():
    for thread in threads:
        print("joining..")
        thread.join()


def start_server():
    setup()
    if sock is None:
        print("could not open socket")
        return
        print("test")
    print("starting socket...")
    start_socket()
    return


def setup():
    global sock
    global PORT
    message = "nothing"
    try:
        PORT = serverGui.port_value.get()
        server_pw = serverGui.password_value.get()
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


def add_to_list(client_info):
    None


def start_socket():
    print("server open!")
    # messagebox.showinfo("Success", "Server was successfully started")
    global started
    global stop_server
    started = True
    while True:
        conn, addr = sock.accept()
        print('connected by', addr)
        #list_entry = "{:<30}".format(str(addr[0])) + "{:<20}".format(str(addr[1]))
        list_entry = f"{addr[0] : <30}{addr[1] : <20}"
        serverGui.list.insert(END, list_entry)
        clients.append(conn)
        rcv_thread = Thread(target=receiver, args=(conn, addr))
        rcv_thread.start()
    print("server socket closed")
    # with conn:
    #     add_to_list(addr)
    #     print('connected by', addr)
    #     while True:
    #         data = conn.recv(1024)
    #         parsed = data.decode('ascii')
    #         print(parsed)
    #         if not data:
    #             print("breaking!")
    #             break
    #         conn.send(b"success")


def receiver(conn, addr):
    connected = True
    print(f"new connection {addr}")
    while connected:
        message = conn.recv(1024)

        broadcast(message)

    print(f"connection lost with {addr}")


def broadcast(message):
    for client in clients:
        client.send(message)


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


class Gui:
    window.geometry("700x700")
    window['background'] = '#252229'
    window.resizable(True, True)
    window.title("Socket Chatting Server")

    title = tkinter.Label(window, bg='#252229', fg='white', font=("Lucida Grande", 25), text="Start a chatting Server",
                          relief="solid")
    title.pack(pady=20)

    label1 = Label(window, bg='#252229', fg='white', relief="solid")
    label1.pack(fill="both", padx=20)

    server_ip = Label(label1, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Server IP: ", relief="solid")
    server_ip.pack(side="left")

    server_ip_value = Label(label1, bg='#252229', fg='white', font=("Lucida Grande", 18), text=external_ip,
                            relief="solid")
    server_ip_value.pack(side="left")

    label2 = Label(window, bg='#252229', fg='white', relief="solid")
    label2.pack(fill="both", padx=20)

    port = Label(label2, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Port: ", relief="solid")
    port.pack(side="left")

    port_value = Entry(label2, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18), text="Port: ")
    port_value.pack(side="left")

    label3 = Label(window, bg='#252229', fg='white', relief="solid")
    label3.pack(fill="x", padx=20)

    password = Label(label3, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Password: ", relief="solid")
    password.pack(side="left")

    password_value = Entry(label3, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18), text="Password: ")
    password_value.pack(side="left")

    label4 = Label(window, bg='#252229', fg='white', relief="solid", anchor="w", font=("Lucida Grande", 18),
                   text="Connected Clients")
    label4.pack(fill="x", padx=20, pady=10)

    label5 = Label(window, height=100, bg='#252229', fg='white', relief="solid")
    label5.pack(padx=20)

    list = Text(label5, bg='#252229', fg='white', width=69, height=22, wrap=None, font=("TkFixedFont", 14), relief="solid")
    list.pack(side="left")

    top_row = "{:<30}".format("Address") + "{:<20}".format("Port") + "{:<30}".format("Username") + "\n\n"
    list.insert(tkinter.END, top_row)

    scroll = Scrollbar(label5, orient="vertical", command=list.yview)
    scroll.pack(side='right', fill=Y)

    list.config(yscrollcommand=scroll.set)

    label6 = tkinter.Label(window, height=80)
    label6.pack(side="right", padx=20, pady=20, fill="x")

    t = Thread(target=start_server)
    threads.append(t)
    start_button = tkinter.Button(label6, font=("Lucida Grande", 18), command=start_threads,
                                  width=3, height=1, text="start")
    start_button.pack(side="right", ipadx=3, ipady=3)

    stop_button = tkinter.Button(label6, font=("Lucida Grande", 18), command=None, width=3, height=1, text="stop")
    stop_button.pack(side="right", padx=20, ipadx=3, ipady=3)

    def start(self):
        window.mainloop()


serverGui = Gui()


def add_to_list(client_info):
    serverGui.list.insert(tkinter.END, str(client_info))


def main():
    Gui.start(serverGui)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
