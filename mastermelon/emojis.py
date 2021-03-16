import asyncio
import discord
ax_emoji = "<:Ax:789661633214676992>"
pog_emoji = "<:pog2:787158994594431008>"
feelsbm_emoji = "<:feelsbadman:789511704777064469>"
hypertada_emoji = "<a:HyperTada:804302792058994699>"
letter_emoji = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵"
rainbow_banner_gif = "https://tenor.com/view/rainbow-bar-rainbow-bar-colorful-line-gif-17716887"
blob_emoji = "<a:blob:806885815044538369>"
kekw_emoji = "<:kekw:786876427311251466>"


async def sleep_add_reaction(msg: discord.Message, duration: int = 5, emoji: str = pog_emoji):
    await asyncio.sleep(duration)
    await msg.add_reaction(emoji)
