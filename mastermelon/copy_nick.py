import discord
from discord.ext import commands

import pymongo
import json

from mastermelon.utils.is_valid_guild import is_valid_guild

with open("watermelon.config", "rb") as f:
    js = json.load(f)
    mongo_key: str = js["mongo_key"]
    prefix: str = js["prefix"]

if prefix in ['w?', 't?']:
    client = pymongo.MongoClient(mongo_key)
    db = client.get_database("AlexMindustry")
    copy_nick_rollback_collection = db["copyNickRollback"]
    config_collection = db["config"]


class CopyNick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(description="Copy target user nick to all server members", brief="Admin Utility",
                      help="<user:target_user> <char:character_to_replace_with_number:x> "
                           "<boolean:should_rename_target_user:false> <boolean:should_rename_bot:false>")
    @commands.has_any_role("Admin (Discord)")
    @commands.check(is_valid_guild)
    async def copy_nick(self, ctx: commands.Context, target_user: discord.User,
                        character_to_replace_with_number: str = "x", should_rename_target_user: bool = False,
                        should_rename_bot: bool = False):
        copy_nick_config = config_collection.find_one({"id": "copy-nick"})

        if copy_nick_config is not None:
            await ctx.reply('Previous copy nick already exist. Reset before using it again.')

            return

        config_collection.insert_one({"id": "copy-nick", "targetUserId": target_user.id})

        for member in ctx.guild.members:
            copy_nick_rollback_collection.insert_many([{"nickname": member.nick}])

        await ctx.reply('Nick copied')

    @commands.command(description="Reset previous copy nick", brief="Admin Utility")
    @commands.has_any_role("Admin (Discord)")
    @commands.check(is_valid_guild)
    async def copy_nick_reset(self, ctx: commands.Context):
        copy_nick_config = config_collection.find_one({"id": "copy-nick"})

        if copy_nick_config is None:
            await ctx.reply('Copy nick does not exist. Create before using it again.')

            return

        config_collection.delete_one({"id": "copy-nick"})

        await ctx.reply('Nick reset')
