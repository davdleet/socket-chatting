import socket
import sys
import os
import tkinter
from tkinter import *
import threading
from threading import Thread
from tkinter import filedialog
import tqdm
gui = None
sock = None
threads = []
chatting = False
errorcode = 0
makebutton = False
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

# executed by other thread
def make_download_button(text):
    gui.chat_log.window_create(tkinter.END, window=tkinter.Button(gui.chat_log, text=text, command=testfunc))
    global makebutton
    makebutton = False

# executed by other thread
def show_chat(msg):
    global gui
    gui.chat_log.insert(tkinter.END, msg)
    # gui.change_make_button()
    global makebutton
    makebutton = True
    gui.chat_log.see("end")


def testfunc():
    print("hi")

def send_file():

    filepath = filedialog.askopenfilename()
    print('Selected: ', filepath)
    filename = filepath.split('/')[-1]
    print('filename: ', filename)
    filesize = os.path.getsize(filepath)
    sock.send(f'[FSN]{filename}{SEPARATOR}{filesize}'.encode())
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filepath, 'rb') as f:
        bytes_read = None
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            sock.sendall(bytes_read)
            progress.update(len(bytes_read))
        f.close()
def receive_file():
    None

# to be executed by other thread
def receive_chat():
    print("recv chat: " + str(threading.get_ident()))
    try:
        while True:
            recv_msg = sock.recv(1024)
            decoded_recv_msg = recv_msg.decode('ascii')
            if recv_msg == b'Server Closed':
                show_chat("The server is closed")
                break
            show_chat(decoded_recv_msg)

    except Exception as e:
        show_chat("An error occurred. Please restart the program.")

# to be executed by main thread
def send_chat(*args):
    try:
        send_msg = gui.chat_value.get() + '\n'
        gui.chat_value.delete(0, tkinter.END)
        header = "[MSG]"
        merged_msg = header + send_msg
        encoded_send_msg = merged_msg.encode('ascii')
        sock.send(encoded_send_msg)
    except Exception as e:
        show_chat("An error occurred. Please restart the program.")


# running on separate thread from main (gui) thread
def chat():
    global sock

    # receiver_thread = Thread(target=receive_chat)
    # receiver_thread.start()

    receive_chat()

# running on main thread splits from here
def connect_to_server():
    global sock
    # HOST = gui.server_ip_value.get()
    # PORT = gui.port_value.get()
    # password = gui.password_value.get()
    # username = gui.username_value.get()
    HOST = '221.155.194.15'
    PORT = '50007'
    password = '1234'
    username= 'temp'
    try:
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            # create socket
            try:
                sock = socket.socket(af, socktype, proto)
            except OSError as msg:
                print("oserror1")
                print(msg)
                sock = None
                continue
            # connect to server socket
            try:
                sock.connect(sa)
            except OSError as msg:
                print("oserror2")
                print(msg)
                sock.close()
                sock = None
                continue
            except socket.error as e:
                sock = None
                print("socket")
            # break for loop if connection was made for IPv4 or IPv6
            break
        # If sock is still None after for loop, connection to server failed
        if sock is None:
            print('could not open socket')
            return 2

        # after successfully connecting to the server socket
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

        global chatting
        chatting = True
        print("main: " + str(threading.get_ident()))
        t = Thread(target=chat)
        t.start()
        # chat(sock)

        return 0
    except socket.error as e:
        print("outer error")
        print(e)
    except KeyboardInterrupt as e:
        print("client closed by user")


def open_chat_gui():
    print("opening chat gui")
    global gui
    gui = ChatGui()
    gui.start()



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
            global gui
            global chatting
            global makebutton
            gui = None
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
                                   text="Chatting Room",
                                   relief="solid")
        self.title.pack(pady=20)

        self.label1 = Label(self.window, height=100, bg='#252229', fg='white', relief="solid")
        self.label1.pack(padx=20)

        self.chat_log = Text(self.label1, bg='#252229', fg='white', width=62, height=25, wrap=None,
                             font=("TkFixedFont", 14),
                             relief="solid")
        self.chat_log.pack(side="left")

        self.scroll = Scrollbar(self.label1, orient="vertical", command=self.chat_log.yview)
        self.scroll.pack(side='right', fill=Y)

        self.chat_log.config(yscrollcommand=self.scroll.set)

        self.label2 = Label(self.window, width=100, height=100, bg='#252229', fg='white', relief="solid")
        self.label2.pack(padx=25, pady=20, fill='both')

        self.chat_value = Entry(self.label2, bg='#252229', fg='white', bd=0, font=("Lucida Grande", 18))
        self.chat_value.pack(side="left", padx= 10, ipadx=100, ipady=40)

        self.chat_value.bind('<Return>', send_chat)

        self.send_button = Button(self.label2, font=("Lucida Grande", 18), height=100, width=6, command=send_chat,
                                  text='Send')
        self.send_button.pack(side="right")

        self.file_button = Button(self.label2, font=("Lucida Grande", 18), height=100, width=6, command=send_file, text='Attach')
        self.file_button.pack(side="right")


        self.make_button = tkinter.BooleanVar(value=False)
        self.make_button.trace("w", self.insert_button)

    def something(self):
        print(1)

    def insert_button(self, *args):
        print("insert button: " + str(threading.get_ident()))
        self.chat_log.window_create(tkinter.END, window=tkinter.Button(self.chat_log, text="download", command=self.something))
        self.chat_log.insert(END, "\n")
    def change_make_button(self):
        self.make_button.set(True)


    def make_download_button(self, text):
        print("make download: " + str(threading.get_ident()))
        self.chat_log.window_create(tkinter.END, window=tkinter.Button(self.chat_log, text=text, command=None))
        global makebutton
        makebutton = False

    def start(self):
        self.window.mainloop()
        print('program fininshed')
        os._exit(0)


def main():
    try:
        global gui
        gui = JoinGui()
        gui.start()
        # connect_to_server()
    except KeyboardInterrupt as e:
        print("program ended by user")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
