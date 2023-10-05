import json

with open("watermelon.config", "rb") as f:
    js = json.load(f)
    prefix: str = js["prefix"]

GUILD_IDS = [785543836608364556, 729946922810605690]


def is_valid_guild_check(guild_id):
    if prefix in ['t?']:
        return True

    return guild_id in GUILD_IDS


def is_valid_guild(ctx):
    return is_valid_guild_check(ctx.guild.id)
