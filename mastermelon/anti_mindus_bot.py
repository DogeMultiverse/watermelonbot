from mastermelon import console_commands

async def process_anti_bot(message,bot):
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
        await message.channel.send("this is the selected msg"+ban_command+"\nsending command")
        await console_commands.sendcommandtoserver(message,-1,ban_command)
