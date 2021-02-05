import discord
from discord.ext import commands
from random import choice
import json
from datetime import datetime, timedelta


class GiveawayInfo:
    def __init__(self, name: str, channel: discord.TextChannel, messageid: int,
                 winners: int = None, enddate: datetime = datetime.now() + timedelta(days=1),
                 ):
        self.name = name
        self.winners = winners
        self.enddate = enddate
        self.channel = channel
        self.messageid = messageid


class Giveaway(commands.Cog, name="test"):
    def __init__(self, bot):  # set up all the existing giveaways
        self.bot = bot
        try:
            with open("data/counting_bot.config", "rb") as f:
                data = json.load(f)
                self.data = data
        except FileNotFoundError:
            self.data = {"running": [], "ended": []}

    @commands.Cog.listener()
    async def on_me(self, ctx):  # todo on emoji reaction!
        management = discord.utils.get(self.bot.get_all_channels(), name='bot-staff-only')
        if ctx.message.channel != management:
            return
        contestants = ctx.message.guild.members
        winner = choice(contestants).display_name
        msg = await self.embeder(winner)
        await ctx.send(embed=msg)
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
