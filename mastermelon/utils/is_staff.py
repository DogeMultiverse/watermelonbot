import json

import discord

staff_roles_id = [
    1146391538008608798,  # Head Admin
    785543836608364563,  # co-owner
    785543836608364561,  # Admin (discord)
    787870801272635413,  # Admin (mindustry)
    1164875471968796803,  # Admin (Idle-verse)
    809646563349495848,  # Admin (Minecraft)
    785543836608364560,  # Mod (Discord)
    874641386090156113,  # Mod (Telegram)
    787871315037913128,  # Mod (Mindustry)
    809646770119770142,  # Mod (Minecraft)
    875011894749065227,  # Mod (Reddit)
    943890014557831178,  # Mod (Giveaway)
    787871934700322827,  # Dev (Discord)
    787872222525652992,  # Dev (Mindustry)
    809648519383613490,  # Dev (Minecraft)
    809647190183378965,  # Dev (terraria)
    875742346124361788,  # Dev (Website)
    814823848138113024,  # Junior Mod (Minecraft)
    786113343629819944,  # Dev LEAD
    1190906909583220846,  # Junior Moderator
    789413487427977238,  # Junior Developer
]


def is_staff(member: discord.Member):
    for role in member.roles:
        if role.id in staff_roles_id:
            return True

    return False
