
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import socket
import sys


def main():
    try:
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
        print("success")
        port = 80

        try:
            host_ip = socket.gethostbyname('www.google.com')
        except socket.gaierror:
            # this means could not resolve the host
            print("there was an error resolving the host")
            sys.exit()
        # connecting to the server
        print("host ip is " + str(host_ip))
        sock.connect((host_ip, port))

        print("the socket has successfully connected to google")
    except socket.error as e:
        print(e)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
