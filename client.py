import socket
import sys
import os
import tkinter
from tkinter import *
import threading
from threading import Thread
from tkinter import filedialog
import tqdm
import errno
import re

gui = None
sock = None
threads = []
chatting = False
errorcode = 0
makebutton = False
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
buffers = []

HOST = None
PORT = None
password = None
username = None


# executed by other thread
def show_chat(msg):
    global gui
    gui.chat_log.insert(tkinter.END, msg)
    # gui.change_make_button()
    global makebutton
    makebutton = True
    gui.chat_log.see("end")

def show_file(filename, file_id, conv_filesize, filesize):
    global gui
    gui.make_download_button(filename, file_id, conv_filesize, filesize)
    gui.chat_log.insert(tkinter.END, '\n')

def testfunc():
    print("hi")

def send_file():

    filepath = filedialog.askopenfilename()
    print('Selected: ', filepath)
    filename = filepath.split('/')[-1]
    print('filename: ', filename)
    filesize = os.path.getsize(filepath)
    sock.sendall(f'[FUP]{filename}{SEPARATOR}{filesize}[END]'.encode('ascii'))
    # progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    send_times = int(filesize/BUFFER_SIZE) + 1
    remaining = filesize
    with open(filepath, 'rb') as f:
        bytes_read = None
        for i in range(0, send_times):
            bytes_read = f.read(BUFFER_SIZE)
            sock.send(bytes_read)
            # progress.update(len(bytes_read))
        i = 0
        # while True:
        #     buff = None
            # if remaining >= BUFFER_SIZE:
            #     buff = BUFFER_SIZE
            #     remaining = remaining - BUFFER_SIZE
            # elif remaining == 0:
            #     break
            # elif remaining < BUFFER_SIZE:
            #     buff = remaining
            # else:
            #     raise

            # bytes_read = f.read(BUFFER_SIZE)
            # # progress.update(len(bytes_read))
            # if not bytes_read:
            #     sock.sendall(b'$[%EOF%]$')
            #     print()
            #     print('done sending')
            #     print(f'sent {i} times')
            #     break
            # sock.sendall(bytes_read)
            # i = i + 1
        f.close()

def request_file(filename, file_id, file_size):
    print(f'request {filename} id: {file_id} size: {file_size}')
    request_filename = f'{file_id}-{filename}'
    request = f'[FRQ]{request_filename}[END]'
    filler_len = 4096 - len(request)
    filler = ' ' * filler_len
    full_request = request + filler
    encoded_request = full_request.encode('ascii')
    sock.send(encoded_request)

def receive_file(filename, file_size):
    global buffers
    global sock

    recv_times = int(int(file_size) / BUFFER_SIZE + 1)

    remaining = file_size
    print(f'must receive {recv_times} times!')
    if not os.path.exists(os.path.dirname('downloads')):
        try:
            os.makedirs('downloads')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    if file_size == 0:
        f = open('downloads/' +str(filename), "wb")
        f.close()
        return
    else:
        with open('downloads/' + filename, "wb") as f:
            eof = '$[%EOF%]$'
            eof_fill_len = 4096 - len(eof)
            eof_fill = ' ' * eof_fill_len
            eof = eof + eof_fill
            remaining_count = int(file_size)
            bytes_read = None
            while True:
                if BUFFER_SIZE > remaining_count > 0:

                    bytes_read = sock.recv(remaining_count)
                    while len(bytes_read) != remaining_count:
                        bytes_read = bytes_read + sock.recv(remaining_count - len(bytes_read))
                    remaining_count = remaining_count - len(bytes_read)
                else:
                    print('check to receive last')
                    bytes_read = sock.recv(BUFFER_SIZE)
                    while len(bytes_read) != BUFFER_SIZE:
                        bytes_read = bytes_read + sock.recv(BUFFER_SIZE - len(bytes_read))
                    remaining_count = remaining_count - len(bytes_read)
                # decoded_bytes_read = bytes_read.decode('ascii')
                if bytes_read == eof.encode('utf-8'):
                    print(f'breaking receivE!')
                    break

                f.write(bytes_read)

            f.close()
# to be executed by other thread
def receive_chat():
    print("recv chat: " + str(threading.get_ident()))
    recv_msg = None
    try:
        while True:
            recv_msg = sock.recv(4096)
            decoded_recv_msg = recv_msg.decode('ascii')
            decoded_recv_msg = decoded_recv_msg.rstrip()
            usable_message = decoded_recv_msg.replace('[END]', '')
            # split_messages = decoded_recv_msg.split('[END]')
            # usable_message = split_messages[0]
            # if len(split_messages) > 1:
            #     print("more than one split message")
            #     if split_messages[1] != '':
            #         buffers.append(split_messages[1])
            #         print(split_messages[1])
            header = usable_message[0:5]
            msg_body = usable_message[5:]
            if recv_msg == b'Server Closed':
                show_chat("The server is closed")
                break
            if header == '[MSG]':
                show_chat(msg_body)
            elif header == '[FBC]':
                split_body = msg_body.split(SEPARATOR)
                broadcast_filename = split_body[0]
                broadcast_fileid = split_body[1]
                broadcast_conv_filesize = split_body[2]
                broadcast_filesize = split_body[3]
                show_file(broadcast_filename, broadcast_fileid, broadcast_conv_filesize, broadcast_filesize)
            elif header == '[FDN]':
                print('header entered!')
                split_body = msg_body.split(SEPARATOR)
                download_filename = split_body[0]
                download_size = split_body[1]
                receive_file(download_filename, download_size)

    except Exception as e:
        #print(f'receive message was: {recv_msg}')
        show_chat("An error occurred. Please restart the program.")


# to be executed by main thread
def send_chat(*args):
    try:
        send_msg = gui.chat_value.get() + '\n'
        gui.chat_value.delete(0, tkinter.END)
        header = "[MSG]"
        merged_msg = header + send_msg + '[END]'
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
    global HOST, PORT, password, username
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

def new_sock():
    newsock = None
    # HOST = gui.server_ip_value.get()
    # PORT = gui.port_value.get()
    # password = gui.password_value.get()
    # username = gui.username_value.get()
    global HOST, PORT, password, username

    try:
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            # create socket
            try:
                newsock = socket.socket(af, socktype, proto)
            except OSError as msg:
                print("oserror1")
                print(msg)
                newsock = None
                continue
            # connect to server socket
            try:
                newsock.connect(sa)
            except OSError as msg:
                print("oserror2")
                print(msg)
                newsock.close()
                newsock = None
                continue
            except socket.error as e:
                newsock = None
                print("socket")
            # break for loop if connection was made for IPv4 or IPv6
            break
        # If sock is still None after for loop, connection to server failed
        if newsock is None:
            print('could not open socket')
            return None
        return newsock
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


    def make_download_button(self, file_name, file_id, conv_filesize, file_size):
        print("make download: " + str(threading.get_ident()))
        self.chat_log.window_create(tkinter.END, window=tkinter.Button(self.chat_log, text=f"Download {file_name} - {conv_filesize}", command=lambda arg1=file_name, arg2=file_id, arg3=file_size: request_file(arg1, arg2, arg3)))
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
