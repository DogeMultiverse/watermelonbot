import json

with open("watermelon.config", "rb") as f:
    js = json.load(f)
    prefix: str = js["prefix"]
    GUILD_ID1:int = int(js["GUILD_ID1"])
    GUILD_ID2:int = int(js["GUILD_ID2"])
GUILD_IDS = [GUILD_ID1,GUILD_ID2 ]


def is_valid_guild_check(guild_id):
    return guild_id in GUILD_IDS


def is_valid_guild(ctx):
    return is_valid_guild_check(ctx.guild.id)
