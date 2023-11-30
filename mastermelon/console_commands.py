import asyncio
import subprocess
import traceback 
from discord.ext import commands
from mastermelon.disc_constants import DUUID_ALEX

def send_consolecommand(host: str, cmd: str):
    subprocess.Popen(f"ssh {host} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return 

def ssh_withcmd(host: str, cmd: str):
    procc = subprocess.Popen(f"ssh {host} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = procc.communicate()
    return out,err

def scp_cmd(host:str, src: str, dst: str):
    procc = subprocess.Popen(f"scp {src} {host}:{dst}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = procc.communicate()
    return out,err

def getservers(): # host screen port
    servers = [
            #("root@alexmindustryv7.servegame.com", "pvp_v7_2023"       , "41962", "LD USA"),
            ("root@alexmindustryv7.servegame.com", "attack_usw_v7_2023", "25588", "RN USA"),
            ("root@172.245.187.143"              , "sandbox_usa"       , "6869" , "RN USA"),
            ("root@172.234.80.96"                , "surv_v7"           , "6768" , "LD JPY"),
            ("root@139.162.41.78"                , "pvp_v7_asia"       , "6767" , "LD SG2"),
            ("root@172.245.187.143"              , "pvp_usa"           , "6868" , "RN USA")
               ]
    #servers = servers
    return [(i,host,screen,port,loc) for i,(host,screen,port,loc) in enumerate(servers)]

def servfolders():
    return [
        #"/root/Documents/pvp_v7_2023",
        "/root/Documents/attack_usw_v7_2023",
        "/root/Documents/sandbox_usa",
        "/root/Documents/surv_v7",
        "/root/Documents/pvp_v7_asia",
        "/root/Documents/pvp_usa"
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
        await ctx.channel.send("error occurred 45:" + str(e)+"tb:"+strr)
    else: 
        pass # todo delete those msgs if passed

async def gameoverserver(ctx: commands.Context, serverid: int):
    servers = getservers()
    try:
        i,host,screen,port,loc = servers[serverid]
        await ctx.channel.send(f"sending gameover command to `{i}` `{host}{port}` with screen `{screen}` ")
        cmd =f'screen -S {screen} -p 0 -X stuff "gameover^M"'
        send_consolecommand(host, cmd) 
        await ctx.channel.send(f"sent gameover command for `{i}` `{host}{port}` `{screen}`")
    except Exception as e:
        strr=traceback.format_exc()
        await ctx.channel.send("error occurred 66:" + str(e)+"tb:"+strr)
    else: 
        pass # todo delete those msgs if passed

async def readserver(ctx: commands.Context, serverid: int):
    servers = getservers()
    try:
        i,host,screen,port,loc = servers[serverid]
        await showconsole(ctx, i, host, screen, port)
    except Exception as e:
        strr=traceback.format_exc()
        await ctx.channel.send("error occurred 67:" + str(e)+"tb:"+strr)
    else: 
        pass 

async def sendcommandtoserver(ctx: commands.Context, serverid: int, consolecommand: str, display: bool = True):
    # this sends command to server with "enter" at the end
    # will print the output after the command is ran
    # also, no js is allowed, unless by alex......
    if ctx.author.id != DUUID_ALEX:
        consolecommand = consolecommand.replace("js","")
    consolecommand = consolecommand.replace(" ","\ ")
    servers = getservers()
    try:
        if serverid==-1: # this sends to all
            for serverid in range(len( servers )):
                await send_command_to_1_server(ctx, serverid, consolecommand, servers, display)
        else: # just sends to 1
            await send_command_to_1_server(ctx, serverid, consolecommand, servers, display)
    except Exception as e:
        strr=traceback.format_exc()
        await ctx.channel.send("error occurred 82:" + str(e)+"tb:"+strr)
    else: 
        pass 

async def send_command_to_1_server(ctx, serverid, consolecommand, servers, display = True):
    i,host,screen,port,loc = servers[serverid]
    await ctx.channel.send(f"sending {consolecommand} to `{i}` `{host}{port}` with screen `{screen}`, waiting 2 seconds")
    send_consolecommand(host, f'screen -S {screen} -p 0 -X stuff "{consolecommand}^M"')
    if display:
        await asyncio.sleep(1)
        await showconsole(ctx, i, host, screen, port)

async def showconsole(ctx, i, host, screen, port):
    await ctx.channel.send(f"reading console on `{i}` `{host}{port}` with screen `{screen}`", delete_after=3)
    cmd =f'screen -S {screen} -p 0 -X hardcopy -h "screen_log.log"'
    send_consolecommand(host, cmd)
    await asyncio.sleep(1)
    fld=servfolders()[i]
    cmd =f'cat {fld}/screen_log.log'
    out,err = ssh_withcmd(host, cmd)
    output = str(out[-1500:])[2:-1].split("\\n") 
    await ctx.channel.send( f"`{host}{port}` `{screen}`:\n"+ "\n".join(output))
    await ctx.channel.send(f"Completed reading for `{i}` `{host}{port}` `{screen}`")# todo delete those msgs if passed

async def servupload(ctx,serverid):
    servers = getservers()
    await ctx.channel.send("Uploading plugins...", delete_after=3)
    try:
        i,host,screen,port,loc = servers[serverid]
        # add logic here to upload the files to the servers
        # use subprocess to scp the files
        #scp run_scp.py root@alexmindustryv7.servegame.com:/root/Documents/pvp_v7_2023/config/mods
        out,err = scp_cmd(host,src="/root/Documents/watermelonbot/data/mindustry/mods/common/*",
                dst=f"{servfolders()[i]}/config/mods")
        await ctx.channel.send(f"done upload: `{i}` `{host}{port}` with screen `{screen}`, output:{str(out)[-1000:]}")
    except Exception as e:
        strr=traceback.format_exc()
        await ctx.channel.send("error occurred 99:" + str(e)+"tb:"+strr)

async def get_version_of_plugin_from_all_servers(ctx: commands.Context):
    servers = getservers()
    try:
        await ctx.channel.send("Getting plugin versions...", delete_after=3)
        stringg=[]
        for i,host,screen,port,loc in servers:
            cmd = f'cat {servfolders()[i]}/config/mods/ASP_version.txt'
            out,_ = ssh_withcmd(host, cmd)
            out = str(out)[2+17:-1]
            stringg.append( f"`{i}` `{out}` `{host}:{port}` `{screen}`" )
        with open("/root/Documents/watermelonbot/data/mindustry/mods/common/ASP_version.txt","r") as f:
            ff = f.readlines()[0][17:]
            ff1=ff.split(":")[0]
        await ctx.channel.send( f"Plugin version on servers (latest: `{ff1}`):\n"+("\n".join(stringg)))
    except Exception as e:
        strr=traceback.format_exc()
        await ctx.channel.send("error occurred 127:" + str(e)+"tb:"+strr)
    else: 
        pass 

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
