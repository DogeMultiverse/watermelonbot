import asyncio
import discord
from discord import ext
from mastermelon import emojis as ej


async def showeffects(ctx: ext.commands.Context):
    await ctx.channel.send("Fetching effects...", delete_after=2)
    effects_cost = {20: ["yellowDiamond", "yellowSquare", "yellowCircle"],
                    30: ["greenCircle", "whiteDoor", "yellowLargeDiam", "yellowSpark"],
                    50: ["whiteLancerRandom"], 80: ["whiteLancerRadius", "pixel", "bubble"],
                    200: ["rainbowPixel", "rainbowBubble"]}
    effects = [ee for c, e in effects_cost.items() for ee in e]
    owned_effects_collection = ingamecosmetics.find_one({"duuid": ctx.author.id})
    if owned_effects_collection is None:
        await ctx.channel.send("error, pls **PING** alex! error 170")
        return
    owned_effects = owned_effects_collection["effects"]
    duuid = ctx.author.id
    if ax.find_one({"duuid": duuid}) is None:
        balance = 0
        ax.insert_one({"duuid": duuid, "ax": 0})
    else:
        balance = ax.find_one({"duuid": duuid})["ax"]
    if isinstance(peffect, type(None)):
        strbuilder = ""
        for cost, effectname in effects_cost.items():
            strbuilder += f"`{cost:>3} `" + ej.ax_emoji + "`  " + \
                          "`, `".join([eff + ("✅" if eff + "Effect" in owned_effects else "")
                                       for eff in effectname]) + "`\n"
        content = f"(Current balance: `{balance}` {ej.ax_emoji})"
        desc = f"`  Price   Effects`  {content}\n" + strbuilder + \
               "\nType `" + prefix + "buyeffect XXXX` to buy the effect. (cAsE sEnSiTiVe)" + \
               "\nNote: `✅`=owned. Purchased effects are non-refundable. " \
               "\nIf color is not specified in the effect, it is *configurable* via `/color` in game."
        embed = discord.Embed.from_dict({"title": f"Alex Mindustry *special* `Effects MENU`", "description": desc,
                                         "color": discord.Colour.dark_grey().value})
        await ctx.channel.send(embed=embed)
        await ctx.channel.send(banner_gif)
    else:
        await ctx.channel.send("Validating purchase...", delete_after=2)
        try:
            if (peffect in effects) and not (peffect + "Effect" in owned_effects):
                peffectcost = [c for c, e in effects_cost.items() if peffect in e][0]
                duuid = ctx.author.id
                balance = ax.find_one({"duuid": duuid})["ax"]
                if balance >= peffectcost:
                    ax.find_one_and_replace({"duuid": duuid},
                                            {"duuid": duuid, "ax": balance - peffectcost})
                    ingamecosmetics.find_one_and_update({"duuid": duuid},
                                                        {"$push": {"effects": peffect + "Effect"}})
                    desc = f"Purchase successful. Congrats! Now you can flex `{peffect}`" \
                           f"\nYou have {balance - peffectcost} {ej.ax_emoji} now." \
                           f"\nType `/effect {peffect}` in **Alex Mindustry** to use it."
                    embed = discord.Embed.from_dict(
                        {"description": desc, "color": discord.Colour.green().value})
                    react = await ctx.channel.send(embed=embed)
                    await sleep_add_reaction(react, 5)
                else:
                    desc = f"You **dont** have enough {ej.ax_emoji} to make the purchase. Balance: " \
                           f"{balance} {ej.ax_emoji}.\nPlay more for **EXP** or " \
                           f"collect <#786110451549208586>. "
                    embed = discord.Embed.from_dict(
                        {"description": desc, "color": discord.Colour.dark_red().value})
                    react = await ctx.channel.send(embed=embed)
                    await sleep_add_reaction(react, 5, emoji=ej.feelsbm_emoji)
            elif peffect in effects:
                desc = f"You already **have** this effect.\nType `/effect {peffect}` in **Alex Mindustry** to use it."
                embed = discord.Embed.from_dict(
                    {"description": desc, "color": discord.Colour.dark_red().value})
                react = await ctx.channel.send(embed=embed)
                await sleep_add_reaction(react, 5)
            else:
                await ctx.channel.send("Effect not known. Spell properly and effects *are* cAsE sEnSiTiVe.")
        except Exception as e:
            print(str(e))
            await ctx.channel.send("Please re-join Alex mindustry."
                                   "\nIf you get this error again, pls **PING** alex! error 189:" + str(e))
    return None
