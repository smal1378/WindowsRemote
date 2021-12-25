import os
import select
import socket


class Service:
    def __init__(self):
        self.s = s = socket.socket()
        s.setblocking(False)
        s.bind(("", 8085))
        s.listen()

    def mainloop(self):
        s = self.s
        potential_readers = []
        buffers = []  # for each socket in potential_readers list there is a buffer here
        logged_in = []
        new_conn = []
        while True:  # mainloop
            ready_to_read, ready_to_write, in_error = select.select(potential_readers + [s],
                                                                    new_conn, potential_readers, 2)
            for conn in in_error:
                potential_readers.remove(conn)
                conn.close()
            if in_error:
                continue
            for conn in ready_to_write:
                conn.sendall(b"LOGIN;")
                new_conn.remove(conn)
            for conn in ready_to_read:
                conn: socket.socket
                if conn == s:
                    new = s.accept()[0]
                    potential_readers.append(new)
                    buffers.append("")
                    new_conn.append(new)
                elif conn not in logged_in:
                    try:
                        login = conn.recv(2048)
                    except (ConnectionAbortedError, ConnectionResetError):
                        conn.close()
                        potential_readers.remove(conn)
                        continue
                    if not self.login(login):
                        conn.sendall(b"WRONG;")
                    else:
                        logged_in.append(conn)
                        conn.sendall(b"OK;")
                    continue
                else:
                    try:
                        data = conn.recv(1024)
                    except (ConnectionAbortedError, ConnectionResetError):
                        conn.close()
                        potential_readers.remove(conn)
                        continue
                    if data:
                        x = buffers[potential_readers.index(conn)]
                        for i in data:
                            if chr(i) == ";":
                                if self.command(x):
                                    conn.sendall(b"DONE;")
                                else:
                                    conn.sendall(b"FAIL;")
                                x = ""
                            else:
                                x += chr(i)
                        buffers[potential_readers.index(conn)] = x
                    else:
                        conn.close()
                        potential_readers.remove(conn)

    @staticmethod
    def command(data: str):
        if data.lower().strip() == "shutdown":
            os.system("shutdown /s /t 60")
        elif data.lower().strip() == "hibernate":
            os.system("shutdown /h")
        elif data.lower().strip() == "exit":
            exit()
        elif data.lower().strip() == "ping":
            pass
        else:
            return False
        return True

    @staticmethod
    def login(info):
        if info == b"123;":
            return True
        return False


if __name__ == '__main__':
    service = Service()
    service.mainloop()
