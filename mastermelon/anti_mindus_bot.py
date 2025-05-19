from mastermelon import console_commands
import discord
from datetime import datetime

async def vkick_anti_bot(message,bot,autoban_counts,melonbotmindusbans):
    if "w?sendcmd -1" not in message.content:
        return
    if "ModAdmin Hammer vkick" not in message.content:
        return
    if "Report" in message.content:
        return

    autoban_channel: discord.TextChannel = bot.get_channel(1165956715230015529)
    mod_report_channel: discord.TextChannel = bot.get_channel(796305521270587413) 
    autoban_message_ctx = await autoban_channel.fetch_message(1173435083353505792)
    if ("Reason grief" in message.content) or ("Reason bot" in message.content) or ("Reason nsfw" in message.content): 
        autoban_counts[0] +=1
        ban_command_ip = message.content.split("\n")[2] # ban by ip
        ban_command_ip = ban_command_ip.split('-1 "')[1][:-1] 
        ban_command_muuid = message.content.split("\n")[1] # ban by muuid
        ban_command_muuid = ban_command_muuid.split('-1 "')[1][:-1]
        username = message.content.split("\n")[0][14:-1].replace(".","(dot)")

        await message.channel.send(f"☠️ autoban activated for {username}")
        await mod_report_channel.send( f"☠️ autoban activated for {username}" )

        await autoban_message_ctx.channel.send(f"☠️{autoban_counts[0]} banning user: {username}. by IP:"+ban_command_ip+"\nsending command")
        await console_commands.sendcommandtoserver(autoban_message_ctx,-2,ban_command_ip,False)
        melonbotmindusbans.insert_one( {"date": datetime.now(),"type":"vkick_ip","banned_user":username,"ban_command":ban_command_ip,"original_msg":message.content} )

        await autoban_message_ctx.channel.send(f"☠️{autoban_counts[0]} banning user: {username}. by MUUID:"+ban_command_muuid+"\nsending command")
        await console_commands.sendcommandtoserver(autoban_message_ctx,-2,ban_command_muuid,False)
        melonbotmindusbans.insert_one( {"date": datetime.now(),"type":"vkick_muuid","banned_user":username,"ban_command":ban_command_muuid,"original_msg":message.content} )

async def plugin_anti_bot(message,bot,autoban_counts,melonbotmindusbans):
    if "BOT detected! IP banned: " not in message.content:
        return
    ip = message.content.split("BOT detected! IP banned: ")[1]
    if message.content.count("BOT detected! IP banned: ")>1:
        return

    autoban_channel: discord.TextChannel = bot.get_channel(1165956715230015529)
    autoban_message_ctx = await autoban_channel.fetch_message(1173435083353505792)
    if len(ip.split("."))!=4:
        await message.channel.send("error here 24")
        return
    else:
        autoban_counts[1]+=1
        strr = ip.split(".")[:3]
        subnet_ip = ".".join(strr)
        sendcmd = f"subnet-ban add {subnet_ip}"
        await message.channel.send(f"☠️☠️{autoban_counts[1]}🤖🤖 autoban activated sending this command to servers: {sendcmd}")
        await console_commands.sendcommandtoserver(autoban_message_ctx,-2,sendcmd,False)
        melonbotmindusbans.insert_one( {"date": datetime.now(),"type":"subnet-ban-bot","ban_command":sendcmd,"original_msg":message.content} )
