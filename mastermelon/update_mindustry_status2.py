from socket import socket, create_connection, AF_INET, SOCK_DGRAM
from struct import unpack
from time import time
import sys
import threading
from time import sleep
# !{sys.executable} -m pip install --upgrade pip
# !{sys.executable} -m pip install wrapt_timeout_decorator
from wrapt_timeout_decorator import timeout
import discord
from multiprocessing import Pool


class Server:
    def __init__(self, host, server_port=6567, socketinput_port=6859):
        self.host = host
        self.server = (host, server_port)
        self.socketinput_port = socketinput_port

    @timeout(5)
    def get_status(self):
        # if self.server[1] == 25586:
        #    print("long server delay")
        #    sleep(7)
        statusdict = {}
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.connect(self.server)
            s.send(b"\xfe\x01")
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
            statusdict["status"] = "Online"
        return statusdict


server_data = [  # ("HUB", "alexmindustryhub.ddns.net", 6568, "ALEXHOST"),
    ("PVP V7", "alexmindustryattac.ddns.net", 6767, "LINODESG"),
    ("SURVIVAL V7", "alexmindustryattac.ddns.net", 6768, "LINODESG"),
    ("HUB V7", "alexmindustryhub.ddns.net", 6565, "ALEXHOST"),
    ("SANDBOX", "alexmindustrysandbox.ddns.net", 25580, "HOSTMC"),
    ("TURBO PVP", "alexmindustryturbo.ddns.net", 25581, "HOSTMC"),
    ("PVP USA WEST", "dogemindustry.ddns.net", 25586, "LINODEUSWEST"),
    # ("PVP ASIA", "alexmindustryattac.ddns.net", 25800, "LINODESG"),
    ("HEX", "alexmindustryhex.ddns.net", 25583, "LINODESG"),
    ("PVP ASIA", "alexmindustryattac.ddns.net", 25800, "LINODESG"),
    ("ATTACK", "alexmindustryattac2.ddns.net", 25582, "HOSTMC"),
    ("PVP", "alexmindustry.ddns.net", 25586, "HOSTMC"),
    ("SURVIVAL", "alexmindustry.ddns.net", 25587, "HOSTMC")]


def fetch_single_data(x):
    name, host, port, servertype = x
    serr = Server(host, port)
    try:
        res = serr.get_status()
        return [name, host, port, servertype, res]
    except TimeoutError:
        return [name, host, port, servertype, {"status": "time out error"}]
    except ConnectionRefusedError:
        return [name, host, port, servertype, {"status": "connection refused error"}]
    except Exception as e:
        return [name, host, port, servertype, {"status": "exception occurred"}]


def fetch_data():
    with Pool() as pool:
        full_string = pool.map(fetch_single_data, server_data)
    return full_string


def spsb(stringg):
    # strip paired square brackets
    result = ""
    flag = False
    for s in stringg:
        if s == "[" and not flag:
            flag = True
        elif flag and s == "]":
            flag = False
        elif not flag:
            result += s
    return result


def get_embed(fetched_data_single):
    name, host, port, servertype, res = fetched_data_single
    embed = discord.Embed(colour=discord.Colour(value=65280) if res["status"] == "Online" else discord.Colour(value=16726072))
    if res["status"] == "Online":
        name = res["name"]
        p = int(res['players'])
        pstring = f"{p} Players" if p > 1 else f"{p} Player"
        embed.add_field(name=spsb(name) + f" Online ({pstring})",
                        value=f"```css\n[Map] {spsb(res['map'])} [Wave] {res['wave']}\n[IP] {host}:{port}  [{servertype}]\n```")
    else:
        embed.add_field(name=spsb(name) + " Offline",
                        value=f"```css\n[IP] {host}:{port} \n[{servertype}] Offline: {res['status']}```")
    return embed


async def update_data(ctx, fetched_data: list(), channel_fetch: discord.TextChannel):
    #print("inside update data")
    #print(channel_fetch.name)
    messages = await channel_fetch.history(limit=15).flatten()
    message: discord.Message
    for fetched_data_single in fetched_data:
        #print(fetched_data_single)
        name, host, port, servertype, res = fetched_data_single
        updated = False
        for message in messages:
            if updated:
                break
            embeded: discord.Embed
            for embeded in message.embeds:
                if updated:
                    break
                check = f"{host}:{port}" in embeded.fields[0].value or f"{host}:{port}" in embeded.fields[0].name
                if check and (servertype in embeded.fields[0].value):
                    await message.edit(embed=get_embed(fetched_data_single))
                    updated = True
        if not updated:
            await channel_fetch.send(embed=get_embed(fetched_data_single))
    #print("end data")
