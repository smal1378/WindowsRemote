import os

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "TestService"
    _svc_display_name_ = "Test Service"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        s = socket.socket()
        s.bind(("", 8085))
        s.listen()
        while True:
            conn, addr = s.accept()
            login = conn.recv(2048)
            if not self.login(login):
                conn.sendall(b"WRONG")
                conn.close()
            else:
                conn.sendall(b"OK")
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        conn.sendall(b"RECEIVED")
                        for i in data.split(b";"):  # this is the seperator
                            self.command(i)

    @staticmethod
    def command(data):
        print("DEBUG: command ", data, "received")
        if data.lower().strip() == b"shutdown":
            os.system("shutdown /s /t 60")

    @staticmethod
    def login(info):
        if info == b"123;":
            return True
        return False


if __name__ == '__main__':
    # win32serviceutil.HandleCommandLine(AppServerSvc)
    AppServerSvc.main(AppServerSvc)
