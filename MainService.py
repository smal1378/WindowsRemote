import os
import select
import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "TestService"
    _svc_display_name_ = "Test Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        s = socket.socket()
        s.setblocking(False)
        s.bind(("", 8085))
        s.listen()
        potential_readers = []
        logged_in = []
        new_conn = []
        while True:  # mainloop
            ready_to_read, ready_to_write, in_error = select.select(potential_readers + [s],
                                                                    potential_readers,
                                                                    potential_readers, 60)
            time.sleep(2)
            for conn in in_error:
                potential_readers.remove(conn)
                conn.close()
            if in_error:
                continue
            for conn in new_conn:
                if conn in ready_to_write:
                    conn.sendall(b"LOGIN;")
                    new_conn.remove(conn)
            for conn in ready_to_read:
                conn: socket.socket
                if conn == s:
                    new = s.accept()[0]
                    potential_readers.append(new)
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
                        x = ""  # Yes Ofcourse! I know that a half received command will mess everything.
                        # TODO: Fix it
                        for i in data:  # this is end of command character
                            if chr(i) == ";":
                                if self.command(x):
                                    conn.sendall(b"DONE;")
                                else:
                                    conn.sendall(b"FAIL;")
                                x = ""
                            else:
                                x += chr(i)
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
        else:
            return False
        return True

    @staticmethod
    def login(info):
        if info == b"123;":
            return True
        return False


if __name__ == '__main__':
    # win32serviceutil.HandleCommandLine(AppServerSvc)
    AppServerSvc.main(AppServerSvc)
