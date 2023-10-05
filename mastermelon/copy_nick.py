import discord
from discord.ext import commands

import pymongo
import json

import re
import random

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
                      help="<user:target_user> <char:character_to_replace_with_number:x> <boolean:should_rename:false, "
                           "if this is false this will just create the db but will not actually rename user in discord>"
                           "<boolean:should_rename_target_user:false> <boolean:should_rename_bot:false>")
    @commands.has_any_role("Admin (Discord)")
    @commands.check(is_valid_guild)
    async def copy_nick(self, ctx: commands.Context, target_user: discord.Member,
                        character_to_replace_with_number: str = "x", should_rename: bool = False,
                        should_rename_target_user: bool = False,
                        should_rename_bot: bool = False):
        copy_nick_config = config_collection.find_one({"_id": "copy-nick"})

        if copy_nick_config is not None:
            await ctx.reply('Previous copy nick already exist. Reset before using it again.')

            return

        config_collection.insert_one({"_id": "copy-nick", "targetUserId": target_user.id})

        for member in ctx.guild.members:
            copy_nick_rollback_collection.insert_one({"nickname": member.nick, "_id": member.id})

            if should_rename:
                if should_rename_target_user and member.id == target_user.id:
                    continue

                new_nick = re.sub(character_to_replace_with_number, lambda match: str(random.randint(0, 9)),
                                  target_user.display_name)

                try:
                    await member.edit(nick=new_nick)
                except discord.errors.Forbidden:
                    await ctx.reply("Can't rename " + member.name + " no permission")

        await ctx.reply('Nick copied')

    @commands.command(description="Reset previous copy nick", brief="Admin Utility")
    @commands.has_any_role("Admin (Discord)")
    @commands.check(is_valid_guild)
    async def copy_nick_reset(self, ctx: commands.Context):
        copy_nick_config = config_collection.find_one({"_id": "copy-nick"})

        if copy_nick_config is None:
            await ctx.reply('Copy nick does not exist. Create before using it again.')

            return

        for member in copy_nick_rollback_collection.find():
            member_nickname = member["nickname"]
            member_id = member["_id"]

            member = ctx.guild.get_member(member_id)

            try:
                await member.edit(nick=member_nickname if member_nickname is not None else '')
            except discord.errors.Forbidden:
                await ctx.reply("Can't rename " + member.name + " no permission")

        config_collection.delete_one({"_id": "copy-nick"})
        copy_nick_rollback_collection.delete_many({})

        await ctx.reply('Nick reset')
