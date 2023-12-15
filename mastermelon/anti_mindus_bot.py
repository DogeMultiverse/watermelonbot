from mastermelon import console_commands
import discord

async def vkick_anti_bot(message,bot,autoban_counts):
    if message.author.id == bot.user.id:
        return
    if "w?sendcmd -1" not in message.content:
        return
    if "ModAdmin Hammer vkick" not in message.content:
        return
    if "Report" in message.content:
        return
    autoban_channel: discord.TextChannel = bot.get_channel(1165956715230015529)
    mod_report_channel: discord.TextChannel = bot.get_channel(796305521270587413) 
    autoban_message = await autoban_channel.fetch_message(1173435083353505792)
    if ("Reason grief" in message.content) or ("Reason bot" in message.content) or ("Reason nsfw" in message.content): 
        if message.content.count("Reason")>1:
            return
        autoban_counts[0] +=1
        ban_command = message.content.split("\n")[2] # ban by ip
        ban_command= ban_command.split('-1 "')[1][:-1] 
        username = message.content.split("\n")[0][14:-1]
        await message.channel.send(f"☠️ autoban activated for {username}")
        await mod_report_channel.send( f"☠️ autoban activated for {username}" )
        await autoban_message.channel.send(f"☠️{autoban_counts[0]} banning user: {username}. "+ban_command+"\nsending command")
        await console_commands.sendcommandtoserver(autoban_message,-1,ban_command,False)

async def plugin_anti_bot(message,bot,autoban_counts):
    
    if message.author.id == bot.user.id:
        return
    if "BOT detected! IP banned: " not in message.content:
        return
    ip = message.content.split("BOT detected! IP banned: ")[1]
    
    if message.content.count("BOT detected! IP banned: ")>1:
        return
    autoban_channel: discord.TextChannel = bot.get_channel(1165956715230015529)
    autoban_message = await autoban_channel.fetch_message(1173435083353505792)
    if len(ip.split("."))!=4:
        await message.channel.send("error here 24")
        return
    else:
        autoban_counts[1]+=1
        strr = ip.split(".")[:3]
        subnet_ip = ".".join(strr)
        sendcmd = f"subnet-ban add {subnet_ip}"
        await message.channel.send(f"☠️☠️{autoban_counts[1]}🤖🤖 autoban activated sending this command to servers: {sendcmd}")
        await console_commands.sendcommandtoserver(autoban_message,-1,sendcmd,False)
