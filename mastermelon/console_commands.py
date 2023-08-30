import asyncio
import subprocess
import traceback 
from discord.ext import commands

def send_consolecommand(host: str, cmd: str):
    subprocess.Popen(f"ssh {host} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return 

def read_consoleoutput(host: str, cmd: str):
    procc = subprocess.Popen(f"ssh {host} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = procc.communicate()
    return out,err

def getservers(): # host screen port
    servers = [("root@alexmindustryv7.servegame.com", "pvp_v7_2023"       , "25588", "LD USA"),
               ("root@alexmindustryv7.servegame.com", "attack_usw_v7_2023", "41962", "LD USA"),
               ("root@alexmindustrypvp.ddns.net"    , "pvp_v7_asia"       , "6767" , "LD ASI"),
               ("root@alexmindustrypvp.ddns.net"    , "surv_v7"           , "6768" , "LD ASI")]
    return [(i,host,screen,port,loc) for i,(host,screen,port,loc) in enumerate(servers)]

def servfolders():
    return [
        "/root/Documents/pvp_v7_2023",
        "/root/Documents/attack_usw_v7_2023",
        "/root/Documents/pvp_v7_asia",
        "/root/Documents/surv_v7"
    ]

async def restartserver(ctx: commands.Context, serverid: int):
    servers = getservers()
    try:
        i,host,screen,port,loc = servers[serverid]
        await ctx.channel.send(f"sending gameover command to `{i}` `{host}{port}` with screen `{screen}`, waiting 2 seconds")
        cmd =f'screen -S {screen} -p 0 -X stuff "gameover^M"'
        send_consolecommand(host, cmd)
        await asyncio.sleep(2)
        await ctx.channel.send(f"sending exit command to `{i}` `{host}{port}` with screen `{screen}`")
        cmd =f'screen -S {screen} -p 0 -X stuff "exit^M"'
        send_consolecommand(host, cmd)
        await asyncio.sleep(2)
        await ctx.channel.send(f"Completed restart for `{i}` `{host}{port}` `{screen}`")
    except Exception as e:
        strr=traceback.format_exc()
        await ctx.channel.send("error occurred 32:" + str(e)+"tb:"+strr)
    else: 
        pass # todo delete those msgs if passed

async def readserver(ctx: commands.Context, serverid: int):
    servers = getservers()
    try:
        i,host,screen,port,loc = servers[serverid]
        await ctx.channel.send(f"reading console on `{i}` `{host}{port}` with screen `{screen}`", delete_after=3)
        cmd =f'screen -S {screen} -p 0 -X hardcopy -h "screen_log.log"'
        send_consolecommand(host, cmd)
        await asyncio.sleep(1)
        fld=servfolders()[i]
        cmd =f'cat {fld}/screen_log.log'
        out,err = read_consoleoutput(host, cmd)
        output = str(out[-100:])[2:-1].split("\n") #"\n".join([str(out[-500:]).split("\n")])
        print(output)
        print("\n".join(output))
        await ctx.channel.send( f"`{host}{port}` `{screen}`:\n"+ "\n".join(output))
        await ctx.channel.send(f"Completed reading for `{i}` `{host}{port}` `{screen}`")
    except Exception as e:
        strr=traceback.format_exc()
        await ctx.channel.send("error occurred 45:" + str(e)+"tb:"+strr)
    else: 
        pass # todo delete those msgs if passed

def getgame_status():
    # todo, gets the game status, and if it is available for restart
    return

def queueforrestart():
    # todo command to wait for the game to be over and then initiate the restart
    return

async def getserver(ctx: commands.Context):
    servers = getservers()
    strr = [f"`ID:{s1:>3}, {s2:<30}, screen={s3:<10}, port= {s4:<5} , owner:{s5}`" for s1, s2, s3, s4, s5 in servers]
    await ctx.channel.send("\n".join(strr))
