from socket import socket, create_connection, AF_INET, SOCK_DGRAM
from struct import unpack
from time import time
import sys
import threading
from time import sleep
# !{sys.executable} -m pip install --upgrade pip
# !{sys.executable} -m pip install wrapt_timeout_decorator
from wrapt_timeout_decorator import timeout


class Server():
    def __init__(self, host, server_port=6567, socketinput_port=6859):
        self.host = host
        self.server = (host, server_port)
        self.socketinput_port = socketinput_port

    @timeout(5)
    def get_status(self):
        if self.server[1] == 25586:
            print("long server delay")
            sleep(7)
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(self.server)
        s.send(b"\xfe\x01")
        statusdict = {}
        data = s.recv(1024)
        statusdict["name"] = data[1:data[0] + 1].decode("utf-8")
        data = data[data[0] + 1:]
        statusdict["map"] = data[1:data[0] + 1].decode("utf-8")
        data = data[data[0] + 1:]
        statusdict["players"] = unpack(">i", data[:4])[0]
        data = data[4:]
        statusdict["wave"] = unpack(">i", data[:4])[0]
        data = data[4:]
        statusdict["version"] = unpack(">i", data[:4])[0]
        data = data[4:]
        statusdict["vertype"] = data[1:data[0] + 1].decode("utf-8")
        return statusdict


server_data = [("HUB", "alexmindustryhub.ddns.net", 6568),
               ("SANDBOX", "alexmindustrysandbox.ddns.net", 25580),
               ("TURBO PVP", "alexmindustryturbo.ddns.net", 25581),
               ("PVP USA WEST", "dogemindustry.ddns.net", 25586),
               ("PVP ASIA", "alexmindustryattac.ddns.net", 25800),
               ("HEX", "alexmindustryhex.ddns.net", 25583),
               ("ATTACK", "alexmindustryattac2.ddns.net", 25582),
               ("PVP", "alexmindustry.ddns.net", 25586),
               ("SURVIVAL", "alexmindustry.ddns.net", 25587)]
async def fetch_data():
    full_string = []
    for name, host, port in server_data:
        serr = Server(host, port)
        try:
            res = serr.get_status()
            #print(name, host, port)
            #print(res)
            full_string.append([name, host, port, res])
        except TimeoutError:
            #print("time out error")
            full_string.append([name, host, port, "time out error"])
            pass
        except ConnectionRefusedError:
            full_string.append([name, host, port, "connection refused error"])
            pass
        except Exception as e:
            full_string.append([name, host, port, "Exception occurred"])
    for val in full_string:
        print(val)
    return full_string

async def update_data(fetched_data:list(),channel:int):
    return "hehe"
