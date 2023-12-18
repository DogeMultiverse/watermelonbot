import pymongo
from mastermelon.disc_constants import DUUID_ALEX
import discord
from pymongo.collection import Collection
from datetime import timedelta
from datetime import datetime
from collections import Counter

from mastermelon import emojis as ej


EXCHANGE_RATE=1000 # EXP to Ax

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
        str_builder += "In Game Name: `" + muuid_name[muuid_i] + "`\n"
        exp_builder = ""
        muuid_exp_dict = {"In_Game_Name": muuid_name[muuid_i], "servers": []}
        for server, exp in sorted(list(exps.items()),
                                  key=lambda x: 0 if isinstance(x[1], type(None)) else x[1], reverse=True):
            if server in ["ALEX | PVP (USA)", "ALEX | PVP (ASIA)", "ALEX | ATTACK (USA)", "ALEX | SURVIVAL (ASIA)"]:
                try:
                    exp = 0 if exp is None else exp
                    rservername = server[7:].replace(" SERVER", "")
                    serverstr = rservername + (
                        " [TOP 1%]" if exp > 40000 else (" [TOP 10%]" if exp > 15000 else ""))
                    if server[7:].replace(" SERVER", "") not in convertedexp_doc[muuid_i]:
                        convertedexp_doc[muuid_i][rservername] = {
                            "claimed": 0, "lcdate": None}
                        claimed = 0
                        lcdate = None
                    else:
                        claimed = convertedexp_doc[muuid_i][rservername]["claimed"]
                        lcdate = convertedexp_doc[muuid_i][rservername]["lcdate"]
                    if last_updated[muuid_i][server] < datetime(2023, 8, 8):
                        legacy_server = True
                    else:
                        legacy_server = False
                    exp_builder += f"{exp:>6}  " + f"{serverstr:<21}" + \
                                   last_updated[muuid_i][server].strftime(
                                       "%Y-%m-%d %H:%M") + f"   {claimed:<6} "+("(legacy server)" if legacy_server else "") + "\n"
                    muuid_exp_dict["servers"].append({"servername": rservername,
                                                      "exp": exp, "claimed": claimed, "lcdate": lcdate,
                                                      "lupdated": last_updated[muuid_i][server],
                                                      "legacy_server": legacy_server
                                                      })
                except Exception as e:
                    print(exp, server)
                    print(str(e))
        if len(exp_builder) > 0:
            exp_builder = "```\n <EXP>  <SERVER>             <LASTUPDATED,UTC>  <CLAIMED>\n" + \
                          exp_builder + "\n```"
            str_builder += exp_builder
            exp_dict[muuid_i] = muuid_exp_dict
    return str_builder, exp_dict, convertedexp_doc


async def checkexp(ctx: discord.ext.commands.Context, user: discord.User, prefix: str, expgains: Collection,
                   convertedexp: Collection, convertedexpv6: Collection, expgainsv6: Collection):
    if prefix == "t?" and ctx.author.id != DUUID_ALEX:
        await ctx.channel.send(f"{ctx.author.name} no testing for u")
        return 
    if isinstance(user, type(None)):
        userTarget = ctx.author.id
    else:
        userTarget = user.id
    await ctx.channel.send('Getting exp', delete_after=3)

    exp_doc : pymongo.Documents = expgains.find_one({"duuid": userTarget},{"_id": 0, "musername": 1, "EXP": 1, "servers": 1})
    if exp_doc is None:
        await ctx.channel.send(f"{ctx.author.name}: User has no EXP or user not found.")
        return
    convertedexp_doc : pymongo.Documents = convertedexp.find_one({"duuid": userTarget})
    EXP = exp_doc["EXP"]
    if convertedexp_doc is None:
        latest_claim = get_latest_claim(userTarget,convertedexpv6,expgainsv6)
        latest_claim = min(EXP,latest_claim)//EXCHANGE_RATE*EXCHANGE_RATE
        convertedexp_doc = {"duuid": userTarget, "convertedexp": latest_claim, "lastconvertdate":datetime.utcnow() }
        convertedexp.insert_one(convertedexp_doc)
    # convertedexp_doc should have 3 fields.
    str_time=convertedexp_doc["lastconvertdate"].strftime("%a %d %b %Y, %I:%M%p")+" (UTC)"
    await ctx.channel.send( f'Current EXP for {ctx.author.name}: `{EXP:,}`\n'\
                            f'Converted EXP: `{convertedexp_doc["convertedexp"]:,}`\n'\
                            f'Last converted: `{str_time}`\n'\
                            f'Use `{prefix}convertexp` to convert your EXP to {ej.ax_emoji} (minimum `{EXCHANGE_RATE:,}`EXP). You will still keep your EXP.'
                            )
    # TODO make this formating better

async def convertexp(ctx: discord.ext.commands.Context, user: discord.User, prefix: str, expgains: Collection,
                   convertedexp: Collection, convertedexpv6: Collection, expgainsv6: Collection):
    await ctx.channel.send(f'Coming soon...')

def get_latest_claim(duuid,convertedexpv6,expgainsv6):
    docs = expgainsv6.find({"duuid":duuid}).sort("EXP",-1).limit(1)
    servername=""
    for d in docs:
        servername=d["servername"]
    latest_claim = 0
    docs2 = convertedexpv6.find({"duuid":duuid}).limit(1)
    for d in docs2:
        for muuid,docc in d["converted"].items():
            if servername[7:] in docc:
                claimed = docc[servername[7:] ]["claimed"]
                if claimed>latest_claim:
                    latest_claim=claimed
    return latest_claim


async def convertexp(ctx: discord.ext.commands.Context, user: discord.User, prefix: str, expgains: Collection, convertedexp: Collection):
    if prefix == "t?" and ctx.author.id != DUUID_ALEX:
        await ctx.channel.send("no testing for u")
        return 
    if isinstance(user, type(None)):
        userTarget = ctx.author.id
    else:
        userTarget = user.id
    await ctx.channel.send('Converting exp', delete_after=3)
    
    
async def checkexp_legacy(ctx: discord.ext.commands.Context, user: discord.User, prefix: str, expgains: Collection, convertedexp: Collection):
    if prefix == "t?" and ctx.author.id != DUUID_ALEX:
        await ctx.channel.send("no testing for u")
        return 
    if isinstance(user, type(None)):
        userTarget = ctx.author.id
    else:
        userTarget = user.id
    await ctx.channel.send('getting exp', delete_after=3)
    cursor = expgains.find({"duuid": userTarget})
    convertedexp_doc = convertedexp.find_one({"duuid": userTarget})
    if convertedexp_doc is None:
        convertedexp.insert_one({"duuid": userTarget, "converted": None})
    else:
        convertedexp_doc = convertedexp_doc["converted"]
    res = []
    for i, cur in enumerate(cursor):
        res.append(cur)
    if len(res) == 0:
        print("User has no EXP.")
        await ctx.channel.send("User has no EXP or user not found.")
    else:
        str_builder, exp_dict, convertedexp_doc = get_latest_exp(
            res, convertedexp_doc)
        if len(str_builder) > 0:
            convertedexp.find_one_and_replace({"duuid": userTarget},
                                              {"duuid": userTarget, "converted": convertedexp_doc})

            # todo count the amount of unconverted exp and trigger the next line if there is
            if len(str_builder) >= 1850:
                temp_str_builder = ""
                sent = False
                for i, strr in enumerate(str_builder.split("In Game Name: ")):
                    if i != 0:
                        temp_str_builder += "In Game Name: " + strr
                        sent = False
                        if i % 3 == 0:
                            await ctx.channel.send(temp_str_builder)
                            sent = True
                            temp_str_builder = ""
                if not sent:
                    await ctx.channel.send(temp_str_builder)
                await ctx.channel.send(f"\n Type `{prefix}convertexp` to convert your EXP into {ej.ax_emoji}."
                                       f"(You still can keep your EXP)")
            else:
                await ctx.channel.send(
                    str_builder +
                    f"\n Type `{prefix}convertexp` to convert your EXP into {ej.ax_emoji}."
                    f"(You still can keep your EXP)")
        else:
            await ctx.channel.send("You have no exp. ;-;")