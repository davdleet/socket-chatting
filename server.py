# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys
import threading
import urllib.request
import ssl
import tkinter
import os
import random
import string
from tkinter import *
from tkinter import messagebox
from threading import Thread
import math
import errno
from tkinter import filedialog
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
ssl._create_default_https_context = ssl._create_unverified_context
external_ip = urllib.request.urlopen('https://ident.me/').read().decode('utf8')

HOST = None
PORT = None
server_pw = None
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
sock = None
serverGui = None
threads = []
started = False
stop_server = False
listen_thread = None
clients = []

file_id = 1

user_tokens = {}
online_tokens =[]

def setup():
    global sock
    global HOST
    global PORT
    global server_pw
    try:
        PORT = serverGui.port_value.get()
        server_pw = str(serverGui.password_value.get())
        server_pw = server_pw + (' ' * (1024 - len(server_pw)))
        print("The server password is: " + str(server_pw.rstrip()))
        if PORT == "":
            raise Exception("Enter a valid port number")
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
        #messagebox.showerror("Error!", e)
        sys.exit(1)


def start_server():
    setup()
    if sock is None:
        print("could not open socket")
        return
    print("starting socket...")
    start_socket()
    return

def b_string_fill(bstring, size):
    fill_size = size - len(bstring)
    fill = b' ' * fill_size
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
        result = result + s.recv(length - len(result))
    return result

def send_bytes(s, bstring, length):
    s.send(b_string_fill(bstring, length))

def listen_loop():
    try:
        while True:
            # connection from client
            conn, addr = sock.accept()
            print('connected by', addr)

            # size is 16
            conn_token = conn.recv(16)
            decoded_conn_token = conn_token.decode('ascii')

            if decoded_conn_token == '****************':
                print(f'no token provided from {addr}')
            else:
                if decoded_conn_token in user_tokens.keys():
                    if decoded_conn_token in online_tokens:
                        print('duplicate token was provided')
                        conn.send(b'DUP')
                        continue
                    conn_username = user_tokens[decoded_conn_token]
                    print(f'{conn_username}:{decoded_conn_token} reconnected with credential token')
                    conn.send(b'SCS')
                    clients.append(conn)
                    bc_msg = f'{conn_username} reconnected\n'
                    broadcast(bc_msg.encode('ascii'))
                    online_tokens.append(decoded_conn_token)
                    rcv_thread = Thread(target=receiver, args=(conn, addr, conn_username, decoded_conn_token, 0))
                    rcv_thread.start()
                    continue
                else:
                    print('invalid token provided')
                    print(decoded_conn_token)
                    conn.send(b'INV')
                    continue


            # password verification
            entered_pw = receive_bytes(conn, 1024)
            #entered_pw = conn.recv(1024)
            decoded_entered_pw = entered_pw.decode('ascii')
            if str(decoded_entered_pw) != str(server_pw):
                pw_msg = 'WPW'
                encoded_pw_msg = pw_msg.encode('ascii')
                conn.send(encoded_pw_msg)
                print(f'password authentication for {addr} failed')
                continue
            else:
                pw_msg = 'SCS'
                encoded_pw_msg = pw_msg.encode('ascii')
                conn.send(encoded_pw_msg)
                print(f'password authentication for {addr} was successful')

            # get a username from the user
            username = receive_bytes(conn, 1024)
            # username = conn.recv(1024)
            username = username.rstrip()
            decoded_username = username.decode('ascii')
            list_entry = f"{addr[0] : <40}{addr[1] : <19}{decoded_username : <20}\n"
            serverGui.list.insert(END, list_entry)
            clients.append(conn)

            client_token = generate_token()
            while client_token in user_tokens:
                client_token = generate_token()
            user_tokens[client_token] = username.decode('ascii')
            conn.send(client_token.encode('ascii'))

            bc_new = f'{decoded_username} joined the room\n'
            broadcast(bc_new.encode('ascii'))

            online_tokens.append(client_token)

            rcv_thread = Thread(target=receiver, args=(conn, addr, decoded_username, client_token, 0))
            rcv_thread.start()
    except ConnectionAbortedError as e:
        #messagebox.showinfo('info', 'Server closed')
        print("Server closed by admin")
        global stop_server
        stop_server = True
    except ConnectionResetError as e:
        print('connection reset while connecting with client')

def generate_token():
    token = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))
    return token

def start_socket():
    #messagebox.showinfo('info', 'Server is opened')
    print("server opened!")
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



def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def send_to_client(conn, header, body):
    conn.send(f'{header}{body}'.encode('ascii'))

def receiver(conn, addr, username, token, count):
    connected = True
    global file_id
    if count == 0:
        None
    try:
        while started:
            message = receive_bytes(conn, 4096)
            # message = conn.recv(4096)
            decoded_message = message.decode('ascii')
            # usable_message = decoded_message.replace('[END]', '')
            decoded_message = decoded_message.rstrip()
            split_messages = decoded_message.split('[END]')
            usable_message = split_messages[0]
            received_header = usable_message[0:5]
            received_body = usable_message[5:]
            if received_header == "[MSG]":
                merged_message = ('[MSG]' + str(username) + ' : ' + received_body + '[END]')
                print(f'user message - {username} : {received_body}', end='')
                if received_body == '/quit\n':
                    if conn in clients:
                        clients.remove(conn)
                    if user_tokens[token]:
                        del user_tokens[token]
                    conn.close()
                    leave_bc = f'{username} left the room'
                    broadcast(leave_bc.encode('ascii'))
                    return
                reencoded_message = merged_message.encode('ascii')
                broadcast(reencoded_message)
            elif received_header == "[FRQ]":
                print(f"{username} requested {received_body}")
                to_send = received_body
                send_size = os.path.getsize(f'files/{to_send}')
                ack = f'[FDN]{received_body}{SEPARATOR}{send_size}[END]'
                filler_len = 4096 - len(ack)
                filler = ' ' * filler_len
                ack = ack + filler
                encoded_ack = ack.encode('ascii')
                conn.send(encoded_ack)
                requested_file = received_body
                send_file(requested_file, conn)
            elif received_header == "[FUP]":
                recv_file(conn, received_body)
                current_file_id = file_id
                file_id = file_id + 1
                recv_body_split = received_body.split(SEPARATOR)
                recv_file_name = recv_body_split[0]
                print(f"{username} uploaded {recv_file_name} file_id: {current_file_id}")
                recv_file_size = int(recv_body_split[1])
                converted_file_size = convert_size(int(recv_body_split[1]))
                merged_message = '[MSG]' +str(username) + ':' + '[END]'
                reencoded_message = merged_message.encode('ascii')
                broadcast(reencoded_message)
                broadcast_file(recv_file_name, current_file_id, converted_file_size, recv_file_size)
    except (ConnectionResetError, BrokenPipeError, TimeoutError) as e:
        if conn in clients:
            clients.remove(conn)
        if token in online_tokens:
            online_tokens.remove(token)
        print(username + ' disconnected')
    except Exception as e:
        send_to_client(conn, '', 'An error occurred processing your last request.\n')
        receiver(conn, addr, username, token, count+1)
    print(f"connection lost with {addr}")
    disconnected_bc = f'{username} disconnected\n'
    broadcast(disconnected_bc.encode('ascii'))


def broadcast(message):
    for client in clients:
        send_bytes(client, message, 4096)
        # client.send(message)

def broadcast_file(filename, current_file_id, conv_filesize, filesize):
    msg = '[FBC]' +str(filename) + SEPARATOR +str(current_file_id)+SEPARATOR+str(conv_filesize) + SEPARATOR +str(filesize)+'[END]'
    encoded_msg = msg.encode('ascii')
    for client in clients:
        send_bytes(client, encoded_msg, 4096)
        #client.send(encoded_msg)


def send_file(filename, conn):
    with open(f'files/{filename}', 'rb') as f:
        bytes_read = None

        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            conn.sendall(bytes_read)
        f.close()

def recv_file(conn, received):
    global file_id
    filename, filesize = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)

    if not os.path.exists(os.path.dirname('files')):
        try:
            os.makedirs('files')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    if filesize == 0:
        f = open('files/'+str(file_id)+'-'+filename, "wb")
        f.close()
        return
    else:
        with open('files/'+str(file_id)+'-'+filename, "wb") as f:

            remaining_count = int(filesize)
            bytes_read = None
            while True:
                if remaining_count == 0:
                    break
                elif BUFFER_SIZE > remaining_count > 0:
                    bytes_read = conn.recv(remaining_count)
                    while len(bytes_read) != remaining_count:
                        bytes_read = bytes_read + conn.recv(remaining_count - len(bytes_read))
                    remaining_count = remaining_count - len(bytes_read)
                else:
                    bytes_read = conn.recv(BUFFER_SIZE)
                    while len(bytes_read) != BUFFER_SIZE:
                        bytes_read = bytes_read + conn.recv(BUFFER_SIZE - len(bytes_read))
                    remaining_count = remaining_count - len(bytes_read)
                f.write(bytes_read)

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
        #messagebox.showerror("error", "Server is already running!")
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

        self.title = tkinter.Label(self.window, bg='#252229', fg='white', font=("Arial", 25), text="Start a chatting Server")
        self.title.pack(pady=20)

        self.label1 = Label(self.window, bg='#252229', fg='white')
        self.label1.pack(fill="both", padx=20)

        self.server_ip = Label(self.label1, bg='#252229', fg='white', font=("Arial", 18), text="Server IP: ")
        self.server_ip.pack(side="left")

        self.server_ip_value = Label(self.label1, bg='#252229', fg='white', font=("Arial", 18), text=external_ip,
                        )
        self.server_ip_value.pack(side="left")

        self.label2 = Label(self.window, bg='#252229', fg='white')
        self.label2.pack(fill="both", padx=20)

        self.port = Label(self.label2, bg='#252229', fg='white', font=("Arial", 18), text="Port: ")
        self.port.pack(side="left")

        self.port_value = Entry(self.label2, bg='#252229', fg='white', bd=2, font=("Arial", 18), text="Port: ")
        self.port_value.pack(side="left")

        self.label3 = Label(self.window, bg='#252229', fg='white')
        self.label3.pack(fill="x", padx=20)

        self.password = Label(self.label3, bg='#252229', fg='white', font=("Arial", 18), text="Password: ")
        self.password.pack(side="left")

        self.password_value = Entry(self.label3, bg='#252229', fg='white', bd=2, font=("Arial", 18), text="Password: ")
        self.password_value.pack(side="left")

        self.label4 = Label(self.window, bg='#252229', fg='white', anchor="w", font=("Arial", 18),
                    text="Connected Clients")
        self.label4.pack(fill="x", padx=20, pady=10)

        self.label5 = Label(self.window, bg='#252229', fg='white')
        self.label5.pack(padx=20)

        self.list = Text(self.label5, bg='#252229', fg='white', height=20, wrap=None, font=("Fixedsys", 14),
            )
        self.list.pack(side="left")

        self.top_row = "{:<43}".format("Address") + "{:<20}".format("Port") + "{:<30}".format("Username") + "\n\n"
        self.list.insert(tkinter.END, self.top_row)

        self.scroll = Scrollbar(self.label5, orient="vertical", command=self.list.yview)
        self.scroll.pack(side='right', fill=Y)

        self.list.config(yscrollcommand=self.scroll.set)

        self.label6 = tkinter.Label(self.window)
        self.label6.pack(side="right", padx=20, pady=20)

        self.start_button = tkinter.Button(self.label6, font=("Arial", 18), command=start_threads, width=3, height=1,
                                      text="start")
        self.start_button.pack(side="right", ipadx=3, ipady=3)

        self.stop_button = tkinter.Button(self.label6, font=("Arial", 18), command=stop_server_button, width=3, height=1,
                                     text="stop")
        self.stop_button.pack(side="right", padx=20, ipadx=3, ipady=3)


    def start(self):
        self.window.mainloop()
        broadcast(b'Server Closed')
        os._exit(0)


serverGui = Gui()


def add_to_list(client_info):
    serverGui.list.insert(tkinter.END, str(client_info))
    serverGui.list.see('end')


def main():
    Gui.start(serverGui)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
