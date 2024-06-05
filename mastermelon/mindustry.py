import io
import pymongo
from mastermelon.disc_constants import DUUID_ALEX
import discord
from pymongo.collection import Collection
from datetime import timedelta
from datetime import datetime
from collections import Counter,defaultdict

from mastermelon import emojis as ej
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
        userTarget = ctx.author
    else:
        userTarget = user
    await ctx.channel.send('Getting exp', delete_after=3)

    exp_doc : pymongo.Documents = expgains.find_one({"duuid": userTarget.id},{"_id": 0, "musername": 1, "EXP": 1, "servers": 1})
    if exp_doc is None:
        await ctx.channel.send(f"{ctx.author.name}: User has no EXP or user not found.")
        return
    convertedexp_doc : pymongo.Documents = convertedexp.find_one({"duuid": userTarget.id})
    EXP = exp_doc["EXP"]
    if convertedexp_doc is None:
        latest_claim = get_latest_claim(userTarget.id,convertedexpv6,expgainsv6)
        latest_claim = min(EXP,latest_claim)//EXCHANGE_RATE*EXCHANGE_RATE
        convertedexp_doc = {"duuid": userTarget.id, "convertedexp": latest_claim, "lastconvertdate":datetime.utcnow() }
        convertedexp.insert_one(convertedexp_doc)
    # convertedexp_doc should have 3 fields.
    str_time = convertedexp_doc["lastconvertdate"].strftime("%a %d %b %Y, %I:%M%p")+" (UTC)"
    flex = getflex(EXP)
    await ctx.channel.send(
        f'{userTarget.name}:\n'
        f'Current EXP`{EXP:,}` {flex}\n'
        f'Converted EXP: `{convertedexp_doc["convertedexp"]:,}`\n'
        f'Last converted: `{str_time}`\n'
        f'Use `{prefix}convertexp` to convert your EXP to {ej.ax_emoji} (minimum `{EXCHANGE_RATE:,}`EXP). You will still keep your EXP.'
    )

    # TODO make this formating better

async def convertexp(ctx: discord.ext.commands.Context, prefix: str, expgains: Collection,
                   convertedexp: Collection, convertedexpv6: Collection, expgainsv6: Collection, ax: Collection):
    if prefix == "t?" and ctx.author.id != DUUID_ALEX:
        await ctx.channel.send(f"{ctx.author.name} no testing for u")
        return  
    userTarget = ctx.author.id 
    await ctx.channel.send(f'Converting EXP to {ej.ax_emoji}', delete_after=3)

    exp_doc : pymongo.Documents = expgains.find_one({"duuid": userTarget},{"_id": 0, "musername": 1, "EXP": 1, "servers": 1})
    if exp_doc is None:
        await ctx.channel.send("User has no EXP or user not found.")
        return
    convertedexp_doc : pymongo.Documents = convertedexp.find_one({"duuid": userTarget})
    EXP = exp_doc["EXP"]
    if convertedexp_doc is None: # first time claiming in the new system
        latest_claim = get_latest_claim(userTarget,convertedexpv6,expgainsv6)
        latest_claim = min(EXP,latest_claim)//EXCHANGE_RATE*EXCHANGE_RATE
        convertedexp_doc = {"duuid": userTarget, "convertedexp": latest_claim, "lastconvertdate":datetime.utcnow() }
        convertedexp.insert_one(convertedexp_doc)

    latest_claim = int(convertedexp_doc["convertedexp"])//EXCHANGE_RATE*EXCHANGE_RATE
    # convertedexp_doc should have 3 fields.
    # do the claim
    if (EXP-latest_claim) >= EXCHANGE_RATE: # more than exchange rate
        new_claim = (EXP-latest_claim)//EXCHANGE_RATE*EXCHANGE_RATE
        # convertedexp_doc = {"duuid": userTarget, "convertedexp": latest_claim+new_claim, "lastconvertdate":datetime.utcnow() }
        lastconvertdate = datetime.utcnow()
        convertedexp.find_one_and_update({"duuid": userTarget},{"$set": {"convertedexp": latest_claim+new_claim, "lastconvertdate":lastconvertdate}})
        # give ax
        new_ax_to_add = new_claim//EXCHANGE_RATE
        old_val = ax.find_one({"duuid": userTarget})
        if isinstance(old_val, type(None)):
            ax.insert_one({"duuid": userTarget, "ax": 0})
            old_val = 0
        else:
            old_val = old_val["ax"]
        ax.find_one_and_update({"duuid": userTarget}, {"$inc": {"ax": new_ax_to_add}})
        str_time=lastconvertdate.strftime("%a %d %b %Y, %I:%M%p")+" (UTC)"
        flex=getflex(EXP)
        await ctx.channel.send( f'{ctx.author.name} gained `{new_ax_to_add:,}` {ej.ax_emoji}\n'\
                                f'Final balance: `{old_val+new_ax_to_add:,}` {ej.ax_emoji}\n'\
                                f'Current EXP: `{EXP:,}` {flex}\n'\
                                f'Converted EXP: `{latest_claim+new_claim:,}`\n'\
                                f'Last converted: `{str_time}`\n'\
                                f'Use `{prefix}buyeffect` to buy some effects!'
                                )
    else:
        await ctx.channel.send(f"{ctx.author.name}, you dont have enough additional EXP to convert to {ej.ax_emoji}. Use `{prefix}checkexp` to check your EXP.")

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
                claimed = int(docc[servername[7:] ]["claimed"])
                if claimed>latest_claim:
                    latest_claim=claimed
    return latest_claim

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

async def plotanalytics(ctx,hourly_players,last_hours):
    def fetch_average_players(start_time,end_time):
        # Aggregate data to calculate average players per hour
        pipeline = [
            {
                '$match': {
                    'time': {'$gte': start_time, '$lte': end_time}
                }
            },
            {
                '$group': {
                    '_id': {
                        'servername': '$servername',
                        'hour': {'$hour': '$time'},
                        'year': {'$year': '$time'},
                        'month': {'$month': '$time'},
                        'day': {'$dayOfMonth': '$time'}
                    },
                    'average_players': {'$avg': '$player_count'}
                }
            },
            {
                '$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1, '_id.hour': 1}
            }
        ]
        
        result = hourly_players.aggregate(pipeline)
        
        # Process the results
        data = defaultdict(list)
        for doc in result:
            datetime_obj = datetime(doc['_id']['year'], doc['_id']['month'], doc['_id']['day'], doc['_id']['hour'])
            data[doc['_id']['servername']].append((datetime_obj, doc['average_players']))
        
        return data

    def figplot_average_players(data,start_time,end_time):
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        total_players_per_hour = defaultdict(int)
        for servername, values in sorted(data.items()):
            values.sort()  # Ensure the values are sorted by datetime
            datetimes, avg_players = zip(*values)
            ax.plot(datetimes, avg_players, marker='o', label=servername)
            # Calculate total players per hour
            for dt, players in zip(datetimes, avg_players):
                total_players_per_hour[dt] += players

        ax2 = ax.twinx()
        total_datetimes, total_players = zip(*sorted(total_players_per_hour.items()))
        ax2.plot(total_datetimes, total_players, marker='x', color='r', linestyle='--', label='Total Players')
        ax2.set_ylabel('Total Number of Players', color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        ax.set_xlabel(f'Datetime (UTC) from {start_time.strftime("%Y-%m-%d")} to {end_time.strftime("%Y-%m-%d")}')
        ax.set_ylabel('Average Number of Players')
        ax.set_title('Average Number of Players per Server per Hour')
        ax.legend()
        ax.grid(True)
        
        # Set major ticks format to show only hours
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %HH'))
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        return fig
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=last_hours)
    average_players_data = fetch_average_players(start_time,end_time)
    if len(average_players_data)==0:
        await ctx.reply("not enough data for time period.")
        return
    fig = figplot_average_players(average_players_data,start_time,end_time)
    image_buffer = io.BytesIO()
    fig.savefig(image_buffer, format='png', dpi=150)
    image_buffer.seek(0)

    await ctx.reply(
        file=discord.File(
            fp=image_buffer,
            filename=f'players_in_server.png'
        )
    )

def getflex(EXP):
    flex=""
    if EXP>800_000:
        flex=" (TOP 0.1%)"
    elif EXP>200_000:
        flex=" (TOP 1%)"
    elif EXP>100_000:
        flex=" (TOP 10%)"
    elif EXP>50_000:
        flex=" (TOP 50%)"
    return flex