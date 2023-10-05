import discord
from discord.ext import commands

from mastermelon.utils.is_valid_guild import is_valid_guild


class CopyNick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(description="Copy target user nick to all server members", brief="Admin Utility",
                      help="<user:target_user> <char:character_to_replace_with_number:x> "
                           "<boolean:should_rename_target_user:false> <boolean:should_rename_bot:false>")
    @commands.has_any_role("Admin (Discord)")
    @commands.check(is_valid_guild)
    async def copy_nick(self, ctx: commands.Context, target_user: discord.Member = None,
                        character_to_replace_with_number: str = "x", should_rename_target_user: bool = False,
                        should_rename_bot: bool = False):
        pass
