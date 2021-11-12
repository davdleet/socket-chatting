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
PORT = 50007
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
window = tkinter.Tk()
sock = None
myGui = None
threads = []

def join_threads():
    for thread in threads:
        print("joining..")
        thread.join()

def start_server():
    setup()
    if sock is None:
        print("could not open socket")
        sys.exit(1)
    start_socket()
    return


def setup():
    global sock
    global PORT
    message = "nothing"
    try:
        PORT = myGui.port_value.get()
        if PORT == "":
            raise Exception("Enter a valid port number")
        #if PORT is None:
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
        join_threads()
        sys.exit(1)


def add_to_list(client_info):
    None


def start_socket():
    print("server open!")

    conn, addr = sock.accept()
    with conn:
        add_to_list(addr)
        print('connected by', addr)
        while True:
            data = conn.recv(1024)
            parsed = data.decode('ascii')
            print(parsed)
            if not data:
                print("breaking!")
                break
            conn.send(b"success")

class Gui:
    window.geometry("700x700")
    window['background'] = '#252229'
    window.resizable(True, True)
    window.title("Socket Chatting")

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
    label5.pack(fill="x", padx=20)

    list = Text(label5, bg='#252229', fg='white', width=89, height=25, wrap=None, relief="solid")
    list.pack(side="left")

    for line in range(100):
        list.insert(END, "This is line number " + str(line) + "\n")

    scroll = Scrollbar(label5, orient="vertical", command=list.yview)
    scroll.pack(side='right', fill=Y)

    list.config(yscrollcommand=scroll.set)

    list.insert(tkinter.END, "hello")

    # scroll = Scrollbar(label5, orient="vertical")
    # scroll.pack(side="right")

    # label5.config(xscrollcommand = scroll.set)

    label6 = tkinter.Label(window, height=80)
    label6.pack(side="right", padx=20, pady=20, fill="x")

    t = Thread(target=start_server)
    threads.append(t)
    start_button = tkinter.Button(label6, font=("Lucida Grande", 18), command=t.start,
                                  width=3, height=1, text="start")
    start_button.pack(side="right", ipadx=3, ipady=3)

    stop_button = tkinter.Button(label6, font=("Lucida Grande", 18), command=None, width=3, height=1, text="stop")
    stop_button.pack(side="right", padx=20, ipadx=3, ipady=3)

    def start(self):
        window.mainloop()

myGui = Gui()


def add_to_list(client_info):
    myGui.list.insert(tkinter.END, str(client_info))

def main():
    Gui.start(myGui)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
