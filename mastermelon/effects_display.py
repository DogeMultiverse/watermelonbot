import asyncio
import discord
from discord import ext
from mastermelon import emojis as ej
import pymongo

effect_links = {
    "yellowSpark": "https://media.discordapp.net/attachments/788044465834950666/806246035798229052/screen-capture_3.gif",
    "pixel": "https://media.discordapp.net/attachments/788044465834950666/806244776655061022/screen-capture_1_1.gif",
    "rainbowBubble": "https://media.discordapp.net/attachments/788044465834950666/806244581963595836/screen-capture_1.gif",
    "greenCircle": "https://media.discordapp.net/attachments/788044465834950666/806244393173778522/screen-capture.gif",
    "whiteDoor": "https://media.discordapp.net/attachments/788044465834950666/806229661620371566/screen-capture.gif",
    "rainbowPixel": "https://media.discordapp.net/attachments/788044465834950666/806228968558690344/screen-capture.gif",
    "yellowLargeDiam": "https://media.discordapp.net/attachments/788044465834950666/806227969760690186/screen-capture_2.gif",
    "whiteLancerRandom": "https://media.discordapp.net/attachments/788044465834950666/806227110419103834/screen-capture_1.gif",
    "whiteLancerRadius": "https://media.discordapp.net/attachments/785543837116399636/806198412764119120/ezgif-1-402e389e3e14.gif"}


async def showeffectsmenu(ctx: ext.commands.Context, effects_cost: dict, owned_effects: list, effects: list,
                          balance: int, ax: pymongo.collection, ingamecosmetics: pymongo.collection):
    emojis_used = []
    emoji_i = 0
    strbuilder = ""
    for cost, effectname in effects_cost.items():
        t_str = []
        for eff in effectname:
            if eff + "Effect" in owned_effects:
                emoji_to_add = " ✅`"
            else:
                emoji_to_add = "`" + ej.letter_emoji[emoji_i]
                emojis_used.append([ej.letter_emoji[emoji_i], eff])
                emoji_i += 1
            t_str.append(f"`{eff}" + emoji_to_add)
        strbuilder += f"`{cost:>3} `" + ej.ax_emoji + "  " + ", ".join(t_str) + "\n"
    content = f"(Current balance: `{balance}` {ej.ax_emoji})"
    desc = f"`  Price   Effects`  {content}\n" + strbuilder + \
           "\nNote: `✅`=owned. Purchased effects are non-refundable. " \
           "\nIf color is not specified in the effect, it is *configurable* via `/color` in game."
    embed = discord.Embed.from_dict({"title": f"Alex Mindustry *special* `Effects MENU`",
                                     "description": desc + "\n🔽Click on the emoji below to view more.🔽",
                                     "color": discord.Colour.dark_grey().value})
    closed_embed = discord.Embed.from_dict({"title": f"Alex Mindustry *special* `Effects MENU`", "description": desc,
                                            "color": discord.Colour.dark_grey().value})

    if len(emojis_used) == 0:
        await ctx.channel.send(embed=closed_embed)
        await ctx.channel.send(ej.rainbow_banner_gif)
        react = await ctx.channel.send(f"{ej.blob_emoji} You have all the effects! {ej.blob_emoji}")
        await react.add_reaction(ej.blob_emoji)
        return
    else:
        msg = await ctx.channel.send(embed=embed)
    for emoj in emojis_used:
        await msg.add_reaction(emoj[0])
    await ctx.channel.send(ej.rainbow_banner_gif)

    def check(reaction1, user1):
        return user1 == ctx.message.author and str(reaction1.emoji) in [e[0] for e in emojis_used]

    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.channel.send("You took too long. Closing menu...", delete_after=5)
    else:
        for emoj in emojis_used:
            if emoj[0] == str(reaction.emoji):
                if emoj[1] in effect_links:
                    cost = [c for c, e in effects_cost.items() if emoj[1] in e][0]
                    animation_embed = discord.Embed(
                        title=f"Effect name: `{emoj[1]}`, Cost: {cost} {ej.ax_emoji}").set_image(
                        url=effect_links[emoj[1]])
                    animation_embed.add_field(name="Options:", value=f"{'✅'}=>BUY, {'❌'}=>CANCEL")
                    msg2 = await ctx.channel.send(embed=animation_embed)
                    await msg2.add_reaction("✅")
                    await msg2.add_reaction('❌')
                    try:
                        def check2(reaction1: discord.Reaction, user1):
                            return user1 == ctx.message.author and (str(reaction1.emoji) in ['✅', '❌']) \
                                   and reaction1.message == msg2

                        reaction2, user2 = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check2)
                    except asyncio.TimeoutError:
                        await ctx.channel.send("You took too long. Closing menu(2)...", delete_after=5)
                    else:
                        if str(reaction2.emoji) == '✅':
                            # attempt the purchase here
                            await makepurchase(ctx, effects_cost, owned_effects, effects, emoj[1], ax, ingamecosmetics)
                        else:
                            await ctx.channel.send("Transaction cancelled. See you again...", delete_after=5)
                    for emoji_remove in ['✅', '❌']:
                        await msg2.remove_reaction(emoji_remove, ctx.bot.user)
                else:
                    react_msg = await ctx.channel.send(
                        f"No preview for this effect yet. Please go to HUB to view it.\nTo "
                        f"purchase, type `{ctx.bot.command_prefix}buyeffect {emoj[1]}`.")
                    await ej.sleep_add_reaction(react_msg, 5, ej.feelsbm_emoji)

    for emoj in emojis_used:
        await msg.remove_reaction(emoj[0], ctx.bot.user)
    await msg.edit(embed=closed_embed)


async def makepurchase(ctx: discord.ext.commands.Context, effects_cost: dict, owned_effects, effects, peffect, ax,
                       ingamecosmetics):
    await ctx.channel.send("Buying effects are not available for now. Coming soon! Meanwhile you can enjoy the free pixel effect in Mindustry!")
    if True:
        return
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
                await ej.sleep_add_reaction(react, 5)
            else:
                desc = f"You **dont** have enough {ej.ax_emoji} to make the purchase. Balance: " \
                       f"{balance} {ej.ax_emoji}.\nPlay more for **EXP** or " \
                       f"collect <#786110451549208586>. "
                embed = discord.Embed.from_dict(
                    {"description": desc, "color": discord.Colour.dark_red().value})
                react = await ctx.channel.send(embed=embed)
                await ej.sleep_add_reaction(react, 5, emoji=ej.feelsbm_emoji)
        elif peffect in effects:
            desc = f"You already **have** this effect.\nType `/effect {peffect}` in **Alex Mindustry** to use it."
            embed = discord.Embed.from_dict(
                {"description": desc, "color": discord.Colour.dark_red().value})
            react = await ctx.channel.send(embed=embed)
            await ej.sleep_add_reaction(react, 5)
        else:
            await ctx.channel.send("Effect not known. Spell properly and effects *are* cAsE sEnSiTiVe.")
    except Exception as e:
        print(str(e))
        await ctx.channel.send("Please re-join Alex mindustry."
                               "\nIf you get this error again, pls **PING** alex! error 189:" + str(e))
