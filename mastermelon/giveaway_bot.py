import asyncio

import discord
import pymongo
from discord.ext import commands
from random import choice
import json
from datetime import datetime, timedelta
from bson import json_util
import pytz
from mastermelon import emojis as ej

feelsbm_emoji = ej.feelsbm_emoji
general_channel_id = 785543837116399636
ga_channel_id = 790529627260321813
pog_emoji = ej.pog_emoji
ax_emoji = ej.ax_emoji
hypertada_emoji = ej.hypertada_emoji

with open("watermelon.config", "rb") as f:
    js = json.load(f)
    mongo_key: str = js["mongo_key"]
    prefix: str = js["prefix"]

if prefix in ["w?", "t?"]:  # only access mongodb for w? and t?
    client = pymongo.MongoClient(mongo_key)
    db = client.get_database("AlexMindustry")
    ax = db["ax"]
    ingamecosmetics = db["ingamecosmetics"]


def form_msg_embed(message, amount, winners, days, seconds, claimed):
    title = hypertada_emoji + f" {amount} {ax_emoji} GIVEAWAY! " + hypertada_emoji
    string = ""
    if days > 0:
        string += f" {days} day" + ("s" if days > 1 else "")
    hours = seconds // 3600
    mins = seconds // 60 - 60 * hours
    secs = seconds % 60
    string += f" {hours} hour" + ("s" if hours > 1 else "")
    if hours < 1:
        string += f" {mins} min" + ("s" if mins > 1 else "")
        string += f" {secs} sec" + ("s" if secs > 1 else "")
    footer = f"ends in{string}, react with any emoji to receive giveaway. ({claimed}/{winners} claimed)"
    embed = discord.Embed.from_dict({"description": message, "title": title,
                                     "color": discord.Colour.gold().value}).set_footer(text=footer)
    return embed


class Giveaway(commands.Cog, name="giveaway"):
    def __init__(self, bot: discord.ext.commands.Bot):  # set up all the existing giveaways
        self.bot = bot
        try:
            with open("data/giveaway_bot.config", "r") as f:
                read = f.read()
                if read == "":
                    self.data = {"running": [], "ended": []}
                else:
                    data = json.loads(read, object_hook=json_util.object_hook)
                    self.data = data
        except FileNotFoundError:
            self.data = {"running": [], "ended": []}
        #self.bot.loop.create_task(self.giveaway_background_task())

    def savedata(self):
        with open("data/giveaway_bot.config", "w") as f:
            json.dump(self.data, f, default=json_util.default, indent=4)

    async def edit_end_msg(self, gaws):
        channel = await self.bot.fetch_channel(gaws["channelid"])
        message: discord.Message = await channel.fetch_message(gaws["messageid"])
        title = feelsbm_emoji + f" {gaws['amount']} {ax_emoji} GIVEAWAY ENDED " + feelsbm_emoji
        await message.edit(
            embed=discord.Embed(title=title, description=gaws["message"]).set_footer(
                text=f";-; come back again... ig... {gaws['claimed']} claimed"))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):  # todo on emoji reaction!
        # print(self.data)
        if payload.member.bot:
            return
        current_time = datetime.now()
        for gaws in self.data["running"]:
            if gaws["messageid"] == payload.message_id:
                if (gaws["enddate"] < current_time) or gaws["winners"] <= len(set(gaws["participants"])):
                    # for parts in set(gaws["participants"]):
                    #    #print("winner", parts)
                    await self.edit_end_msg(gaws)
                    self.data["ended"].append(gaws)
                    self.data["running"].remove(gaws)
                    self.savedata()
        for gaws in self.data["running"]:
            timeleft = gaws["enddate"] - current_time
            if gaws["messageid"] == payload.message_id and payload.user_id not in gaws["participants"]:
                # print("new participant" + payload.member.name)
                gaws["participants"].append(payload.user_id)
                channel: discord.TextChannel = await self.bot.fetch_channel(gaws["channelanncid"])
                channelga: discord.TextChannel = await self.bot.fetch_channel(gaws["channelid"])
                if ax.find_one({"duuid": payload.user_id}) is None:
                    ax.insert_one({"duuid": payload.user_id, "ax": gaws["amount"]})
                else:
                    ax.find_one_and_update({"duuid": payload.user_id}, {"$inc": {"ax": gaws["amount"]}})
                await channel.send(content=f"{payload.member.name}#{payload.member.discriminator} just claimed a "
                                           f"Giveaway in {channelga.mention} {pog_emoji}")
                embed = form_msg_embed(gaws["message"], gaws["amount"], gaws["winners"], timeleft.days,
                                       timeleft.seconds, len(set(gaws["participants"])))
                message: discord.Message = await channelga.fetch_message(gaws["messageid"])
                await message.edit(embed=embed)
                self.savedata()

    def addGiveawayEvent(self, messageid: int, channel: discord.TextChannel, channelannc: discord.TextChannel,
                         msg: str, amount: int, winners: int, days: int, hours: int):
        enddate = datetime.now() + timedelta(days=days, hours=hours)
        gaws = {"winners": winners, "amount": amount, "messageid": messageid, "channelid": channel.id,
                "channelanncid": channelannc.id, "message": msg, "enddate": enddate, "participants": []}
        self.data["running"].append(gaws)
        self.savedata()

    async def removeGiveawayEvent(self, ctx: discord.ext.commands.Context, messageid: int):
        for gaws in self.data["running"]:
            if gaws["messageid"] == messageid:
                self.data["running"].remove(gaws)
                await ctx.channel.send("Removing active giveaway event.. Self destructing", delete_after=15)
                await self.edit_end_msg(gaws)
        self.savedata()

    async def showallgevents(self, ctx: discord.ext.commands.Context):
        st = [f"{gaws['messageid']}: timeleft{gaws['enddate'] - datetime.now()}"
              for gaws in self.data["running"]]
        await ctx.channel.send(", ".join(st), delete_after=15)

    async def giveaway_background_task(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(20)
        while not self.bot.is_closed():
            await asyncio.sleep(180)
            current_time = datetime.now()
            for gaws in self.data["running"]:  # update the time in the footer, if ended, edit end msg
                if (gaws["enddate"] < current_time) or gaws["winners"] <= len(set(gaws["participants"])):
                    await self.edit_end_msg(gaws)
                    self.data["ended"].append(gaws)
                    self.data["running"].remove(gaws)
                    self.savedata()
                else:  # update the time
                    timeleft = gaws["enddate"] - current_time
                    channelga: discord.TextChannel = await self.bot.fetch_channel(gaws["channelid"])
                    message: discord.Message = await channelga.fetch_message(gaws["messageid"])
                    embed = form_msg_embed(gaws["message"], gaws["amount"], gaws["winners"], timeleft.days,
                                           timeleft.seconds, len(set(gaws["participants"])))
                    await message.edit(embed=embed)

        # management = discord.utils.get(self.bot.get_all_channels(), name='bot-staff-only')
        # if ctx.message.channel != management:
        #    return
        # contestants = ctx.message.guild.members
        # winner = choice(contestants).display_name
        # msg = await self.embeder(winner)
        # await ctx.send(embed=msg)
    #
    # async def embeder(self, winner):
    #     # server_url = "https://s3.amazonaws.com/files.enjin.com/1015535/site_logo/2019_logo.png"
    #     em = discord.Embed(
    #         title="**__TCS GIVEAWAY WINNER__**", description="*for the random garbage giveaway...*", color=0x008080)
    #     # em.set_thumbnail(url=server_url)
    #     em.add_field(name="☝🏼**{}** 😩💯💦👌🏼🔥🙏".format(winner),
    #                  value="```Or just run it again because who fucking cares? No one else can see this.```",
    #                  inline=False)
    #     em.set_footer(text="Terms and Conditions Apply")
    #     return em

# def setup(bot):
#    bot.add_cog(Giveaway(bot))
