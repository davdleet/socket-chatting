import socket
import sys
import os
import tkinter
from tkinter import *
import threading
from threading import Thread
from tkinter import filedialog
from tkinter import messagebox
import errno
import json
import time
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
    global makebutton
    makebutton = True
    gui.chat_log.see("end")

def show_file(filename, file_id, conv_filesize, filesize):
    global gui
    gui.make_download_button(filename, file_id, conv_filesize, filesize)
    gui.chat_log.insert(tkinter.END, '\n')

def send_file():
    filepath = None
    try:
        filepath = filedialog.askopenfilename()
        print('Selected path: ', filepath)
        filename = filepath.split('/')[-1]
        print('filename: ', filename)
        filesize = os.path.getsize(filepath)

        fup = f'[FUP]{filename}{SEPARATOR}{filesize}[END]'
        filler_len = 4096 - len(fup)
        filler = ' ' * filler_len
        fup = fup + filler
        sock.sendall(fup.encode('ascii'))
        with open(filepath, 'rb') as f:
            bytes_read = None
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                sock.sendall(bytes_read)
            f.close()
    except UnicodeEncodeError:
        print("invalid upload title - try changing the title to alphanumeric")
        # messagebox.showerror("error", "please make sure your files have english titles")
    except FileNotFoundError:
        if filepath == '':
            print('upload cancelled')
        else:
            print("File was not found")
            #messagebox.showerror("error", "File was not found")

def request_file(filename, file_id, file_size):
    print(f'requesting {filename} id: {file_id} size: {file_size}')
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
            remaining_count = int(file_size)
            bytes_read = None
            while True:
                if remaining_count == 0:
                    break
                elif BUFFER_SIZE > remaining_count > 0:

                    bytes_read = sock.recv(remaining_count)
                    while len(bytes_read) != remaining_count:
                        bytes_read = bytes_read + sock.recv(remaining_count - len(bytes_read))
                    remaining_count = remaining_count - len(bytes_read)
                else:
                    bytes_read = sock.recv(BUFFER_SIZE)
                    while len(bytes_read) != BUFFER_SIZE:
                        bytes_read = bytes_read + sock.recv(BUFFER_SIZE - len(bytes_read))
                    remaining_count = remaining_count - len(bytes_read)
                f.write(bytes_read)

            f.close()

# to be executed by other thread
def receive_chat():
    global gui
    global chatting
    while not gui:
        #print('wait for gui')
        None
    time.sleep(1)
    print('receiving chat')
    recv_msg = None
    try:
        while chatting:
            # recv_msg = sock.recv(4096)
            recv_msg = receive_bytes(sock, 4096)
            decoded_recv_msg = recv_msg.decode('ascii')
            decoded_recv_msg = decoded_recv_msg.rstrip()
            usable_message = decoded_recv_msg.replace('[END]', '')
            header = usable_message[0:5]
            msg_body = usable_message[5:]
            if recv_msg == b'Server Closed':
                show_chat("The server is closed")
                break
            if header == '[MSG]':
                print(f'message from user {msg_body}', end='')
                show_chat(msg_body)
            elif header == '[FBC]':
                split_body = msg_body.split(SEPARATOR)
                broadcast_filename = split_body[0]
                broadcast_fileid = split_body[1]
                broadcast_conv_filesize = split_body[2]
                broadcast_filesize = split_body[3]
                print(f'file broadcasted: {broadcast_filename}')
                show_file(broadcast_filename, broadcast_fileid, broadcast_conv_filesize, broadcast_filesize)
            elif header == '[FDN]':
                split_body = msg_body.split(SEPARATOR)
                download_filename = split_body[0]
                download_size = split_body[1]
                print(f'downloading {download_filename}')
                receive_file(download_filename, download_size)
            else:
                if usable_message == '':
                    return
                print('server message : ' + usable_message)
                show_chat(usable_message + '\n')
    except (BrokenPipeError, ConnectionResetError) as e:
        print('connection broken')
        show_chat("Connection is broken. Please re-boot the program.")
    except Exception as e:
        print(e.with_traceback())
        # show_chat("An error occurred.\n")
        # receive_chat()


# to be executed by main thread
def send_chat(*args):
    global gui
    global chatting
    global sock
    try:
        send_msg = gui.chat_value.get() + '\n'

        gui.chat_value.delete(0, tkinter.END)
        header = "[MSG]"
        merged_msg = header + send_msg + '[END]'
        encoded_send_msg = merged_msg.encode('ascii')
        # sock.send(encoded_send_msg)
        send_bytes(sock, encoded_send_msg, 4096)
        print('message sent!')
        if send_msg == '/quit\n':
            if os.path.exists('credential.json'):
                os.remove('credential.json')
            print('quitting chat room')
            sock.close()
            gui.destroy()
            chatting = False
            os._exit(0)
    except Exception as e:
        print(e)
        show_chat("An error occurred. Please restart the program.")
        os._exit(0)

def b_string_fill(bstring, size):
    fill_size = size - len(bstring)
    fill = ' ' * fill_size
    result = bstring + fill
    return result

def b_string_check(bstring, size):
    decoded_bstring = bstring.decode('ascii')
    if len(decoded_bstring) == size:
        return True
    else:
        return False

def receive_bytes(s, length):
    result = b''
    while not b_string_check(result, length):
        result = result + s.recv(length - result)
    return result

def send_bytes(s, bstring, length):
    s.send(b_string_fill(bstring, length))

def receive_bytes(sock, length):
    result = b''
    while not b_string_check(result, length):
        result = result + sock.recv(length - result)
    return result

# running on separate thread from main (gui) thread
def chat():
    global sock
    receive_chat()

# running on main thread splits from here
def connect_to_server(HOST, PORT, password, username, input_token):
    global sock
    global chatting
    try:

        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            # create socket
            try:
                sock = socket.socket(af, socktype, proto)
            except OSError as msg:
                global gui
                sock = None
                continue
            # connect to server socket
            try:
                sock.connect(sa)
            except OSError as msg:
                sock.close()
                sock = None
                continue
            except socket.error as e:
                print('socket error')
                sock = None
            # break for loop if connection was made for IPv4 or IPv6
            break
        # If sock is still None after for loop, connection to server failed
        if sock is None:
            #messagebox.showerror('error', 'Error opening socket')
            return 2

        # after successfully connecting to the server socket
        pw_verified = False

        #token reconnect if token is provided
        if input_token:
            print(f'your token: {input_token}')
            sock.send(input_token.encode('ascii'))
            token_response = sock.recv(3)
            decoded_token_response = token_response.decode('ascii')
            if decoded_token_response == 'SCS':
                chatting = True
                t = Thread(target=chat)
                t.start()
                return 0
            elif decoded_token_response == 'DUP':
                return 5
            else:
                return 3
        else:
            print('no token available')
            sock.send(b'****************')

        # check password
        encoded_password = password.encode('ascii')
        #sock.send(encoded_password)
        send_bytes(sock, encoded_password, 1024)
        pw_check_msg = sock.recv(3)
        decoded_pw_check_msg = pw_check_msg.decode('ascii')
        if decoded_pw_check_msg == 'SCS':
            pw_verified = True
        if not pw_verified:
            print(decoded_pw_check_msg)
            return 1


        # send username to server
        encoded_username = username.encode('ascii')
        #sock.send(encoded_username)
        send_bytes(sock, encoded_username, 1024)
        token = sock.recv(16)
        decoded_token = token.decode('ascii')
        print(f'received token from server: {decoded_token}')
        credential = {
            'token':decoded_token,
            'host':HOST,
            'port':PORT
        }
        with open('credential.json', 'w') as f:
            json.dump(credential, f)
            f.close()
        chatting = True

        t = Thread(target=chat)
        t.start()
        return 0
    except socket.error as e:
        print(e)
    except KeyboardInterrupt as e:
        print("client closed by user")
    except Exception as e:
        print('error while connecting to server')

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
                            )
        self.title.pack(pady=20)

        self.label1 = Label(self.window, bg='#252229', fg='white')
        self.label1.pack(fill="both", padx=20)

        self.server_ip = Label(self.label1, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Server IP: ",
                        )
        self.server_ip.pack(side="left")

        self.server_ip_value = Entry(self.label1, bg='#252229', fg='white', font=("Lucida Grande", 18))
        self.server_ip_value.pack(side="right")

        self.label2 = Label(self.window, bg='#252229', fg='white')
        self.label2.pack(fill="both", padx=20)

        self.port = Label(self.label2, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Port: ",
                    )
        self.port.pack(side="left")

        self.port_value = Entry(self.label2, bg='#252229', fg='white', font=("Lucida Grande", 18))
        self.port_value.pack(side="right")

        self.label3 = Label(self.window, bg='#252229', fg='white')
        self.label3.pack(fill="x", padx=20)

        self.password = Label(self.label3, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Password: ",
                        )
        self.password.pack(side="left")

        self.password_value = Entry(self.label3, bg='#252229', fg='white', font=("Lucida Grande", 18))
        self.password_value.pack(side="right")

        self.label4 = Label(self.window, bg='#252229', fg='white')
        self.label4.pack(fill="x", padx=20)

        self.username = Label(self.label4, bg='#252229', fg='white', font=("Lucida Grande", 18), text="Username: ",
                        )
        self.username.pack(side="left")

        self.username_value = Entry(self.label4, bg='#252229', fg='white', font=("Lucida Grande", 18))
        self.username_value.pack(side="right")

        self.label5 = tkinter.Label(self.window, height=80)
        self.label5.pack(side="right", padx=20, pady=20, fill="x")

        self.start_button = tkinter.Button(self.label5, font=("Lucida Grande", 13), command=self.press_start_button,
                                           width=4, height=1,
                                           text="Join")
        self.start_button.pack(side="right", ipadx=3, ipady=3)

        self.reset_button = tkinter.Button(self.label5, font=("Lucida Grande", 13), command=self.reset_input, width=4,
                                           height=1,
                                           text="Reset")
        self.reset_button.pack(side="right", padx=20, ipadx=3, ipady=3)

    def press_start_button(self):
        host = self.server_ip_value.get()
        port = self.port_value.get()
        pw = self.password_value.get()
        usern = self.username_value.get()

        result = connect_to_server(host, port, pw, usern, None)
        if result == 1:
            print("Your password was wrong")
            #messagebox.showerror("error", "Wrong server password!")
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

    def destroy(self):
        self.window.destroy()

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
                            )
        self.title.pack(pady=20)

        self.label1 = Label(self.window, height=100, bg='#252229', fg='white')
        self.label1.pack(padx=20)

        self.chat_log = Text(self.label1, bg='#252229', fg='white', width=72, height=25, wrap=None,
                             font=("Fixedsys", 14),
                        )
        self.chat_log.pack(side="left")

        self.scroll = Scrollbar(self.label1, orient="vertical", command=self.chat_log.yview)
        self.scroll.pack(side='right', fill=Y)

        self.chat_log.config(yscrollcommand=self.scroll.set)

        self.label2 = Label(self.window, width=100, height=100, bg='#252229', fg='white')
        self.label2.pack(padx=25, pady=20, fill='both')

        self.chat_value = Entry(self.label2, bg='#252229', fg='white', font=("Lucida Grande", 18))
        self.chat_value.pack(side="left", padx= 10, ipadx=100, ipady=40)

        self.chat_value.bind('<Return>', send_chat)

        self.send_button = Button(self.label2, font=("Lucida Grande", 13), height=100, width=6, command=send_chat,
                                  text='Send')
        self.send_button.pack(side="right", pady = 35)

        self.file_button = Button(self.label2, font=("Lucida Grande", 13), height=100, width=6, command=send_file, text='Attach')
        self.file_button.pack(side="right", pady=35)


        self.make_button = tkinter.BooleanVar(value=False)
        self.make_button.trace("w", self.insert_button)

    def insert_button(self, *args):
        self.chat_log.window_create(tkinter.END, window=tkinter.Button(self.chat_log, text="download", command=self.something))
        self.chat_log.insert(END, "\n")

    def change_make_button(self):
        self.make_button.set(True)


    def make_download_button(self, file_name, file_id, conv_filesize, file_size):

        self.chat_log.window_create(tkinter.END, window=tkinter.Button(self.chat_log, text=f"Download {file_name} - {conv_filesize}", command=lambda arg1=file_name, arg2=file_id, arg3=file_size: request_file(arg1, arg2, arg3)))
        global makebutton
        makebutton = False

    def start(self):
        try:
            self.window.mainloop()
        except KeyboardInterrupt as e:
            print('program closed from terminal')
        print('program fininshed')
        os._exit(0)


def main():
    try:
        global gui
        if os.path.exists('credential.json'):
            with open('credential.json') as f:
                credential = json.load(f)
                token = credential['token']
                host = credential['host']
                port = credential['port']
                result = connect_to_server(host, port, '', '', token)
                if result == 0:
                    print("reconnection was successful")
                    open_chat_gui()
                elif result == 2:
                    print('could not open the socket with credentials')
                    gui = JoinGui()
                    gui.start()
                elif result == 5:
                    print('this user is already logged in')
                    gui = JoinGui()
                    gui.start()
                else:
                    print('token was invalid')
                    gui = JoinGui()
                    gui.start()
                f.close()
        else:
            gui = JoinGui()
            gui.start()
    except KeyboardInterrupt as e:
        print("program ended by user")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
