#!/usr/bin/env python3

"""
|=====================================|
| Classes for enable communication    |
| between a Raspberry and a computer. |
|=====================================|
"""

import ipaddress
import os
import pickle
import queue
import socket
import subprocess
import sys
import threading
import time

import interface


PORT = 1234 # This can be any number 


class Server:
    """
    Server that should run on a Raspberry.
    """
    def __init__(self):
        """
        Initialisation using IPV6 and IPV4 protocols.
        """
        interface.move_wheel("", 0) # Stop wheels.
        self.clients = {} # List of connected clients
        self.tcp_socket = socket.create_server(("", PORT),
            family=socket.AF_INET6, dualstack_ipv6=True, reuse_port=True) # Blend ipv4 and ipv6 python >= 3.8

        self.tcp_socket.listen(2) # Only two connections can wait in queue
        print("Listening port %d ..." % PORT)

    def salon(self, client_socket):
        """
        Method to be launched in a thread, if it's a client.
        """
        while True:
            data = client_socket.recv(1024)
            if data:
                print("Received message :")
                print(data)
                message = pickle.loads(data)
                print("\t%s", message)
                try:
                    interface.move_wheel(*message["args"], **message["kwargs"])
                except Exception as e:
                    sys.stderr.write(str(e))

    def ecoute(self):
        """
        Main method, create a room on the fly.
        """
        while True:
            client_socket, info = self.tcp_socket.accept() # We can't directly write :
            ip_client = info[0]                    # client_socket, (ip_client, port_client)
            port_client = info[1]                  # Because the second tuple may content 4 elements.
            print("A client is connecting on port %d, ip %s." % (port_client, ip_client))

            self.clients[ip_client] = {
                "thread": threading.Thread(target=self.salon, args=(client_socket,)),
                "socket": client_socket}
            self.clients[ip_client]["thread"].start()

    def close(self):
        """
        Close every connections.
        """
        for ip in self.clients:
            try:
                self.clients[ip]["socket"].shutdown(socket.SHUT_RDWR)
                self.clients[ip]["socket"].close()
            except OSError:
                pass
        if hasattr(self, "tcp_socket"): # If the constructor does not fail.
            self.tcp_socket.close()

    def __del__(self):
        self.close()

class Client:
    """
    |========================================|
    | A client that automaticaly connect to  |
    | a Raspberry server.                    |
    |========================================|
    """
    def __init__(self, ip=None):
        """
        |====================|
        | Init a connection. |
        |====================|
        """
        if not ip:
            self.ip, self.port = self.scan()
        else:
            self.ip = ip
            self.port = PORT
        print(self.ip, self.port)
        self.tcp_socket = socket.create_connection((self.ip, self.port))

    def get_ipv4_lan(self):
        """
        Return IP on the local network.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        # un socket en mode UDP (DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)     # broadcast
            s.connect(("<broadcast>", 0))                               # le mot-cle python pour INADDR_BROADCAST
            ip_local, port = s.getsockname()                            # renvoi de l'adresse source
            return str(ipaddress.IPv4Address(ip_local))                      # on retourne donc la vrai adresse
        except socket.error:                                            # mais l'on est pas certain que cette methode fonctionne a tous les coups
            return None                                                 # c'est pour cela que l'on prend des precautions

    def scan(self):
        """
        |===============================|
        | Search a listening Raspberry. |
        |===============================|

        Returns
        -------
        :return: ip, port couple
        :rtype: tuple
        """
        def scanip(ip, server_queue):
            """Scan only one ip."""
            try:
                hostname, alias, addresslist = socket.gethostbyaddr(ip)
            except socket.herror: # A fail doesn't mean there are no server listening.
                if subprocess.run("ping -c 1 %s" % ip,
                        shell=True, capture_output=True).returncode:
                    return False
                hostname, addresslist = ip, [ip]

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if 0 == sock.connect_ex((ip, PORT)):
                sock.close()
                print("port %d for %s is open." % (PORT, repr(hostname)))
                server_queue.put((ip, PORT))
                return True
            sock.close()
            return False

        server_queue = queue.Queue() # Fifo queue.
        ip_base = ".".join(self.get_ipv4_lan().split(".")[:-1]) + ".%d" # Model for IP to scan.
        threads = [] # Thread list

        if os.path.exists("ip_rasp.txt"):
            with open("ip_rasp.txt", "r") as f:
                if scanip(f.read(), server_queue):
                    return server_queue.get()

        for addr in (ip_base % i for i in range(256)):
            if not server_queue.empty():
                break
            while True:
                if threading.active_count() < 32: # Number of simulataneous threads.
                    threads.append(threading.Thread(target=scanip, args=(addr, server_queue)))
                    threads[-1].start()
                    break
                else:
                    time.sleep(1)
                    threads = [th for th in threads if th.is_alive()]

        # Waiting for a result...
        while server_queue.empty() and threads:
            time.sleep(1)
            threads = [th for th in threads if th.is_alive()]

        # If there is a result :
        if server_queue.empty():
            raise ConnectionError("No server found !")
        ip, port = server_queue.get()
        with open("ip_rasp.txt", "w") as f:
            f.write(ip)
        return ip, port

    def move_wheel(self, *args, **kwargs):
        """
        Alias to move_wheel of the Rapsberry.
        """
        data = pickle.dumps({"args": args, "kwargs": kwargs})
        self.tcp_socket.sendall(data)
