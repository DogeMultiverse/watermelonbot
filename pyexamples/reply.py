from datetime import datetime

import discord
import json
import pymongo
import asyncio
import random
from discord.ext import commands
from pyexamples import counting_bot
from pyexamples import highlow_game
import time


def get_latest_exp(res, convertedexp_doc):
    muuid = {}
    muuid_name = {}
    last_updated = {}
    exp_dict = {}
    if convertedexp_doc is None:
        convertedexp_doc = {}
    for doc in res:
        if doc["EXP"] is None:
            doc["EXP"] = 0
        if doc["muuid"] not in muuid:
            muuid[doc["muuid"]] = {doc["servername"]: doc["EXP"]}
            muuid_name[doc["muuid"]] = doc["musername"]
            last_updated[doc["muuid"]] = {doc["servername"]: doc["date"]}
        elif (doc["servername"] in muuid[doc["muuid"]]) and (muuid[doc["muuid"]][doc["servername"]] < doc["EXP"]):
            muuid[doc["muuid"]][doc["servername"]] = doc["EXP"]
            muuid_name[doc["muuid"]] = doc["musername"]
            last_updated[doc["muuid"]][doc["servername"]] = doc["date"]
        else:
            muuid[doc["muuid"]][doc["servername"]] = doc["EXP"]
            last_updated[doc["muuid"]][doc["servername"]] = doc["date"]
        if doc["muuid"] not in convertedexp_doc:
            convertedexp_doc[doc["muuid"]] = {}
    str_builder = ""
    for muuid_i, exps in muuid.items():
        str_builder += "In Game Name: `" + muuid_name[muuid_i] + "`\n"  # +str(exps) +"\n"
        exp_builder = ""
        muuid_exp_dict = {"In_Game_Name": muuid_name[muuid_i], "servers": []}
        for server, exp in sorted(list(exps.items()),
                                  key=lambda x: 0 if isinstance(x[1], type(None)) else x[1], reverse=True):
            if server in ["ALEX | ATTACK SERVER", "ALEX | PVP SERVER", "ALEX | SURVIVAL SERVER",
                          'ALEX | TURBO PVP SERVER', "ALEX | PVP SERVER (ASIA)"]:
                try:
                    exp = 0 if exp is None else exp
                    rservername = server[7:].replace(" SERVER", "")
                    serverstr = rservername + (
                        " [TOP 1%]" if exp > 40000 else (" [TOP 10%]" if exp > 15000 else ""))
                    if server[7:].replace(" SERVER", "") not in convertedexp_doc[muuid_i]:
                        convertedexp_doc[muuid_i][rservername] = {"claimed": 0, "lcdate": None}
                        claimed = 0
                        lcdate = None
                    else:
                        claimed = convertedexp_doc[muuid_i][rservername]["claimed"]
                        lcdate = convertedexp_doc[muuid_i][rservername]["lcdate"]
                    exp_builder += f"{exp:>6}  " + f"{serverstr:<21}" + \
                                   last_updated[muuid_i][server].strftime("%Y-%m-%d %H:%M") + f"   {claimed:<6}" + "\n"
                    muuid_exp_dict["servers"].append({"servername": rservername,
                                                      "exp": exp, "claimed": claimed, "lcdate": lcdate,
                                                      "lupdated": last_updated[muuid_i][server]
                                                      })
                except Exception as e:
                    print(exp, server)
                    print(str(e))
        if len(exp_builder) > 0:
            exp_builder = "```\n <EXP>  <SERVER>             <LASTUPDATED,UTC>  <CLAIMED>\n" + exp_builder + "\n```"
            str_builder += exp_builder
            exp_dict[muuid_i] = muuid_exp_dict
    return str_builder, exp_dict, convertedexp_doc


#
# class MyClient(discord.Client):
#     def __init__(self, **options):
#
#         with open("watermelon.config", "rb") as f:
#             js = json.load(f)
#             mongo_key = js["mongo_key"]
#             self.prefix = js["prefix"]
#         if self.prefix in ["w?", "t?"]:  # only access mongodb for w? and t?
#             client = pymongo.MongoClient(mongo_key)
#             db = client.get_database("AlexMindustry")
#             self.expgains = db["expgains"]
#             self.convertedexp = db["convertedexp"]
#             self.ax = db["ax"]
#             self.ingamecosmetics = db["ingamecosmetics"]
#         self.banner_gif = "https://tenor.com/view/rainbow-bar-rainbow-bar-colorful-line-gif-17716887"
#         self.ax_emoji = "<:Ax:789661633214676992>"
#         self.pog_emoji = "<:pog:786886696552890380>"
#         self.feelsbm_emoji = "<:feelsbadman:789511704777064469>"
#         super().__init__(**options)
#
#     async def on_ready(self):
#         print('Logged in as')
#         print(self.user.name)
#         print(self.user.id)
#         print('------')
#
#     async def sleep_add_reaction(self, msg, duration, emoji="<:pog:786886696552890380>"):
#         await asyncio.sleep(duration)
#         await msg.add_reaction(emoji)
#
#     async def on_message(self, message):
#         # we do not want the bot to reply to itself
#         if message.author.id == self.user.id:
#             return
#         prefix = self.prefix
#         if message.content.startswith(prefix + 'help'):
#             await message.channel.send(
#                 'Available commands: `help`, `hello`, `guess`, `checkexp`, `convertexp`, `buyeffect`, `github`. '
#                 'Prefix is `' + prefix + "` .\n" +
#                 "Other bots commands: `a?help`, `lol help`, `,suggest help`")
#         elif message.content.startswith(prefix + 'guess'):
#             await message.channel.send('Guess a number between 1 and 1000000. Its one in a million')
#
#             def is_correct(m):
#                 return m.author == message.author and m.content.isdigit() and m.channel == message.channel
#
#             answer = random.randint(1, 1000000)
#             try:
#                 guess = await self.wait_for('message', check=is_correct, timeout=20.0)
#             except asyncio.TimeoutError:
#                 return await message.channel.send('Sorry, you took too long it was {}.'.format(answer))
#             if int(guess.content) > 1000000:
#                 await message.channel.send('Number too large, should be <1000000. Game ends.')
#                 return
#             if int(guess.content) == answer or False \
#                     and ((message.author.id in [500744743660158987, 612861256189083669])
#                          and random.randint(1, 10) > 5):
#                 await message.channel.send('You are right?')
#             else:
#                 await message.channel.send('Oops. It is actually {}.'.format(answer))
#
#         elif message.content.startswith(prefix + 'hello'):
#             await message.reply('Hello!', mention_author=True)
#         elif message.content.startswith(prefix + "checkexp"):
#             if prefix == "t?" and message.author.id != 612861256189083669:
#                 await message.channel.send("no testing for u")
#                 return
#             await message.channel.send('getting exp')
#             cursor = self.expgains.find({"duuid": message.author.id})
#             convertedexp_doc = self.convertedexp.find_one({"duuid": message.author.id})
#             if convertedexp_doc is None:
#                 self.convertedexp.insert_one({"duuid": message.author.id, "converted": None})
#             else:
#                 convertedexp_doc = convertedexp_doc["converted"]
#             res = []
#             for i, cur in enumerate(cursor):
#                 res.append(cur)
#             if len(res) == 0:
#                 print("User has no EXP.")
#                 await message.channel.send("User has no EXP or user not found.")
#             else:
#                 # await message.channel.send('user found')
#                 str_builder, exp_dict, convertedexp_doc = get_latest_exp(res, convertedexp_doc)
#                 if len(str_builder) > 0:
#                     self.convertedexp.find_one_and_replace({"duuid": message.author.id},
#                                                            {"duuid": message.author.id, "converted": convertedexp_doc})
#                     await message.channel.send(str_builder)
#                 else:
#                     await message.channel.send("You have no exp. ;-;")
#         elif message.content.startswith(prefix + "claimeffect"):
#             # todo @BOUNTY # check for role precondition then give effect
#             #  https://discordpy.readthedocs.io/en/latest/api.html#reaction
#             pass
#         elif message.content.startswith(prefix + "restartservers"):
#             # todo @BOUNTY # check for role precondition then soft restart and hard restart
#             pass
#         elif message.content.startswith(prefix + "buyeffect"):
#             if prefix == "t?" and message.author.id != 612861256189083669:
#                 await message.channel.send("t? is only for alex to test")
#                 return
#             await message.channel.send("Fetching effects...", delete_after=2)
#             effects_cost = {20: ["yellowDiamond", "yellowSquare", "yellowCircle"],
#                             30: ["greenCircle", "whiteDoor", "yellowLargeDiam", "yellowSpark"],
#                             50: ["whiteLancerRandom"], 80: ["whiteLancerRadius", "pixel", "bubble"],
#                             200: ["rainbowPixel", "rainbowBubble"]}
#             effects = [ee for c, e in effects_cost.items() for ee in e]
#             owned_effects_collection = self.ingamecosmetics.find_one({"duuid": message.author.id})
#             if owned_effects_collection is None:
#                 await message.channel.send("error, pls **PING** alex! error 170")
#                 return
#             owned_effects = owned_effects_collection["effects"]
#             duuid = message.author.id
#             if self.ax.find_one({"duuid": duuid}) is None:
#                 balance = 0
#                 self.ax.insert_one({"duuid": duuid, "ax": 0})
#             else:
#                 balance = self.ax.find_one({"duuid": duuid})["ax"]
#             if message.content == (prefix + "buyeffect"):
#                 strbuilder = ""
#                 for cost, effectname in effects_cost.items():
#                     strbuilder += f"`{cost:>3} `" + self.ax_emoji + "`  " + \
#                                   "`, `".join([eff + ("✅" if eff + "Effect" in owned_effects else "")
#                                                for eff in effectname]) + "`\n"
#                 content = f"(Current balance: `{balance}` {self.ax_emoji})"
#                 desc = f"`  Price   Effects`  {content}\n" + strbuilder + \
#                        "\nType `" + prefix + "buyeffect XXXX` to buy the effect. (cAsE sEnSiTiVe)" + \
#                        "\nNote: `✅`=owned. Purchased effects are non-refundable. " \
#                        "\nIf color is not specified in the effect, it is *configurable* via `/color` in game."
#                 embed = discord.Embed.from_dict(
#                     {"title": f"Alex Mindustry *special* `Effects MENU`", "description": desc,
#                      "color": discord.Colour.dark_grey().value})
#                 await message.channel.send(embed=embed)
#                 await message.channel.send(self.banner_gif)
#             elif len(message.content.split(" ")) == 2:
#                 await message.channel.send("Validating purchase...", delete_after=2)
#                 try:
#                     peffect = message.content.split(" ")[1]
#                     if (peffect in effects) and not (peffect + "Effect" in owned_effects):
#                         peffectcost = [c for c, e in effects_cost.items() if peffect in e][0]
#                         duuid = message.author.id
#                         balance = self.ax.find_one({"duuid": duuid})["ax"]
#                         if balance >= peffectcost:
#                             self.ax.find_one_and_replace({"duuid": duuid},
#                                                          {"duuid": duuid, "ax": balance - peffectcost})
#                             self.ingamecosmetics.find_one_and_update({"duuid": duuid},
#                                                                      {"$push": {"effects": peffect + "Effect"}})
#                             desc = f"Purchase successful. Congrats! Now you can flex `{peffect}`" \
#                                    f"\nYou have {balance - peffectcost} {self.ax_emoji} now." \
#                                    f"\nType `/effect {peffect}` in **Alex Mindustry** to use it."
#                             embed = discord.Embed.from_dict(
#                                 {"description": desc, "color": discord.Colour.green().value})
#                             react = await message.channel.send(embed=embed)
#                             await self.sleep_add_reaction(react, 5)
#                         else:
#                             desc = f"You **dont** have enough {self.ax_emoji} to make the purchase. Balance: " \
#                                    f"{balance} {self.ax_emoji}.\nPlay more for **EXP** or " \
#                                    f"collect <#786110451549208586>. "
#                             embed = discord.Embed.from_dict(
#                                 {"description": desc, "color": discord.Colour.dark_red().value})
#                             react = await message.channel.send(embed=embed)
#                             await self.sleep_add_reaction(react, 5, emoji=self.feelsbm_emoji)
#                     elif peffect in effects:
#                         desc = f"You already **have** this effect.\nType `/effect {peffect}` in **Alex Mindustry** to use it."
#                         embed = discord.Embed.from_dict(
#                             {"description": desc, "color": discord.Colour.dark_red().value})
#                         react = await message.channel.send(embed=embed)
#                         await self.sleep_add_reaction(react, 5)
#                     else:
#                         await message.channel.send("Effect not known. Spell properly and effects *are* cAsE sEnSiTiVe.")
#                 except Exception as e:
#                     print(str(e))
#                     await message.channel.send("error, pls **PING** alex! error 189:" + str(e))
#             else:
#                 await message.channel.send("Wrong usage of command.")
#             # await message.channel.send("coming soon")
#             # checks for price n balance, if valid, make purchase, else error message
#         elif message.content.startswith(prefix + "axleaderboard"):
#             await message.channel.send("type `a?axleaderboard`")
#         elif message.content == (prefix + "highlow"):
#             await highlow_game.run_highlowgame(message, self)
#         elif message.content.startswith(prefix + "convertexp"):
#             if prefix == "t?" and message.author.id != 612861256189083669:
#                 await message.channel.send("t? is only for alex to test")
#                 return
#             await message.channel.send(f'Converting EXP: 1000 EXP -> 1 {self.ax_emoji}. Minimum conversion = 1000 EXP.')
#             # add a new collection to show how much was claimed # add last claimed time.
#             cursor = self.expgains.find({"duuid": message.author.id})
#             convertedexp_doc = self.convertedexp.find_one({"duuid": message.author.id})
#             if convertedexp_doc is None:
#                 self.convertedexp.insert_one({"duuid": message.author.id, "converted": None})
#             else:
#                 convertedexp_doc = convertedexp_doc["converted"]
#             res = []
#             for i, cur in enumerate(cursor):
#                 res.append(cur)
#             if len(res) == 0:
#                 await message.channel.send("User has no EXP or user not found. Can't convert emptiness.")
#                 return
#             else:
#                 str_builder, exp_dict, convertedexp_doc = get_latest_exp(res, convertedexp_doc)
#                 if len(str_builder) > 0:
#                     new_Ax = 0
#                     for muuid, exps in exp_dict.items():
#                         for servdata in exps["servers"]:
#                             rservername = servdata["servername"]
#                             exp = servdata["exp"]
#                             if exp is None:
#                                 exp = 0
#                             claimed = servdata["claimed"]
#                             claims = (exp - claimed) // 1000  # integer division
#                             new_Ax += claims
#                             servdata["claimed"] += claims * 1000
#                             convertedexp_doc[muuid][rservername] = {"claimed": servdata["claimed"],
#                                                                     "lcdate": datetime.utcnow()}
#                     self.convertedexp.find_one_and_replace({"duuid": message.author.id},
#                                                            {"duuid": message.author.id, "converted": convertedexp_doc})
#                     if self.ax.find_one({"duuid": message.author.id}) is None:
#                         self.ax.insert_one({"duuid": message.author.id, "ax": new_Ax})
#                     else:
#                         self.ax.find_one_and_update({"duuid": message.author.id}, {"$inc": {"ax": new_Ax}})
#                     await message.channel.send(
#                         f"You have converted {new_Ax * 1000} EXP into {new_Ax} {self.ax_emoji}. Congrats!. Type "
#                         f"`a?checkax @user` to check your current {self.ax_emoji}.")
#                 else:
#                     await message.channel.send("You have no exp. ;-; Can't convert emptiness.")
#         elif message.content.startswith(prefix + "github"):
#             await message.channel.send("watermelonbot: https://github.com/alexpvpmindustry/watermelonbot\n" +
#                                        "lol bot: https://github.com/unjown/unjownbot")
#         elif '<@!804013622963208213>' in message.content:
#             if prefix == "w?":
#                 await message.channel.send(prefix + 'is my prefix')
#         elif message.content.startswith(prefix):
#             await message.channel.send("Unknown command, type `" + prefix + "help` for help.")
#         elif prefix == "w?" and message.channel.id == 805105861450137600:
#             await counting_bot.run_counterbot(message, self)
#         elif prefix == "t?" and message.channel.id == 805105861450137600:
#             pass


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
    db = client.get_database("AlexMindustry")
    expgains = db["expgains"]
    convertedexp = db["convertedexp"]
    ax = db["ax"]
    ingamecosmetics = db["ingamecosmetics"]
    print("mongodb key loaded")

banner_gif = "https://tenor.com/view/rainbow-bar-rainbow-bar-colorful-line-gif-17716887"
ax_emoji = "<:Ax:789661633214676992>"
pog_emoji = "<:pog:786886696552890380>"
feelsbm_emoji = "<:feelsbadman:789511704777064469>"


async def sleep_add_reaction(msg, duration, emoji="<:pog:786886696552890380>"):
    await asyncio.sleep(duration)
    await msg.add_reaction(emoji)


bot = commands.Bot(command_prefix=prefix, description=description, intents=intents)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def highlow(ctx):
    await highlow_game.run_highlowgame(ctx, bot)


@bot.command()
async def getemojis(ctx):
    emojis = await ctx.guild.fetch_emojis()
    for emoji in emojis:
        if emoji.animated:
            print(emoji.name)
            await ctx.message.add_reaction(emoji)
    await ctx.channel.send("added animated all emojis")


@bot.command(description="adds <:EMOJI:> to the desired <message_id>. max 20 emojis per message")
async def addemoji(ctx, emoji: str, messageid: int, channel: discord.TextChannel = None):
    # todo fix error message when command invalid
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


@bot.command(description="adds hype emojis")
async def addhype(ctx, messageid: int, channel: discord.TextChannel = None, counts: int = 5):
    # todo fix error message when command invalid
    emojis = await ctx.guild.fetch_emojis()
    try:
        if channel is None:
            msg = await ctx.fetch_message(messageid)
        else:
            msg = await channel.fetch_message(messageid)
        total_emojis = 0
        await ctx.send(f"Hype sending! Self destructing...", delete_after=3)
        for emoji_custom in random.sample(emojis, k=len(emojis)):
            if emoji_custom.name.lower() in ["partyglasses", "pepoclap", "roll", "blob", "auke",
                                             "catdance", "pog", "hypertada", "cata", "petangry", "typing",
                                             "petmelon", "petalex"]:
                total_emojis += 1
                time.sleep(random.randint(3, 3 + counts * 10))
                await msg.add_reaction(emoji_custom)
            if total_emojis > counts:
                break
    except discord.NotFound:
        await ctx.send("Message id not found. Maybe message was deleted?", delete_after=3)
    await ctx.message.delete(delay=3)


@bot.event
async def on_command_error(ctx: discord.ext.commands.Context, error: Exception):
    print(ctx, str(error))
    if isinstance(type(error), discord.ext.commands.UserInputError):
        await ctx.message.channel.send("Wrong arguments:" + str(error))
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.message.channel.send("ERROR: Bad arugments" + str(error))
    elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.message.channel.send("ERROR: CommandNotFound")
    else:
        await ctx.message.channel.send("Unknown error:" + str(type(error)) + str(error))


@bot.command(description="play the guessing number game")
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
    if int(guess1.content) == answer or False and ((ctx.author.id in [500744743660158987, 612861256189083669])
                                                   and random.randint(1, 10) > 5):
        await ctx.channel.send('You are right!!!!')
    else:
        await ctx.channel.send('Oops. It is actually {}.'.format(answer))


@bot.command(description="command to checkexp")
async def checkexp(ctx: discord.ext.commands.Context):
    if prefix == "t?" and ctx.author.id != 612861256189083669:
        await ctx.channel.send("no testing for u")
        return
    await ctx.channel.send('getting exp', delete_after=3)
    cursor = expgains.find({"duuid": ctx.author.id})
    convertedexp_doc = convertedexp.find_one({"duuid": ctx.author.id})
    if convertedexp_doc is None:
        convertedexp.insert_one({"duuid": ctx.author.id, "converted": None})
    else:
        convertedexp_doc = convertedexp_doc["converted"]
    res = []
    for i, cur in enumerate(cursor):
        res.append(cur)
    if len(res) == 0:
        print("User has no EXP.")
        await ctx.channel.send("User has no EXP or user not found.")
    else:
        str_builder, exp_dict, convertedexp_doc = get_latest_exp(res, convertedexp_doc)
        if len(str_builder) > 0:
            convertedexp.find_one_and_replace({"duuid": ctx.author.id},
                                              {"duuid": ctx.author.id, "converted": convertedexp_doc})

            # todo count the amount of unconverted exp and trigger the next line if there is
            await ctx.channel.send(str_builder + f"\n Type `{prefix}convertexp` to convert your EXP into {ax_emoji}."
                                                 f"(You still can keep your EXP)")
        else:
            await ctx.channel.send("You have no exp. ;-;")


@bot.command()
async def buyeffect(ctx: discord.ext.commands.Context, peffect: str = None):
    if prefix == "t?" and ctx.author.id != 612861256189083669:
        await ctx.channel.send("t? is only for alex to test")
        return
    await ctx.channel.send("Fetching effects...", delete_after=2)
    effects_cost = {20: ["yellowDiamond", "yellowSquare", "yellowCircle"],
                    30: ["greenCircle", "whiteDoor", "yellowLargeDiam", "yellowSpark"],
                    50: ["whiteLancerRandom"], 80: ["whiteLancerRadius", "pixel", "bubble"],
                    200: ["rainbowPixel", "rainbowBubble"]}
    effects = [ee for c, e in effects_cost.items() for ee in e]
    owned_effects_collection = ingamecosmetics.find_one({"duuid": ctx.author.id})
    if owned_effects_collection is None:
        await ctx.channel.send("error, pls **PING** alex! error 170")
        return
    owned_effects = owned_effects_collection["effects"]
    duuid = ctx.author.id
    if ax.find_one({"duuid": duuid}) is None:
        balance = 0
        ax.insert_one({"duuid": duuid, "ax": 0})
    else:
        balance = ax.find_one({"duuid": duuid})["ax"]
    if isinstance(peffect, type(None)):
        strbuilder = ""
        for cost, effectname in effects_cost.items():
            strbuilder += f"`{cost:>3} `" + ax_emoji + "`  " + \
                          "`, `".join([eff + ("✅" if eff + "Effect" in owned_effects else "")
                                       for eff in effectname]) + "`\n"
        content = f"(Current balance: `{balance}` {ax_emoji})"
        desc = f"`  Price   Effects`  {content}\n" + strbuilder + \
               "\nType `" + prefix + "buyeffect XXXX` to buy the effect. (cAsE sEnSiTiVe)" + \
               "\nNote: `✅`=owned. Purchased effects are non-refundable. " \
               "\nIf color is not specified in the effect, it is *configurable* via `/color` in game."
        embed = discord.Embed.from_dict({"title": f"Alex Mindustry *special* `Effects MENU`", "description": desc,
                                         "color": discord.Colour.dark_grey().value})
        await ctx.channel.send(embed=embed)
        await ctx.channel.send(banner_gif)
    else:
        await ctx.channel.send("Validating purchase...", delete_after=2)
        try:
            if (peffect in effects) and not (peffect + "Effect" in owned_effects):
                peffectcost = [c for c, e in effects_cost.items() if peffect in e][0]
                duuid = ctx.author.id
                balance = ax.find_one({"duuid": duuid})["ax"]
                if balance >= peffectcost:
                    ax.find_one_and_replace({"duuid": duuid},
                                            {"duuid": duuid, "ax": balance - peffectcost})
                    ingamecosmetics.find_one_and_update({"duuid": duuid},
                                                        {"$push": {"effects": peffect + "Effect"}})
                    desc = f"Purchase successful. Congrats! Now you can flex `{peffect}`" \
                           f"\nYou have {balance - peffectcost} {ax_emoji} now." \
                           f"\nType `/effect {peffect}` in **Alex Mindustry** to use it."
                    embed = discord.Embed.from_dict(
                        {"description": desc, "color": discord.Colour.green().value})
                    react = await ctx.channel.send(embed=embed)
                    await sleep_add_reaction(react, 5)
                else:
                    desc = f"You **dont** have enough {ax_emoji} to make the purchase. Balance: " \
                           f"{balance} {ax_emoji}.\nPlay more for **EXP** or " \
                           f"collect <#786110451549208586>. "
                    embed = discord.Embed.from_dict(
                        {"description": desc, "color": discord.Colour.dark_red().value})
                    react = await ctx.channel.send(embed=embed)
                    await sleep_add_reaction(react, 5, emoji=feelsbm_emoji)
            elif peffect in effects:
                desc = f"You already **have** this effect.\nType `/effect {peffect}` in **Alex Mindustry** to use it."
                embed = discord.Embed.from_dict(
                    {"description": desc, "color": discord.Colour.dark_red().value})
                react = await ctx.channel.send(embed=embed)
                await sleep_add_reaction(react, 5)
            else:
                await ctx.channel.send("Effect not known. Spell properly and effects *are* cAsE sEnSiTiVe.")
        except Exception as e:
            print(str(e))
            await ctx.channel.send("Please re-join Alex mindustry."
                                   "\nIf you get this error again, pls **PING** alex! error 189:" + str(e))


@bot.command()
async def axleaderboard(ctx: discord.ext.commands.Context):
    await ctx.channel.send(f'for axleaderboard, type `a?axleaderboard`')


@bot.command()
async def github(ctx: discord.ext.commands.Context):
    await ctx.channel.send("watermelonbot: https://github.com/alexpvpmindustry/watermelonbot\n" +
                           "lol bot: https://github.com/unjown/unjownbot")


@bot.command()
async def convertexp(ctx: discord.ext.commands.Context):
    if prefix == "t?" and ctx.author.id != 612861256189083669:
        await ctx.channel.send("t? is only for alex to test")
        return
    await ctx.channel.send(f'Conversion rate: 1000 EXP -> 1 {ax_emoji}. '
                           f'Minimum conversion = 1000 EXP.', delete_after=20)
    # add a new collection to show how much was claimed # add last claimed time.
    cursor = expgains.find({"duuid": ctx.author.id})
    convertedexp_doc = convertedexp.find_one({"duuid": ctx.author.id})
    if convertedexp_doc is None:
        convertedexp.insert_one({"duuid": ctx.author.id, "converted": None})
    else:
        convertedexp_doc = convertedexp_doc["converted"]
    res = []
    for i, cur in enumerate(cursor):
        res.append(cur)
    if len(res) == 0:
        await ctx.channel.send("User has no EXP or user not found. Can't convert emptiness.")
        return
    else:
        str_builder, exp_dict, convertedexp_doc = get_latest_exp(res, convertedexp_doc)
        if len(str_builder) > 0:
            new_Ax = 0
            for muuid, exps in exp_dict.items():
                for servdata in exps["servers"]:
                    rservername = servdata["servername"]
                    exp = servdata["exp"]
                    if exp is None:
                        exp = 0
                    claimed = servdata["claimed"]
                    claims = (exp - claimed) // 1000  # integer division
                    new_Ax += claims
                    servdata["claimed"] += claims * 1000
                    convertedexp_doc[muuid][rservername] = {"claimed": servdata["claimed"],
                                                            "lcdate": datetime.utcnow()}
            convertedexp.find_one_and_replace({"duuid": ctx.author.id},
                                              {"duuid": ctx.author.id, "converted": convertedexp_doc})
            if ax.find_one({"duuid": ctx.author.id}) is None:
                ax.insert_one({"duuid": ctx.author.id, "ax": new_Ax})
            else:
                ax.find_one_and_update({"duuid": ctx.author.id}, {"$inc": {"ax": new_Ax}})
            await ctx.channel.send(
                f"You have converted {new_Ax * 1000} EXP into {new_Ax} {ax_emoji}.\nCongrats!. Type "
                f"`a?checkax @user` to check your current {ax_emoji}.")
        else:
            await ctx.channel.send("You have no exp. ;-; Can't convert emptiness.")


@bot.event
async def on_message(message):
    fig = "https://media.discordapp.net/attachments/785543837116399636/806563140116152380/reallyangrymelon.png"
    pepo_clap = "https://media.discordapp.net/attachments/799855760011427880/806869234122358794/792177151448973322.gif"
    if "<@!500744743660158987>" in message.content and prefix == "t?":
        await message.reply(fig, mention_author=True)
    elif message.content == ':pepoclap:' and prefix == "t?":
        await message.reply(pepo_clap)
    elif prefix == "w?" and message.channel.id == 805105861450137600: # counting hardcore channel
        await counting_bot.run_counterbot(message, bot)
    else:
        await bot.process_commands(message)


def runbot():
    with open("watermelon.config", "rb") as f:
        js = json.load(f)
        bot_token = js["bot_token"]
    # clientdisc = MyClient(intents=discord.Intents().all())
    bot.run(bot_token)

#
# @bot.event
# async def on_message(message):  # todo rewrite this whole chunk into their individual commands see eg above
#     # we do not want the bot to reply to itself
#     if message.author.id == bot.user.id:
#         return
#     if message.content.startswith(prefix + 'help'):
#         await message.channel.send(
#             'Available commands: `help`, `hello`, `guess`, `checkexp`, `convertexp`, `buyeffect`, `github`. '
#             'Prefix is `' + prefix + "` .\n" +
#             "Other bots commands: `a?help`, `lol help`, `,suggest help`")
#     elif message.content.startswith(prefix + 'guess'):
#     elif message.content.startswith(prefix + 'hello'):
#         await message.reply('Hello!', mention_author=True)
#     elif message.content.startswith(prefix + "checkexp"):
#     elif message.content.startswith(prefix + "claimeffect"):
#         # todo @BOUNTY # check for role precondition then give effect
#         #  https://discordpy.readthedocs.io/en/latest/api.html#reaction
#         pass
#     elif message.content.startswith(prefix + "restartservers"):
#         # todo @BOUNTY # check for role precondition then soft restart and hard restart
#         pass
#     elif message.content.startswith(prefix + "buyeffect"):
#         i
#     elif message.content.startswith(prefix + "axleaderboard"):
#         await message.channel.send("type `a?axleaderboard`")
#     elif message.content.startswith(prefix + "convertexp"):
#
#     elif message.content.startswith(prefix + "github"):
#         await message.channel.send("watermelonbot: https://github.com/alexpvpmindustry/watermelonbot\n" +
#                                    "lol bot: https://github.com/unjown/unjownbot")
#     elif '<@!804013622963208213>' in message.content:
#         if prefix == "w?":
#             await message.channel.send(prefix + 'is my prefix')
#     elif message.content.startswith(prefix):
#         await message.channel.send("Unknown command, type `" + prefix + "help` for help.")
#
#     elif prefix == "t?" and message.channel.id == 805105861450137600:
#         pass
