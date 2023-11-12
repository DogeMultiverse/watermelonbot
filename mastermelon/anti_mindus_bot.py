from mastermelon import console_commands

async def vkick_anti_bot(message,bot):
    if message.author.id == bot.user.id:
        return
    if "w?sendcmd -1" not in message.content:
        return
    if "ModAdmin Hammer vkick" not in message.content:
        return
    if ("Reason grief" in message.content) or ("Reason bot" in message.content): 
        await message.channel.send("recieved this message, "+message.content)
        ban_command = message.content.split("\n")[2] # ban by ip
        ban_command= ban_command.split("-1 ")[1]
        await message.channel.send("this is the send command to servers: "+ban_command+"\nsending command")
        await console_commands.sendcommandtoserver(message,-1,ban_command)

async def plugin_anti_bot(message,bot):
    if message.author.id == bot.user.id:
        return
    if "BOT detected! IP banned: " not in message.content:
        return
    ip = message.content.split("BOT detected! IP banned: ")[1]
    if len(ip.split("."))!=4:
        await message.channel.send("error here 24")
        return
    else:
        strr = ip.split(".")[:3]
        subnet_ip = ".".join(strr)
        sendcmd = f"subnet-ban add {subnet_ip}"
        await message.channel.send(f"sending this command to servers: {sendcmd}")
        await console_commands.sendcommandtoserver(message,-1,sendcmd)
