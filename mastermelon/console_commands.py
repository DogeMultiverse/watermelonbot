import discord
import requests
import json
import asyncio
import requests
from discord.ext import commands


def getserver_token():
    with open("watermelon.config", "rb") as f:
        js = json.load(f)
        host_server_token = js["host_server_token"]
        host_server_baseurl = js["host_server_baseurl"]
    return host_server_token, host_server_baseurl


def send_consolecommand(server_key: str, consolecommand: str):
    host_server_token, host_server_baseurl = getserver_token()
    url = host_server_baseurl + 'api/client/servers/' + server_key + '/command'
    headers = {
        "Authorization": f"Bearer {host_server_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"}
    payload = '{  "command": "' + consolecommand + '" }'
    response = requests.request('POST', url, data=payload, headers=headers)
    return response


def getservers():
    host_server_token, host_server_baseurl = getserver_token()
    url = host_server_baseurl + 'api/client'
    headers = {
        "Authorization": f"Bearer {host_server_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"}
    response = requests.request('GET', url, headers=headers)
    return [(i, s["attributes"]["name"], s["attributes"]["identifier"], s["attributes"]["server_owner"]) for i, s in
            enumerate(response.json()["data"])]


def send_powersignal(server_key: str, signal: str):
    host_server_token, host_server_baseurl = getserver_token()
    url = host_server_baseurl + 'api/client/servers/' + server_key + '/power'
    headers = {
        "Authorization": f"Bearer {host_server_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"}
    payload = '{  "signal": "' + signal + '" }'
    response = requests.request('POST', url, data=payload, headers=headers)
    return response


async def restartserver(ctx: commands.Context, serverid: int, servercommand: str = "hubkick"):
    servers = getservers()
    try:
        serverkey = servers[serverid][2]
        await ctx.channel.send(f"sending servercommand to {servers[serverid][1]}, waiting 2 seconds")
        send_consolecommand(serverkey, servercommand)
        await asyncio.sleep(4)
        await ctx.channel.send("sending stop console, waiting 2 seconds")
        send_powersignal(serverkey, "stop")
        await asyncio.sleep(2)
        await ctx.channel.send("sending kill console, waiting 6 seconds")
        send_powersignal(serverkey, "kill")
        await asyncio.sleep(8)
        await ctx.channel.send("sending start console")
        send_powersignal(serverkey, "start")
        await ctx.channel.send(f"Completed restart for {servers[serverid][1]}")
    except Exception as e:
        await ctx.channel.send("error occurred:" + str(e))
    else:
        # todo delete those msgs if passed
        pass


async def getserver(ctx: commands.Context):
    servers = getservers()
    strr = [f"`{s1:>3}  {s2:<30}  , id= {s3:<10} , owner:{s4}`" for s1, s2, s3, s4 in servers]
    await ctx.channel.send("\n".join(strr))
