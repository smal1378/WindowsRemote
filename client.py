import socket
import select
import time
from time import sleep


class Remote:
    def __init__(self, address=("localhost", 8085)):
        self.address = address
        self.s = socket.socket()
        self.s.setblocking(False)
        self.s.connect_ex(address)

    def wait_readable(self, timeout: int = 5):
        if self.s in select.select([self.s], [], [], timeout)[0]:
            return True
        return False

    def wait_writable(self, timeout: int = 5):
        if self.s in select.select([], [self.s], [], timeout)[1]:
            return True
        return False

    def login(self, passwd='123'):
        if self.wait_readable() and self.s.recv(1024) == b'LOGIN;':
            if self.wait_writable():
                self.s.sendall(bytes(passwd+';', encoding='utf-8'))
                if self.wait_readable() and self.s.recv(1024) == b'OK;':
                    return True
        return False

    def send(self, command: str = 'ping'):
        if self.wait_readable(0):
            self.s.recv(1024)
        if self.wait_writable():
            self.s.sendall(bytes(command+';', encoding='utf-8'))
            if self.wait_readable() and self.s.recv(1024) == b'DONE;':
                return True
        return False


if __name__ == '__main__':
    while True:
        print("----- WindowsRemote Client -----")
        remote = Remote()
        print("Connecting to", remote.address)
        if not remote.wait_readable(10):
            print("Connection Failed, Restarting..")
            sleep(3)
            continue
        if not remote.login('123'):
            print("Login Failed. exiting..")
            exit()
        a = time.time()
        if not remote.send():
            print("Ping Failed. exiting..")
            exit()
        print(f"Connected. Ping:{round((time.time() - a) * 1000)}ms")
        while True:
            c = input("Command>>> ").lower().strip()
            if c == 'exit':
                exit()
            if c == 'reconnect' or c == 'restart':
                break
            if remote.send(c):
                print("Done.")
            else:
                print("Failed.")
