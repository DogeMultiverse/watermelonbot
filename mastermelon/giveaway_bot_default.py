import asyncio
import discord
from discord.ext import commands


async def run_giveawaybot(ctx, bot):
    # read existing giveaways and then continue their running
    pass


async def start_giveawaybot(ctx, bot):
    # start a new giveaway and save the config then continue their running
    pass


class Greetings(commands.Cog, name="first"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send('Hello {0.name}~'.format(member))
        else:
            await ctx.send('Hello {0.name}... This feels familiar.'.format(member))
        self._last_member = member
