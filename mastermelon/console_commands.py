import asyncio
import subprocess 
from discord.ext import commands

def send_consolecommand(host: str, cmd: str):
    subprocess.Popen(f"ssh {host} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return 

def getservers(): # host screen port
    servers = [("root@alexmindustryv7.servegame.com", "pvp_v7_2023"       , "25588", "LD USA"),
               ("root@alexmindustryv7.servegame.com", "attack_usw_v7_2023", "41962", "LD USA"),
               ("root@alexmindustrypvp.ddns.net"    , "pvp_v7_asia"       , "6767" , "LD ASI"),
               ("root@alexmindustrypvp.ddns.net"    , "surv_v7"           , "6768" , "LD ASI")]
    return [(i,host,screen,port,loc) for i,(host,screen,port,loc) in enumerate(servers)]

async def restartserver(ctx: commands.Context, serverid: int):
    servers = getservers()
    try:
        i,host,screen,port,loc = servers[serverid]
        await ctx.channel.send(f"sending gameover command to {i} {host}{port} with screen {screen}, waiting 2 seconds")
        cmd =f'screen -S {screen} -p 0 -X stuff "gameover^M"'
        send_consolecommand(host, cmd)
        await asyncio.sleep(2)
        await ctx.channel.send(f"sending exit command to {i} {host}{port} with screen {screen}")
        cmd =f'screen -S {screen} -p 0 -X stuff "exit^M"'
        send_consolecommand(host, cmd)
        await asyncio.sleep(2)
        await ctx.channel.send(f"Completed restart for {i} {host}{port} {screen}")
    except Exception as e:
        await ctx.channel.send("error occurred:" + str(e))
    else:
        # todo delete those msgs if passed
        pass

def getgame_status():
    # todo, gets the game status, and if it is available for restart
    return

def queueforrestart():
    # todo command to wait for the game to be over and then initiate the restart
    return

async def getserver(ctx: commands.Context):
    servers = getservers()
    strr = [f"`{s1:>3}  {s2:<30}  , id= {s3:<10} , owner:{s4}`" for s1, s2, s3, s4 in servers]
    await ctx.channel.send("\n".join(strr))
