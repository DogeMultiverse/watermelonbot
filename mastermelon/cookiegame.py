import asyncio
import pymongo
from discord.ext import commands
import discord
from mastermelon import emojis as ej


async def triggercookieclaim(message: discord.Message, ax: pymongo.collection, bot: commands.Bot):
    if len(message.attachments) == 1:
        msg = await message.reply("Thanks for the screenshot. Please wait while we verify the screenshot.",
                                  mention_author=True)
        await msg.add_reaction("🍪")
        await msg.add_reaction("👎")
        try:
            def check2(reaction1: discord.Reaction, user1: discord.Member):
                approved_roles = ["Admin (Discord)", "Mod (Discord)", "Admin (Mindustry)", "Mod (Mindustry)", "Admin (Minecraft)", "Mod (Minecraft)"]
                has_perms = False
                for role in user1.roles:
                    if str(role) in approved_roles:
                        has_perms = True
                return has_perms and (str(reaction1.emoji) in ["🍪", "👎"]) and reaction1.message == msg

            reaction2, user2 = await bot.wait_for('reaction_add', timeout=3600.0 * 24, check=check2)
            duuid = message.author.id
            if str(reaction2.emoji) == "🍪":  # approved
                balance = 0
                if ax.find_one({"duuid": duuid}) is None:
                    ax.insert_one({"duuid": duuid, "ax": 0})
                else:
                    balance = ax.find_one({"duuid": duuid})["ax"]
                ax.find_one_and_replace({"duuid": duuid}, {"duuid": duuid, "ax": balance + 10})
                msg_react = await message.reply(
                    f"Claim approved by {user2.mention}. 10{ej.ax_emoji} awarded to {message.author.mention}."
                    f"\nYou now have {balance + 10} {ej.ax_emoji}.", mention_author=True)
                await msg_react.add_reaction(ej.blob_emoji)
            else:
                await message.reply(f"Claim rejected by {user2.mention}.", mention_author=True)

        except asyncio.TimeoutError:
            await message.reply("Claim not processed, please ping a moderator.", mention_author=True)
    else:
        await message.reply("Please attach 1 screenshot for review.", mention_author=True)
