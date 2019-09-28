import socket
import sys
import select
import constants as const


class HostLinkProtocol():
    def __init__(self, host, port):
        self.__port = port
        self.__host = host
        self.__sock = None
        self.__timeout = 30.0
        self.__debug = True

    def timeout(self, timeout=None):
        if timeout is None:
            return self.__timeout
        if 0 < float(timeout) < 3600:
            self.__timeout = float(timeout)
            return self.__timeout
        else:
            return None

    def __send(self, message):
        if (self.__sock is None):
            self.__printMsg("can't send TCP is None")
            return None
        value = None
        try:
            value = self.__sock.send(message)
        except socket.error:
            self.__printMsg("Hostlink send error")
            self.close()
            return None
        return value

    def open(self):
        if self.is_open():
            self.close()

        for res in socket.getaddrinfo(self.__host, self.__port,
                                      socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, sock_type, proto, canon_name, sa = res
            try:
                self.__sock = socket.socket(af, sock_type, proto)
            except socket.error:
                self.__sock = None
                continue
            try:
                self.__sock.settimeout(self.__timeout)
                self.__sock.connect(sa)
            except socket.error:
                self.__sock.close()
                self.__sock = None
                continue
            break

        if self.__sock is not None:
            return True
        else:
            self.__printMsg("connect error")
            return False

    def _can_read(self):
        if self.__sock is None:
            return None
        if select.select([self.__sock], [], [], self.__timeout)[0]:
            return True
        else:
            self.__printMsg('timeout error')
            self.close()
            return None

    def is_open(self):
        return self.__sock is not None

    def __printMsg(self, msg):
        if self.__debug == True:
            print(msg)

    def close(self):
        if self.__sock:
            self.__sock.close()
            self.__sock = None
            return True
        else:
            return None

    def __recv(self):
        # wait for read
        if not self._can_read():
            self.close()
            return None
        # recv
        try:
            r_buffer = self.__sock.recv(const.BUFFER_SIZE)
        except socket.error:
            r_buffer = None
        # handle recv error
        if not r_buffer:
            self.__printMsg('_recv error')
            self.close()
            return None

        return r_buffer

    def requestDataRead(self, addr):
        message = "RD " + addr + ".D\r"
        if self.__send(message) is None:
            return None

        data = self.__recv()
        if data is None:
            return None

        return int(data)

    def requestContinuousDataRead(self, addr, length):
        """
            request continuous data
            return array of data
        """
        message = "RDS " + addr + " " + str(length) + "\r"
        if self.__send(message) is None:
            return None

        data = self.__recv()
        if data is None:
            return None
        self.__printMsg("data is " + data)
        arr = data.split(' ')
        for i in range(len(arr)):
            try:
                arr[i] = int(arr[i])
            except ValueError:
                self.__printMsg("casting error")
                return None

        return arr

    # def requestContinuousDataWrite(self, addr, length):
    #     pass

    # def requestDataWrite(self, addr, value):
    #     pass
