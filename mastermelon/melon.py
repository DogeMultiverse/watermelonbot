import time
from datetime import timedelta
from datetime import datetime
import traceback
import logging
from typing import Union, Optional

import requests
import discord
import json
from mastermelon.anti_mindus_bot import plugin_anti_bot, vkick_anti_bot
from mastermelon.disc_constants import DUUID_ALEX, DUUID_WATERMELON

import pymongo
from pymongo.collection import Collection
from pymongo.database import Database
import asyncio
import random
from discord.ext import commands
# from discord import ui this dont work in discord 1.7.3
from mastermelon import counting_bot, console_commands
from mastermelon import highlow_game
from mastermelon import homework_game
from mastermelon import giveaway_bot
from mastermelon import effects_display
from mastermelon import emojis as ej
from mastermelon import cookiegame
from mastermelon import gen_image
from mastermelon import feedback
from mastermelon import mindustry
from mastermelon.utils.is_staff import is_staff
from mastermelon.utils.is_valid_guild import is_valid_guild_check, is_valid_guild
from mastermelon.utils.get_user_display_name import get_user_display_name

autoban_counts = [0, 0]  # griefers and bots


# some hardcoded variables
ADMIN_LOGS_CHANNEL = 789511356197765190
MODERATOR_LOGS_CHANNEL = 796305521270587413
COUNTING_CHANNEL = 805105861450137600
APPEAL_CHANNEL = 791490149753683988

PREFIX_TEST = "t?"
PREFIX_PROD = "w?"


def get_date_str():
    return str(datetime.now())[:-4]


intents = discord.Intents.default()
intents.members = True

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

with open("watermelon.config", "rb") as f:
    js = json.load(f)
    mongo_key: str = js["mongo_key"]
    prefix: str = js["prefix"]

if prefix in ["w?", "t?"]:  # only access mongodb for w? and t?
    client = pymongo.MongoClient(mongo_key)
    db: Database = client.get_database("AlexMindustry")
    expgains: Collection = db["expgains"]
    convertedexp: Collection = db["convertedexp"]
    # V7 stuff
    expv7: Collection = db["expv7"]
    convertedexpv7: Collection = db["convertedexpv7"]
    ingamecosmeticsv7: Collection = db["ingamecosmeticsv7"]
    hexv7: Collection = db["hexdataV7"]

    #mindus bans
    melonbotmindusbans: Collection = db["melonbotmindusbans"]
    mindusbans: Collection = db["mindusbans"]

    axdatabase: Collection = db["ax"]
    ipaddress_access_key: str = js["ipaddress_access_key"]
    serverplayerupdates: Collection = db["serverplayerupdates"]
    discordinvites: Collection = db["discordinvites"]
    registerpin: Collection = db["registerpin"]
    duuid1: Collection = db["duuid1"]
    # discord names
    discordname: Collection = db["discordname"]
    # hourly number of players
    hourly_players : Collection = db["hourly_players"]


invitecode_mapping = {"KPVVsj2MGW": "Alex Mindustry Invite", "BnBf2STAAd": "Doge Youtube Invite",
                      "GSdkpZZuxN": "Doge Youtube Premium Invite", "BmCssqnhX6": "Alex TOP MC Invite",
                      "FpKnzzQFne": "Alex TOP MC SERVERS Invite", "EhzVgNGxPD": "Alex Annoucement Invite",
                      "nVwZjfNJHJ": "Doge Youtube Invite", "WjKUdKNhdR": "Mintable Invite",
                      "A33dUt6r7n": "Alex Factorio Invite", "sHBFkzDJhv": "Youtube Invite"}


class bb(commands.Bot):

    def __init__(self, command_prefix, *args, **options):
        self.invites = {}
        self.inviter_dict = {}
        super().__init__(command_prefix, *args, **options)
        self.bg_task = []

    async def on_member_join(self, member: discord.Member):
        if prefix == "t?":
            return
        guild: discord.Guild = member.guild
        if member.bot:
            return
        invites_before_join = self.invites[member.guild.id]
        invites_after_join = await member.guild.invites()
        total_members = len([m for m in guild.members if not m.bot])

        curr_invite: discord.guild.Invite
        existing_invite: discord.guild.Invite
        found_resp_invite = False
        resp_invite: discord.guild.Invite
        for curr_invite in invites_after_join:
            found_old_invite = False
            for existing_invite in invites_before_join:
                if curr_invite.code == existing_invite.code:
                    found_old_invite = True
                    if curr_invite.uses > existing_invite.uses:
                        found_resp_invite = True
                        resp_invite = curr_invite  # this is the invite that was used
            if not found_old_invite:
                await self.update_self_invite_dict(guild, curr_invite)
                # update mongo with the new entry
                discordinvites.find_one_and_update({"duuid": curr_invite.inviter.id},
                                                   {"$set": {"codes." + curr_invite.code: curr_invite.uses}})
                if curr_invite.uses > 0:
                    found_resp_invite = True
                    resp_invite = curr_invite

        if found_resp_invite:
            # type the msg here
            invite = resp_invite
            # add the invited member to the inviter's list
            invite_dict_info = {"invited": {"name": f"{member.name}#{member.discriminator}", "duuid": member.id,
                                            "date": datetime.now()}}
            discordinvites.find_one_and_update({"duuid": invite.inviter.id}, {
                "$push": invite_dict_info})
            print(
                f"Member {member.name} Joined. Invite Code: {invite.code}. Inviter: {invite.inviter}")
            if invite.code in invitecode_mapping:
                to_send = f'{member.mention}, you are the #{total_members} member' + \
                          f".\n Inviter: {invitecode_mapping[invite.code]}. \nInvite counts: {invite.uses}"
            else:
                to_send = f'{member.mention}, you are the #{total_members} member' + \
                          f".\nInvite Code: {invite.code}. Inviter: {invite.inviter}. \nInvite counts: {invite.uses}"
        else:
            # invite code unknown.
            to_send = f'{member.mention}, you are the #{total_members} member' + \
                      f".\n Unable to identify invite code."

        # todo everytime someone joins, compare old invite list to new invite list
        # find the invitecode with the increment OR with a new invitecode with >1 invite
        #   # print it out
        # save all invites to invite list
        self.invites[member.guild.id] = invites_after_join

        if guild.system_channel is not None:
            embed = discord.Embed(colour=discord.Colour.random().value)
            embed.add_field(name=f"Welcome to {guild.name}!", value=to_send)
            embed.set_thumbnail(url=str(member.avatar_url))

            avatar = member.avatar_url_as(
                format="png", static_format="png", size=64)
            name = f"{member.name}#{member.discriminator}"
            image_data = await gen_image.getwelcomeimage(name=name, avatar=avatar)
            await guild.system_channel.send(embed=embed, file=image_data)

    async def on_member_remove(self, member: discord.Member):
        if prefix == "t?":
            return
        # Updates the cache when a user leaves to make sure everything is up to date
        invites_before_remove = self.invites[member.guild.id]
        invites_after_remove = await member.guild.invites()
        self.invites[member.guild.id] = await member.guild.invites()
        guild: discord.Guild = member.guild
        msg_builder = f'`{member.display_name.replace("`", "")}` left ;-;'
        total_members = len([m for m in guild.members if not m.bot])
        for invite in invites_before_remove:
            if invite.uses > find_invite_by_code(invites_after_remove, invite.code).uses:
                msg_builder += f" {member.display_name}, -1 invite for Invite Code: {invite.code}. Inviter: {invite.inviter}"
        await guild.system_channel.send(msg_builder + f"\nNow we have {total_members} members.")

    async def on_ready(self):
        print('Logged in as', bot.user.name, bot.user.id)
        for guild in bot.guilds:
            # Adding each guild's invites to our dict
            self.invites[guild.id] = await guild.invites()
            self.inviter_dict[guild.id] = {}
            invite: discord.guild.Invite
            for invite in self.invites[guild.id]:
                await self.update_self_invite_dict(guild, invite)
        self.bg_task.append(self.loop.create_task(
            self.update_mind_status_task()))
        git_update_channel: discord.TextChannel = self.get_channel(
            788228956372992020)
        await git_update_channel.send(f"melon bot started at {get_date_str()}")

    async def update_self_invite_dict(self, guild, invite):
        if invite.inviter.id not in self.inviter_dict[guild.id]:
            self.inviter_dict[guild.id][invite.inviter.id] = {"total": invite.uses,
                                                              "name": f"{invite.inviter.name}#{invite.inviter.discriminator}",
                                                              "codes": {invite.code: invite.uses}}
        else:
            prev_uses = self.inviter_dict[guild.id][invite.inviter.id]["total"]
            prev_codes = self.inviter_dict[guild.id][invite.inviter.id]["codes"]
            inviter_name = self.inviter_dict[guild.id][invite.inviter.id]["name"]
            self.inviter_dict[guild.id][invite.inviter.id] = {"total": invite.uses + prev_uses,
                                                              "name": inviter_name,
                                                              "codes": {invite.code: invite.uses, **prev_codes}}

    # background tasks:
    async def update_mind_status_task(self):
        await self.wait_until_ready()
        try:
            status_msg_channel: discord.TextChannel = self.get_channel(
                791158921443409950)
            status_log_channel: discord.TextChannel = self.get_channel(
                791129836948422676)
            while prefix == PREFIX_PROD:  
                t0 = time.time()
                messages = await status_log_channel.history(limit=30, oldest_first=False,
                                                            after=datetime.now() - timedelta(minutes=7)).flatten()
                msg: discord.Message
                servers = set()
                timestamp = int(datetime.now().timestamp())
                strbuilder = f"Updated <t:{timestamp}:R>\n"
                maps = []
                players_in_servers = dict()
                for msg in messages:
                    if " is **running**:" in msg.content and "**PLAYERS**" in msg.content:
                        # print(msg.content, msg.created_at)
                        msg1 = msg.content.split(" is **running**: ")
                        servername = strip_colourbrackets(msg1[0])
                        if servername not in servers:
                            servers.add(servername)
                            msg2 = msg1[1].split(", **PLAYERS**=")
                            msg3 = msg2[1].split(", **RAM**=")
                            num_players = msg3[0]
                            RAM = msg3[1]
                            ss = strip_colourbrackets(msg2[0])
                            maps += [
                                f"✅ `ONLINE`✅ {servername}\n`            `**Map**: `{ss}`  **Players**:`{num_players}`  **RAM**:`{RAM}`\n"]
                            players_in_servers[servername] = int(float(num_players))
                if len(servers) == 0:
                    strbuilder += "Servers Ded :("
                else:
                    strbuilder += "".join(sorted(maps))
                status_msg: discord.Message = await status_msg_channel.history(limit=1).flatten()
                if status_msg and status_msg[0].content.startswith("Updated <t"):
                    await status_msg[0].edit(content=strbuilder)
                else:  # if not found, send as a new msg
                    await status_msg_channel.send(strbuilder)
                # save the time series onto AlexMindustry.hourly_players
                add_hourly_player_data(players_in_servers)
                print(
                    f"update mindus servers took {time.time() - t0:.3f}seconds {get_date_str()}")
                await asyncio.sleep(60 * 5)
        except RuntimeError:
            print("mindus status update closed")

def add_hourly_player_data(players_in_servers):
    # this is the of the number of players currently in the servers
    data = []
    current_time = datetime.now()
    
    for server, count in players_in_servers.items():
        data.append({
            'servername': server,
            'player_count': count,
            'time': current_time
        })
    # Insert the documents into the collection
    hourly_players.insert_many(data)
    print(f"Added data for servers at {current_time}")


bot = bb(command_prefix=prefix, description=description, intents=intents)


def find_invite_by_code(invite_list, code):
    # Simply looping through each invite in an
    # invite list which we will get using guild.invites()
    for inv in invite_list:
        # Check if the invite code in this element
        # of the list is the one we're looking for
        if inv.code == code:
            # If it is, we return it.
            return inv
    return None


bot.remove_command("help")


@bot.command()
async def help(ctx, args=None):
    help_embed = discord.Embed(title=f"All commands from `[{prefix}] {bot.user.display_name}`",
                               colour=discord.Colour.random().value)
    command_names_list = [x.name for x in bot.commands]

    if not args:
        help_embed.set_thumbnail(url=str(bot.user.avatar_url))
        dictt = {}  # category:{name:,help:}
        x: discord.ext.commands
        for i, x in enumerate(bot.commands):
            if str(x.brief) in dictt:
                dictt[str(x.brief)].append(
                    {"name": x.name, "description": x.description})
            else:
                dictt[str(x.brief)] = [
                    {"name": x.name, "description": x.description}]
        for category, commandss in dictt.items():
            help_embed.add_field(name=category if category != "None" else "Others/Misc",
                                 value="`" + ("`, `".join([c["name"] for c in commandss])) + "`")
        help_embed.add_field(
            name="Details",
            value=f"Type `{prefix}help <command name>` for more details about each command.",
            inline=False
        )

    # If the argument is a command, get the help text from that command:
    elif args in command_names_list:
        help_embed.title = "Command Information"
        command = bot.get_command(args)
        command_help = "" if isinstance(command.help, type(
            None)) else ("Help: " + command.help + "\n")
        command_desc = "" if (isinstance(command.description, type(None)) or command.description == "") else (
                "\nDescription: " + command.description)
        help_embed.add_field(
            name="Command name: `" + args + "`",
            value=command_help + "Usage: `" + prefix + args +
                  " " + command.signature + "`" + command_desc
        )

    # If someone is just trolling:
    else:
        help_embed.add_field(
            name="Nope.",
            value="Don't think I got that command, boss!"
        )

    await ctx.send(embed=help_embed)


@bot.command(description="High low game, try to guess the correct number by clicking higher or lower.", brief="Game")
async def highlow(ctx):
    await highlow_game.run_highlowgame(ctx, bot)


@bot.command(description="Do your homework.", brief="Game")
async def homework(ctx):
    await homework_game.run_homeworkgame(ctx, bot)


@bot.command(description="Gets all animated emojis from this discord.", brief="None")
@commands.check(is_valid_guild)
@commands.has_any_role("Admin (Discord)", "Mod (Discord)")
async def getemojis(ctx):
    emojis = await ctx.guild.fetch_emojis()
    for emoji in emojis:
        if emoji.animated:
            await ctx.message.add_reaction(emoji)
    await ctx.channel.send("added animated all emojis")


@bot.command(description="get countries played", brief="Admin Utility")
@commands.has_role("Admin (Discord)")
async def gettest(ctx: commands.Context):
    if ctx.author.id != DUUID_ALEX:
        await ctx.channel.send("no testing for u")
        return
    # await show_countries.getcountries(serverplayerupdates, ipaddress_access_key)
    await ctx.channel.send(len([m for m in ctx.guild.members if not m.bot]))


@bot.command(description="get names of users (admin only)", brief="Admin Mindustry Utility",
             help="<serverid, -1 for allservers>")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def getnames(ctx: commands.Context, serverid: int = None):
    if ctx.author.id != DUUID_ALEX:
        await ctx.channel.send("no testing for u")
        return
    if True:
        await ctx.channel.send("alex, dont run this again... it will add unnecessary additional documents")
        return
    listt = [{"duuid": m.id, "discname": m.name, "discri": m.discriminator} for m in ctx.guild.members if not m.bot]
    discordname.insert_many(listt)
    # mems = [m for m in ctx.guild.members if not m.bot]
    # await ctx.channel.send(str(mems[:5]))
    await ctx.channel.send("done")


@bot.command(description="Get info of user's mindustry account", brief="Admin Mindustry Utility",
             help="<DUUID of user>") 
@commands.has_any_role("Admin (Discord)","Admin (Mindustry)")
@commands.check(is_valid_guild)
async def getmindusinfo(ctx: commands.Context, DUUID: int = None):
    if ctx.author.id != DUUID_ALEX:
        await ctx.channel.send("no testing for u")
        return
    # TODO: make this function accept both int and @user
    # search for this duuid in duuid1
    # return the name, ip, muuid etc etc.
    duuid_docs = duuid1.find({"duuid":DUUID}).sort("date",pymongo.DESCENDING)
    embed = discord.Embed(title=f"Accounts of {DUUID}")
    list_muuid = []
    for userdata in duuid_docs:
        musername = userdata["musername"]
        muuid = userdata["muuid"]
        role = userdata["role"]
        color = userdata["color"]
        date1 = userdata["date"]
        strr=f"musername:`{musername}`, role:`{role}`, color:`{color}`, date:`{date1}`"
        if (muuid in list_muuid) or (len(list_muuid)>20):
            continue
        list_muuid.append(muuid)
        embed.add_field(name=f"muuid {muuid}",value=strr,inline=False)
    if len(list_muuid)==0:
        await ctx.channel.send("User not registered. Unable to unban.")
        return
    embed.add_field(name=f"All muuid {len(list_muuid)}",value=" ".join(list_muuid),inline=False)
    await ctx.channel.send(embed=embed)
    embed_mindusbans_muuid = discord.Embed(title=f"Search bans by muuid")
    counts = 0
    for muuid in list_muuid:
        mindusbans_docs = mindusbans.find({'banned_muuid': muuid})
        for mindusbans_doc in mindusbans_docs:
            banned_by_duuid = mindusbans_doc["banned_by_duuid"]
            strr = ""
            strr+= "date:"+str(mindusbans_doc["date"])+"\n"
            strr+= "banned_muuid:"+mindusbans_doc["banned_muuid"]+"\n"
            strr+= "banned_ip:"+mindusbans_doc["banned_ip"]+"\n"
            strr+= "banned_reason:"+mindusbans_doc["banned_reason"]+"\n"
            strr+= "servername:"+mindusbans_doc["servername"]+"\n"
            strr+= "banned_type:"+mindusbans_doc["banned_type"]
            
            if counts>20: # unlikely for more than 20 bans.
                counts+=1
                continue
            embed_mindusbans_muuid.add_field(name=f"(ban by {banned_by_duuid}) banned_musername: `{mindusbans_doc['banned_musername']}`", 
                            value=strr,inline=False)
            counts+=1
    if counts==0:
        embed_mindusbans_muuid.add_field(name="no muuid bans found",value="searched from mindusbans",inline=False)
    await ctx.channel.send(embed=embed_mindusbans_muuid)

    # TODO find all other IP that are related.
    # TODO find the banned statuses.

# commands related to mindustry servers
@bot.command(description="restart servers (admin only)", brief="Admin Mindustry Utility",
             help="<serverid, -1 for allservers>")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
# todo add servercommand: str = "hubkick"
async def restartserver(ctx: commands.Context, serverid: int = None):
    if serverid is None:
        await console_commands.getserver(ctx)
        await ctx.send(f"use <serverid, -1 for allservers>")
    elif serverid == -1:  # update all servers
        for serverid in range(len(console_commands.getservers())):
            await console_commands.restartserver(ctx, serverid)
    else:
        await console_commands.restartserver(ctx, serverid)


@bot.command(description="start servers (admin only)", brief="Admin Mindustry Utility",
             help="<serverid, -1 for allservers>")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def startserver(ctx: commands.Context, serverid: int = None):
    if serverid is None:
        await console_commands.getserver(ctx)
        await ctx.send(f"use <serverid, -1 for allservers>")
    elif serverid == -1:  # start all servers
        for serverid in range(len(console_commands.getservers())):
            await console_commands.startserver(ctx, serverid)
    else:
        await console_commands.startserver(ctx, serverid)


@bot.command(description="send gameover command to servers (admin only)", brief="Admin Mindustry Utility",
             help="<serverid, -1 for allservers>")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
# todo add servercommand: str = "hubkick"
async def gameoverserver(ctx: commands.Context, serverid: int = None):
    if serverid is None:
        await console_commands.getserver(ctx)
        await ctx.send(f"use <serverid, -1 for allservers>")
    elif serverid == -1:  # update all servers
        for serverid in range(len(console_commands.getservers())):
            await console_commands.gameoverserver(ctx, serverid)
    else:
        await console_commands.gameoverserver(ctx, serverid)


@bot.command(description="get available servers (admin only)", brief="Admin Mindustry Utility")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def getserver(ctx):
    await console_commands.getserver(ctx)


@bot.command(description="get alexserverplugin versions from all servers (admin only)", brief="Admin Mindustry Utility")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def getver(ctx):
    await console_commands.get_version_of_plugin_from_all_servers(ctx)
    await ctx.send("send `w?update -1` to update all servers")


@bot.command(description="see server console (admin only)", brief="Admin Mindustry Utility")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def readserver(ctx: commands.Context, serverid: int):
    await console_commands.readserver(ctx, serverid)


@bot.command(description="send command to mindustry server and read the console (admin only)",
             brief="Admin Mindustry Utility")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def sendcmd(ctx: commands.Context, serverid: int, consolecommand: str):
    await console_commands.sendcommandtoserver(ctx, serverid, consolecommand)


@bot.command(description="upload alexplugin to servers.", brief="Admin Mindustry Utility",
             help="<serverid, -1 for allservers>")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def update(ctx: commands.Context, serverid: int = None):
    if serverid is None:
        await console_commands.getserver(ctx)
        await ctx.send(f"use <serverid, -1 for allservers>")
    elif serverid == -1:  # update all servers
        await ctx.send(f"Updating servers...", delete_after=5)
        for serverid in range(len(console_commands.getservers())):
            await console_commands.servupload(ctx, serverid)
    else:
        await console_commands.servupload(ctx, serverid)


@bot.command(description="upload maps to servers.", brief="Admin Mindustry Utility",
             help="<serverid, -1 for allservers>")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def syncmap(ctx: commands.Context, serverid: int = None):
    if serverid is None:
        await console_commands.getserver(ctx)
        await ctx.send(f"use <serverid, -1 for allservers>")
    elif serverid == -1:  # syncmap all servers
        await ctx.send(f"Updating maps...", delete_after=5)
        for serverid in range(len(console_commands.getservers())):
            await console_commands.syncmindusmap(ctx, serverid)
    else:
        await console_commands.syncmindusmap(ctx, serverid)


@bot.command(description="assigns the user's role in mindustry, role can be Admin|Mod|Player",
             help="<@user or duuid> <role>",
             brief="Admin Mindustry Utility")
@commands.has_any_role("Admin (Discord)", "Admin (Mindustry)")
@commands.check(is_valid_guild)
async def changemindusrole(ctx, user: discord.user.User, role: str):
    userid: int
    usermention = None
    if isinstance(user, discord.user.User):
        userid = user.id
        usermention = user.mention
    elif isinstance(user, int):
        userid = user
        usermention = str(user)
    else:
        await ctx.send(
            f"Error, input invalid, u gave {user}type{type(user)}, {role}type{type(role)}, type{type(discord.user.User)}type{type(discord.Member)}")
        return
    if role in ["Admin", "Mod", "Player"]:
        result = duuid1.update_many(
            {"duuid": userid}, {"$set": {"role": role}})
        if result.modified_count > 0:
            await ctx.send(f"Congrats, {usermention} is now a {role} in Mindustry")
        else:
            await ctx.send(f"Nothing changed.")
    else:
        await ctx.send(f"Error, role not found. Please choose Admin|Mod|Player.")


def is_valid_ip(ip: str) -> bool: # checks if a string is a valid IP address
    import re
    pattern = re.compile(r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return bool(pattern.match(ip))


@bot.command(description="Query if the IP address is banned in any way. Automatically checks for subnet bans. MUST enter a full IP address.",
             help="<IP address>",
             brief="Admin Mindustry Utility")
@commands.has_any_role("Admin (Discord)", "Admin (Mindustry)")
@commands.check(is_valid_guild)
async def querybannedip(ctx, ipadd:str):
    if not is_valid_ip(ipadd):
        await ctx.send("Error, IP address is invalid.")
        return
    query = {"type": "subnet-ban-bot"}
    projection = {"ban_command": 1, "_id": 0}
    results = melonbotmindusbans.find(query, projection)
    res = list(results)
    subnet_bans = set([bc["ban_command"][15:] for bc in res])

    query = {"type": "vkick_ip"}
    projection = {"ban_command": 1, "_id": 0}
    results = melonbotmindusbans.find(query, projection)
    res = list(results)
    ip_bans = set([bc["ban_command"][7:] for bc in res])
    ip_in_question = ".".join(ipadd.split(".")[:3]) # drops the last part.
    strr= []
    for ip in ip_bans:
        if ip_in_question in ip :
            strr.append( f" `ipban:{ip}` ")
    for ip in subnet_bans:
        if ip_in_question in ip :
            strr.append( f" `subnet-ban:{ip}` ")
    if len(strr)==0:
        await ctx.send("IP address is not banned in any way.")
    else:
        final_str = ", ".join(strr)
        await ctx.send(f"IP address found: {final_str}.\n To unban, use `subnet-ban remove XXX` or `unban XXX`")


@bot.command(description="gets the recent bans given by a moderator or admin",
             help="<@user>",
             brief="Admin Mindustry Utility")
@commands.has_any_role("Admin (Discord)", "Admin (Mindustry)")
@commands.check(is_valid_guild)
async def getmindusbans(ctx, user: discord.user.User):
    userid: int
    if isinstance(user, discord.user.User):
        userid = user.id
    else:
        await ctx.send(
            f"Error, input invalid, u gave {user}type{type(user)}, type{type(discord.user.User)}type{type(discord.Member)}")
        return
    docs = mindusbans.find({'banned_by_duuid': userid}).sort("date",-1).limit(10)
    embed = discord.Embed(title=f"Bans given by {user.name}",colour=discord.Colour.random().value)
    for i,d in enumerate(docs):
        strr = ""
        strr+= "date:"+str(d["date"])+"\n"
        strr+= "banned_muuid:"+d["banned_muuid"]+"\n"
        strr+= "banned_ip:"+d["banned_ip"]+"\n"
        strr+= "banned_reason:"+d["banned_reason"]+"\n"
        strr+= "servername:"+d["servername"]+"\n"
        strr+= "banned_type:"+d["banned_type"]
        embed.add_field(name=f"({i}) banned_musername: `{d['banned_musername']}`", 
                        value=strr,inline=False) 
    await ctx.channel.send(embed=embed)


@bot.command(description="plots the historical usage of servers. specify the hours in the past, default 24hours.",
             help="[hours]",
             brief="Admin Mindustry Utility")
@commands.has_any_role("Admin (Discord)", "Admin (Mindustry)")
@commands.check(is_valid_guild)
async def plotmindushistory(ctx, hours: int = 24): 
    await mindustry.plotanalytics(ctx,hourly_players,hours)


# end of commands related to mindustry servers

@bot.command(description="adds <:EMOJI:> to the desired <message_id> in [channel]. max 20 emojis per message",
             help="adds <:emoji:> to <message_id> in [channel]",
             brief="Hype")
@commands.has_any_role("Admin (Discord)", "Mod (Discord)")
@commands.check(is_valid_guild)
async def addemoji(ctx, emoji: str, messageid: int, channel: discord.TextChannel = None):
    emojis = await ctx.guild.fetch_emojis()
    try:
        await ctx.message.delete(delay=3)
        if channel is None:
            msg = await ctx.fetch_message(messageid)
        else:
            msg = await channel.fetch_message(messageid)
        found = False
        for emoji_custom in emojis:
            if emoji[1:-1].lower() == emoji_custom.name.lower():
                await msg.add_reaction(emoji_custom)
                found = True
                await ctx.send(f"{emoji_custom} sent! Self destructing...", delete_after=3)
        if not found:
            await ctx.send("Emoji not found. Make sure to add the colons `:   :`", delete_after=3)
    except discord.NotFound:
        await ctx.send("Message id not found. Maybe message was deleted?", delete_after=3)


@bot.command(description="adds hype emojis",
             help="<message_id> <channel> <counts> (duration will be ~ counts*10 secs)", brief="Hype")
@commands.has_any_role("Admin (Discord)", "Mod (Discord)")
@commands.check(is_valid_guild)
async def addhype(ctx, message: discord.Message, counts: int = 5):
    emojis = await ctx.guild.fetch_emojis()
    try:
        total_emojis = 0
        await ctx.send(f"Hype sending! Self destructing...", delete_after=3)
        for emoji_custom in random.sample(emojis, k=len(emojis)):
            if emoji_custom.name.lower() in ["partyglasses", "pepoclap", "roll", "blob", "auke", "catdance", "pog",
                                             "hypertada", "feelsgoodman", "cata", "petangry",
                                             "typing", "petmelon", "petalex"]:
                total_emojis += 1
                await asyncio.sleep(random.randint(3, 3 + counts * 10))
                await message.add_reaction(emoji_custom)
            if total_emojis > counts:
                break
    except discord.NotFound:
        await ctx.send("Message id not found. Maybe message was deleted?", delete_after=3)
    await ctx.message.delete(delay=3)


@bot.command(description="adds hype emojis",
             help="<message_id> <channel> <counts> (duration will be ~ counts*10 secs)", brief="Hype")
@commands.has_any_role("Admin (Discord)", "Mod (Discord)")
@commands.check(is_valid_guild)
async def addhype2(ctx, messageid: int, channel: discord.TextChannel = None, counts: int = 5):
    emojis = await ctx.guild.fetch_emojis()
    try:
        if channel is None:
            msg = await ctx.fetch_message(messageid)
        else:
            msg = await channel.fetch_message(messageid)
        total_emojis = 0
        await ctx.send(f"Hype sending! Self destructing...", delete_after=3)
        for emoji_custom in random.sample(emojis, k=len(emojis)):
            if emoji_custom.name.lower() in ["partyglasses", "pepoclap", "roll", "blob", "auke", "catdance", "pog",
                                             "hypertada", "feelsgoodman", "cata", "petangry",
                                             "typing", "petmelon", "petalex"]:
                total_emojis += 1
                await asyncio.sleep(random.randint(3, 3 + counts * 10))
                await msg.add_reaction(emoji_custom)
            if total_emojis > counts:
                break
    except discord.NotFound:
        await ctx.send("Message id not found. Maybe message was deleted?", delete_after=3)
    await ctx.message.delete(delay=3)


@bot.event
async def on_command_error(ctx: discord.ext.commands.Context, error: Exception, *args, **kwargs):
    print(ctx.author, ctx, str(error))
    if isinstance(type(error), discord.ext.commands.UserInputError):
        await ctx.message.channel.send(f"Wrong arguments {ctx.author.mention}: {error} Use `{prefix}help {ctx.command.name}` to learn to use the command properly.")
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.message.channel.send(f"Bad arguments {ctx.author.mention}: {error} Use `{prefix}help {ctx.command.name}` to learn to use the command properly.")
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.message.channel.send(f"Missing argument {ctx.author.mention}: {error} Use `{prefix}help {ctx.command.name}` to learn to use the command properly.")
    elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.message.channel.send(f"ERROR {ctx.author.mention}: CommandNotFound")
    elif isinstance(error, discord.ext.commands.MissingRole):
        await ctx.channel.send(f"You dont have the permission to run this command. {ctx.author.mention}")
    elif isinstance(error, discord.ext.commands.CheckFailure):
        # Fail silently
        # The check should handle the error and notify the user
        pass
    else:
        await ctx.message.channel.send(f"Unknown error {ctx.author.mention}:" + str(type(error)) + str(error))


@bot.command(description="Play the guessing number game.", brief="Game")
@commands.check(is_valid_guild)
async def guess(ctx: discord.ext.commands.Context):
    await ctx.channel.send('Guess a number between 1 and 1000000. Its one in a million')

    def is_correct(m):
        return m.author == ctx.author and m.content.isdigit() and m.channel == ctx.channel

    answer = random.randint(1, 1000000)
    print(answer)
    try:
        guess1 = await bot.wait_for('message', check=is_correct, timeout=20.0)
    except asyncio.TimeoutError:
        return await ctx.channel.send('Sorry, you took too long it was {}.'.format(answer))
    if int(guess1.content) > 1000000:
        await ctx.channel.send('Number too large, should be <1000000. Game ends.')
        return
    if int(guess1.content) == answer or (False and ((ctx.author.id in [DUUID_WATERMELON, DUUID_ALEX]) and random.randint(1, 10) > 5)):
        await ctx.channel.send('You are right!!!!')
    else:
        await ctx.channel.send('Oops. It is actually {}.'.format(answer))


@bot.command(description="Displays buyeffect menu.", brief="Utility")
@commands.check(is_valid_guild)
async def buyeffect(ctx: discord.ext.commands.Context, peffect: str = None):
    if prefix == "t?" and ctx.author.id != DUUID_ALEX:
        await ctx.channel.send("t? is only for alex to test")
        return
    await ctx.channel.send("Fetching effects...", delete_after=2)
    discount = 0.5
    effects_cost = {50: ["yellowDiamond", "yellowSquare"],
                    100: ["yellowSpark"],
                    160: ["yellowLargeDiam"],
                    200: ["whiteLancerRandom"],
                    550: ["whiteLancerRadius", "circle", "pixel"],
                    800: ["rainbowPixel", "rainbowCircle"]}
    effects = [ee for c, e in effects_cost.items() for ee in e]
    owned_effects_collection = ingamecosmeticsv7.find_one({"duuid": ctx.author.id})
    if owned_effects_collection is None:
        await ctx.channel.send(f"{ctx.author.name}: You need to have a **REGISTERED** mindustry account.")
        return
    owned_effects = owned_effects_collection["effects"]
    duuid = ctx.author.id
    if axdatabase.find_one({"duuid": duuid}) is None:
        balance = 0
        axdatabase.insert_one({"duuid": duuid, "ax": 0})
    else:
        balance = axdatabase.find_one({"duuid": duuid})["ax"]
    if isinstance(peffect, type(None)):
        await effects_display.showeffectsmenu(ctx, effects_cost, owned_effects, effects, balance, axdatabase, ingamecosmeticsv7,
                                              discount)
    else:
        await ctx.channel.send("Validating purchase...", delete_after=2)
        await effects_display.makepurchase(ctx, effects_cost, owned_effects, effects, peffect, axdatabase, ingamecosmeticsv7)


# todo show all effects?
#  @bot.command(description=f"Shows effects", brief="Utility")
# async def showeffects(ctx: discord.ext.commands.Context):
#     if prefix == "t?" and ctx.author.id != DUUID_ALEX:
#         msg: discord.Message = await ctx.channel.send("t? is only for alex to test")
#         await msg.add_reaction(ej.pog_emoji)
#         return
#     await effects_display.showeffectsmenu()


@bot.command(description=f"Check leaderboard of {ej.ax_emoji} ownership", brief="Utility")
@commands.check(is_valid_guild)
async def axleaderboard(ctx: discord.ext.commands.Context):
    cursor = axdatabase.find({"ax": {"$gte": 0}}).sort('ax', -1).limit(10)
    output = f"{ej.ax_emoji} Leaderboard\n" + f"Rank, Amount, User\n"
    for i, user_ax in enumerate(cursor):
        name = get_user_display_name(ctx, user_ax["duuid"])
        output += f'{i}. {user_ax["ax"]}{ej.ax_emoji}: {name}\n'
    await ctx.reply(output)


@bot.command(description=f"Check leaderboard in hex", brief="Utility")
@commands.check(is_valid_guild)
async def hexleaderboard(ctx: discord.ext.commands.Context):
    docs = hexv7.find({},{"currMMR":1,"musername":1,"_id":0,"losswinrank":1}).sort("currMMR",-1).limit(10)
    listt = []
    for d in docs:
        listt.append(d)
    output = ["Rank, MMR,   WR,   N, IGN"]
    for rank,dictt in enumerate(listt[:10]):
            # wr = sum([ (d>0) and (d<4) for d in dictt["losswinrank"]])/len(dictt["losswinrank"])
            wr = sum([ d==1 for d in dictt["losswinrank"]])/len(dictt["losswinrank"])
            matches = len(dictt["losswinrank"])
            # output.append( f'`  {rank+1:>2}`,` {dictt["currMMR"]}`,`{wr:>5.0%}`,`{matches:>4}`, `{dictt["musername"]}`')
            output.append( f'`  {rank+1:>2}, {dictt["currMMR"]},{wr:>5.0%},{matches:>4}, {dictt["musername"]}`')
    await ctx.reply("\n".join(output))


@bot.command(description="Allocate Ax.", brief="Admin Utility", help="<amount:integer> <@user> <reason>")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def giveax(ctx: discord.ext.commands.Context, amount: int, user: discord.Member, *reason):
    old_val = axdatabase.find_one({"duuid": user.id})
    if isinstance(old_val, type(None)):
        axdatabase.insert_one({"duuid": user.id, "ax": 0})
        old_val = 0
    else:
        old_val = old_val["ax"]
    axdatabase.find_one_and_update({"duuid": user.id}, {"$inc": {"ax": amount}})
    await ctx.channel.send(f"{amount}{ej.ax_emoji} awarded to {user.mention}. "
                           f"Now {old_val + amount}{ej.ax_emoji}.\nReason: {' '.join(reason)}")


@bot.command(description="Allocate Ax to multiple users.", brief="Admin Utility",
             help="<amount:integer> <@user1>, <@user2>, ... <reason>")
@commands.has_role("Admin (Discord)")
@commands.check(is_valid_guild)
async def giveaxmultiple(ctx: discord.ext.commands.Context, amount: int, *args):
    users = []
    reason = []
    flag = False
    for arg in args:
        if arg.startswith("<@") and not flag:
            users.append(arg[:-1])
        else:
            flag = True
            reason.append(arg)

    updates = []  # List to accumulate updates for each user
    for user in users:
        member = await commands.MemberConverter().convert(ctx, user)
        old_val = axdatabase.find_one({"duuid": member.id})

        if isinstance(old_val, type(None)):
            axdatabase.insert_one({"duuid": member.id, "ax": 0})
            old_val = 0
        else:
            old_val = old_val["ax"]

        axdatabase.find_one_and_update({"duuid": member.id}, {"$inc": {"ax": amount}})

        # Accumulate the update message for this user
        updates.append(
            f"{amount}{ej.ax_emoji} awarded to {member.mention}. Now {old_val + amount}{ej.ax_emoji}.")

    # Join all the update messages into a single message and send it at the end
    await ctx.channel.send("\n".join(updates) + f"\nReason: {' '.join(reason)}")


@bot.command(description="Check user's Ax. If no user is specified, check your own Ax.",
             brief="Utility", help="[@user or discord ID or nothing]")
@commands.check(is_valid_guild)
async def checkax(ctx: discord.ext.commands.Context, user: discord.User = None):
    try:
        if user is None:
            user = ctx.author

        old_val = axdatabase.find_one({"duuid": user.id})
        if isinstance(old_val, type(None)):
            old_val = 0
        else:
            old_val = old_val["ax"]

        await ctx.channel.send(f"{user.display_name} currently has {old_val}{ej.ax_emoji}.")
    except ValueError:
        await ctx.channel.send(f"Invalid input. Try the ID in digits or @user.")


@bot.command(description=f"Register your mindustry account with your discord account.", brief="Utility")
@commands.check(is_valid_guild)
async def register(ctx: discord.ext.commands.Context, pin: str):
    try:
        int(pin)
    except ValueError:
        await ctx.channel.send(f'Pin has to be digits only. eg, `12345` or `12346`')
    else:
        await ctx.channel.send(f'Pin input is `{pin}`, please wait.')
        res = registerpin.find(
            {"pin": pin, "date": {"$gte": datetime.now() - timedelta(minutes=5)}})
        found = False
        userdata = None
        found_objects = []
        for val in res:
            found = True
            userdata = val
            found_objects.append(val["_id"])
        if found:
            role = "Player"
            for role_temp in ctx.author.roles:
                if role_temp.name.lower() in ["admin (mindustry)", "admin (discord)", "co-owner"]:
                    role = "Admin"
                if role_temp.name.lower() in ["mod (mindustry)", "mod (discord)"]:
                    role = "Mod"
            duuid1.insert_one({"duuid": ctx.author.id, "musername": userdata["musername"],
                               "muuid": userdata["muuid"], "role": role, "color": "0000ffff",
                               "date": datetime.now()})

            prev_doc = discordname.find_one({"duuid": ctx.author.id})
            if prev_doc is None:
                # [{"duuid":m.id,"discname":m.name,"discri":m.discriminator} for m in ctx.guild.members if not m.bot]
                discordname.insert_one(
                    {"duuid": ctx.author.id, "discname": ctx.author.name, "discri": ctx.author.discriminator})
            for found_object in found_objects:  # delete all the pins from database
                registerpin.find_one_and_delete({"_id": found_object})
            await ctx.channel.send(
                f'✅Successfully registered 👍 <@!{ctx.author.id}>. Welcome to Alex Multiverse. Enjoy your in game skins/effects.')
        else:
            await ctx.channel.send(
                f"❌Pin not found for <@!{ctx.author.id}>. Make sure you did `/register` in Mindustry within the last 5 mins. Don't spam it.")


@bot.command(description=f"get image with user's pfp", brief="Utility")
@commands.check(is_valid_guild)
async def getimage(ctx: discord.ext.commands.Context, user: discord.User):
    avatar = user.avatar_url_as(format="png", static_format="png", size=64)
    name = f"{user.name}#{user.discriminator}"
    image_data = await gen_image.getwelcomeimage(name=name, avatar=avatar)
    # emb = discord.Embed()
    await ctx.channel.send(file=image_data)


@bot.command(brief="Links", description="Shows the links to github.")
async def github(ctx: discord.ext.commands.Context):
    embed = discord.Embed(title=f"Github links",
                          colour=discord.Colour.random().value)
    embed.add_field(name="watermelonbot (python)", 
                    value="https://github.com/DogeMultiverse/watermelonbot",inline=False)
    embed.add_field(name="Hex Alex plugin (java)",
                    value="https://github.com/alexpvpmindustry/HexedPlugin", inline=False)
    embed.add_field(name="lol bot (javascript) ( not maintained ;-; )",
                    value="https://github.com/unjown/unjownbot", inline=False)
    await ctx.channel.send(embed=embed)


@bot.command(brief="Links", description="Shows the links to donate.")
async def donate(ctx: discord.ext.commands.Context):
    embed = discord.Embed(title=f"Donation links",
                          colour=discord.Colour.random().value)
    embed.add_field(name="ko-fi ($0 Fee)",
                    value="https://ko-fi.com/dogemultiverse", inline=False)
    embed.add_field(
        name="PayPal", value="https://www.paypal.com/paypalme/alexservers", inline=False)
    embed.add_field(name="Buy Me A Coffee",
                    value="https://www.buymeacoffee.com/alexservers", inline=False)
    embed.add_field(
        name="Patreon", value="https://www.patreon.com/DogeMultiverse", inline=False)
    await ctx.channel.send(embed=embed)


@bot.command(brief="Links", description="Shows the affiliate links.", aliases=['aff'])
async def affiliate(ctx: discord.ext.commands.Context):
    embed = discord.Embed(title=f"Affiliate links",
                          colour=discord.Colour.random().value)
    embed.add_field(name="Cheap VPS & webhosting", value="https://my.racknerd.com/aff.php?aff=10213",
                    inline=False)
    await ctx.channel.send(embed=embed)


@bot.command(brief="Links", description="Shows the link to FAQ.")
async def faq(ctx: discord.ext.commands.Context):
    embed = discord.Embed(title=f"FAQ link",
                          colour=discord.Colour.random().value)
    embed.add_field(name="FAQ", value="https://discord.com/channels/785543836608364556/785543836750315616",
                    inline=False)
    embed.add_field(name="Information", value="https://discord.com/channels/785543836608364556/785543836608364565",
                    inline=False)
    embed.add_field(name="Rules", value="https://discord.com/channels/785543836608364556/785543836750315612",
                    inline=False)
    embed.add_field(name="Self-roles", value="https://discord.com/channels/785543836608364556/785543836750315619",
                    inline=False)
    await ctx.channel.send(embed=embed)


@bot.command(description="Create giveaway.", brief="Admin Utility",
             help="<add/remove> <giveawaychannel> <anncchannel> <amount> <winners> <days> <hours> <'msg'>")
@commands.has_any_role("Admin (Discord)", "Mod (Giveaway)")
@commands.check(is_valid_guild)
async def giveaway(ctx: discord.ext.commands.Context, what: str, channel: discord.TextChannel,
                   channelannc: discord.TextChannel, amount: int = 1,
                   winners: int = 0, days: int = 0, hours: int = 0, message: str = ""):
    cog: giveaway_bot.Giveaway = bot.get_cog("giveaway")
    if isinstance(cog, type(None)):
        bot.add_cog(giveaway_bot.Giveaway(bot))
        cog: giveaway_bot.Giveaway = bot.get_cog("giveaway")
        print("cog not started, started it")
    if what == "add":
        embed = giveaway_bot.form_msg_embed(
            message, amount, winners, days, hours * 3600, 0)
        msg = await channel.send(embed=embed)
        cog.addGiveawayEvent(msg.id, channel, channelannc,
                             message, amount, winners, days, hours)
        await msg.add_reaction(ej.ax_emoji)
        await ctx.channel.send(f"giveaway added to {channel}. Giving {amount} {ej.ax_emoji} to {winners} people.")
    elif what.startswith("remove"):
        pass
    elif what == "findall":
        pass
    else:
        await ctx.channel.send("invalid command usage")

@bot.command(description="Get members with a certain role", brief="Admin Utility")
@commands.check(is_valid_guild)
async def getmemberswithrole(ctx: discord.ext.commands.Context, *, role_name: str):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        await ctx.send(f"Role '{role_name}' not found.")
        return
    
    members = [member for member in guild.members if role in member.roles]
    member_names = "\n".join([member.name + f"#{member.discriminator}" for member in members])
    
    if member_names:
        await ctx.send(f"Members with role '{role_name}':\n{member_names}")
    else:
        await ctx.send(f"No members with role '{role_name}' found.")


@bot.command(description="Get exp of members with a certain role. Input days to see historical values",
             brief="Admin Utility",
             help="<role_name> [days]")
@commands.check(is_valid_guild)
async def getexpofmemberswithrole(ctx: discord.ext.commands.Context, *, args: str):
    import re
    args_list = args.rsplit(' ', 1)
    if len(args_list) == 2 and re.match(r'^\d+$', args_list[1]):
        role_name = args_list[0]
        days = int(args_list[1])
    else:
        role_name = args
        days = 7
    
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name.strip())
    if role is None:
        await ctx.send(f"Role '{role_name}' not found.")
        return
    
    members = [member for member in guild.members if role in member.roles]
    members_id = [member.id for member in members]
    date_threshold = datetime.now() - timedelta(days=days)

    pipeline = [
        {'$match': {'duuid': {'$in': members_id}}},
        {'$project': {
            'duuid': 1,
            'EXP': 1,
            'COUNTS': {
                '$size': {
                    '$filter': {
                        'input': '$dates',
                        'as': 'date',
                        'cond': {'$gte': ['$$date', date_threshold]}
                    }
                }
            },
            '_id': 0
        }}
    ]
    documents = expv7.aggregate(pipeline)
    exp_by_duuid = {doc["duuid"]: {"EXP": doc["EXP"], "COUNTS": doc["COUNTS"]} for doc in documents}
    member_details = "\n".join(
        [
            f"`{member.name}#{member.discriminator}`    EXP [`{exp_by_duuid.get(member.id, {}).get('EXP', 0)}`]    TIME [`{exp_by_duuid.get(member.id, {}).get('COUNTS', 0)*3}`]"
            for member in members
        ]
    )
    
    if member_details:
        withS = "s" if days>1 else ""
        await ctx.send(f"Members with role '{role_name}'. Playtime in the last {days} day{withS}:\n{member_details}")
    else:
        await ctx.send(f"No members with role '{role_name}' found.")


@bot.command(description="Check user's registered account's EXP", brief="Utility")
@commands.check(is_valid_guild)
async def checkexp(ctx: discord.ext.commands.Context, user: discord.User = None):
    await mindustry.checkexp(ctx, user, prefix, expv7, convertedexpv7, convertedexpv6=convertedexp, expgainsv6=expgains)


@bot.command(description=f"Convert user's exp into {ej.ax_emoji}.", brief="Utility")
@commands.check(is_valid_guild)
async def convertexp(ctx: discord.ext.commands.Context):
    await mindustry.convertexp(ctx, prefix, expv7, convertedexpv7, convertedexpv6=convertedexp, expgainsv6=expgains,
                               ax=axdatabase)


@bot.command(description="For appealing a banned account of a registered member", brief="Utility",
             help="<minecraftBan|terrariaBan|mindustryKick|mindustryBan> <in_game_name> <reason>")
@commands.check(is_valid_guild)
async def appeal(ctx: discord.ext.commands.Context, punishment: str, idoruuid: str, *, reason: str):
    if not punishment.startswith(("minecraftBan", "terrariaBan", "mindustryKick", "mindustryBan")):
        await ctx.channel.send("you must fill a punishment type:"
                               "\nmindustryBan, mindustryKick, terrariaBan, minecraftBan")
        return
    if isinstance(reason, type(None)) or reason == "":
        await ctx.channel.send("you must fill a reason of you got banned/kick")
        return
    await ctx.send("Thanks for appealing. Please be patient while our moderators attend to your appeal.")
    channel = bot.get_channel(APPEAL_CHANNEL)  # appeal-submission
    embed = discord.Embed(title="Appeal")
    embed.set_author(name=ctx.author.name + "#" +
                          ctx.author.discriminator, icon_url=ctx.author.avatar_url)
    embed.add_field(name="Type:", value=str(punishment) +
                                        f" {ctx.author.mention}", inline=False)
    embed.add_field(name="In-game Player Name:",
                    value=str(idoruuid), inline=False)
    embed.add_field(name="Reason:", value=str(reason), inline=False)

    # check if user is registered or not.
    # also, returns the duuid
    embed.add_field(name="DUUID:", value=str(ctx.author.id), inline=False)
    await channel.send(embed=embed)


@bot.check
async def check_command_on_general(ctx: discord.ext.commands.Context):
    general_channel_id = 785543837116399636
    bot_commands_channel_id = 785543837116399637
    verification_channel_id = 791886317491191818

    is_register = ctx.message.content.startswith(f"{prefix}register")

    if is_staff(ctx.author):
        return True

    if ctx.channel.id == general_channel_id:
        if is_register:
            await ctx.reply(
                f"Please do not register in <#{ctx.channel.id}> instead do it in <#{verification_channel_id}>."
                f"\nFor other bot commands you can do it in <#{bot_commands_channel_id}>."
                f"\nYour command was `{ctx.message.content}`."
                f"\nPlease re-run your command in the correct channel."
            )
        else:
            await ctx.reply(
                f"Please do not use commands in <#{ctx.channel.id}> instead do it in <#{bot_commands_channel_id}>."
                f"\nYour command was `{ctx.message.content}`."
                f"\nPlease re-run your command in the correct channel."
            )

    return True


@bot.event
async def on_message(message: discord.Message):
    if message.guild is None:  # Ignore DMs
        return

    if not is_valid_guild_check(message.guild.id):
        return

    fig = "https://media.discordapp.net/attachments/785543837116399636/806563140116152380/reallyangrymelon.png"
    pepo_clap = "https://media.discordapp.net/attachments/799855760011427880/806869234122358794/792177151448973322.gif"
    if "<@!500744743660158987>" in message.content and prefix == "t?":
        await message.reply(fig, mention_author=True)
    elif message.content.startswith(prefix + "test"):
        await message.channel.send(f"this is to test stuff")
    elif (message.content.startswith(("ty", "Ty", "TY"))) and (bot.user in message.mentions):
        await message.reply("😊", mention_author=True)
    elif message.content == ':pepoclap:' and prefix == "t?":
        await message.reply(pepo_clap)
    elif prefix == "w?" and message.channel.id == ADMIN_LOGS_CHANNEL:  # admin logs channel
        await vkick_anti_bot(message, bot, autoban_counts, melonbotmindusbans)
    elif prefix == "w?" and message.channel.id == MODERATOR_LOGS_CHANNEL:  # moderator logs channel
        await plugin_anti_bot(message, bot, autoban_counts, melonbotmindusbans)
    elif prefix == "w?" and message.channel.id == COUNTING_CHANNEL :  # counting hardcore channel
        if message.author.id != bot.user.id:
            await counting_bot.run_counterbot(message, bot)
    elif ("#alexcookie" in message.content) and (message.channel.id == 811993295114076190) and (prefix == "w?"):
        await cookiegame.triggercookieclaim(message, axdatabase, bot)
    else:
        await bot.process_commands(message)


def strip_colourbrackets(inputstr):
    builder = ""
    remove = False
    for char in inputstr:
        if char == "[":
            remove = True
        elif char == "]":
            remove = False
        elif not remove:
            builder += char
    return builder


def runbot():
    timestr = datetime.now().isoformat(timespec='minutes')
    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARN)
    handler = logging.FileHandler(
        filename=f'logs/discord_{timestr}.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    # Assume client refers to a discord.Client subclass...
    # client.run(token, log_handler=handler, log_level=logging.DEBUG)

    with open("watermelon.config", "rb") as f:
        js = json.load(f)
        bot_token = js["bot_token"]
    # clientdisc = MyClient(intents=discord.Intents().all())
    # bot.load_extension("mastermelon.giveaway_bot2")
    bot.add_cog(giveaway_bot.Giveaway(bot))
    try:
        bot.run(bot_token)  # , log_handler=handler, log_level=logging.DEBUG)
    except KeyboardInterrupt:
        print("Exiting")
        asyncio.run(bot.close())
    except Exception as e:
        strr = traceback.format_exc()
        # melon bot ping
        with open("watermelon.config", "rb") as f:
            js = json.load(f)
            error_ping = js["error_ping"]
        requests.post(error_ping, data={
            "content": "melon bot error 910" + strr})
        raise

#     elif message.content.startswith(prefix + "claimeffect"):
#         # todo @BOUNTY # check for role precondition then give effect
#         #  https://discordpy.readthedocs.io/en/latest/api.html#reaction
#         pass
