import discord
import json
import pymongo
import asyncio
import random
from pyexamples import counting_bot


def get_latest_exp(res, convertedexp_doc):
    muuid = {}
    muuid_name = {}
    last_updated = {}
    exp_list = []
    if convertedexp_doc is None:
        convertedexp_doc = {}
    for doc in res:
        if doc["muuid"] not in muuid:
            muuid[doc["muuid"]] = {doc["servername"]: doc["EXP"]}
            muuid_name[doc["muuid"]] = doc["musername"]
            last_updated[doc["muuid"]] = {doc["servername"]: doc["date"]}
        elif (doc["servername"] in muuid[doc["muuid"]]) and (
                muuid[doc["muuid"]][doc["servername"]] < doc["EXP"]):
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
            exp_list.append(muuid_exp_dict)
    return str_builder, exp_list, convertedexp_doc


class MyClient(discord.Client):
    def __init__(self, **options):

        with open("watermelon.config", "rb") as f:
            js = json.load(f)
            mongo_key = js["mongo_key"]
            self.prefix = js["prefix"]
        if self.prefix in ["w!", "t!"]:  # only access mongodb for w! and t!
            client = pymongo.MongoClient(mongo_key)
            db = client.get_database("AlexMindustry")
            self.expgains = db["expgains"]
            self.convertedexp = db["convertedexp"]
            self.ax = db["ax"]
        super().__init__(**options)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        prefix = self.prefix
        if message.content.startswith(prefix + 'help'):
            await message.channel.send(
                'Available commands: `help`, `hello`, `guess`, `checkexp` , `github`. Prefix is `' + prefix + "` .\n" +
                "Other bots commands: `a?help`, `lol help`, `,suggest help`")
        elif message.content.startswith(prefix + 'guess'):
            await message.channel.send('Guess a number between 1 and 1000000. Its one in a million')

            def is_correct(m):
                print(message.author.id, message.author)
                print(type(message.author.id))
                if message.author.id in [500744743660158987, 612861256189083669]:
                    return random.randint(1, 10) > 3
                return m.author == message.author and m.content.isdigit()

            answer = random.randint(1, 1000000)
            try:
                guess = await self.wait_for('message', check=is_correct, timeout=20.0)
            except asyncio.TimeoutError:
                return await message.channel.send('Sorry, you took too long it was {}.'.format(answer))
            if int(guess.content) > 1000000:
                await message.channel.send('Number too large, should be <1000000. Game ends.')
                return
            if int(guess.content) == answer or False \
                    and ((message.author.id in [500744743660158987, 612861256189083669])
                         and random.randint(1, 10) > 5):
                await message.channel.send('You are right!')
            else:
                await message.channel.send('Oops. It is actually {}.'.format(answer))

        elif message.content.startswith(prefix + 'hello'):
            await message.reply('Hello!', mention_author=True)
        elif message.content.startswith(prefix + "checkexp"):
            if prefix == "t!" and message.author.id != 612861256189083669:
                await message.channel.send("no testing for u")
                return
            await message.channel.send('getting exp')
            cursor = self.expgains.find({"duuid": message.author.id})
            convertedexp_doc = self.convertedexp.find_one({"duuid": message.author.id})
            if convertedexp_doc is None:
                self.convertedexp.insert_one({"duuid": message.author.id, "converted": None})
            else:
                convertedexp_doc = convertedexp_doc["converted"]
            res = []
            for i, cur in enumerate(cursor):
                res.append(cur)
            if len(res) == 0:
                print("User has no EXP.")
                await message.channel.send("User has no EXP or user not found.")
            else:
                # await message.channel.send('user found')
                str_builder, exp_dict, convertedexp_doc = get_latest_exp(res, convertedexp_doc)
                if len(str_builder) > 0:
                    self.convertedexp.find_one_and_replace({"duuid": message.author.id},
                                                           {"duuid": message.author.id, "converted": convertedexp_doc})
                    await message.channel.send(str_builder)
                else:
                    await message.channel.send("You have no exp. ;-;")

        elif message.content.startswith(prefix + "buyeffect"):
            if prefix == "t!" and message.author.id != 612861256189083669:
                await message.channel.send("coming soon")
                return
            # checks for price n balance, if valid, make purchase, else error message

        elif message.content.startswith(prefix + "convertexp"):
            if prefix == "t!" and message.author.id != 612861256189083669:
                await message.channel.send("coming soon")
                return
            # add a new collection to show how much was claimed # add last claimed time.
        elif message.content.startswith(prefix + "github"):
            await message.channel.send("watermelonbot: https://github.com/alexpvpmindustry/watermelonbot\n" +
                                       "lol bot: https://github.com/unjown/unjownbot")

        elif message.content.startswith(prefix):
            await message.channel.send("Unknown command, type `" + prefix + "help` for help.")
        elif prefix == "w!" and message.channel.id == 805105861450137600:
            await counting_bot.run_counterbot(message, self)
        elif prefix == "t!" and message.channel.id == 805105861450137600:
            pass


def runbot():
    with open("watermelon.config", "rb") as f:
        js = json.load(f)
        bot_token = js["bot_token"]
    clientdisc = MyClient(intents=discord.Intents().all())
    clientdisc.run(bot_token)
