import asyncio


async def run_highlowgame(message, disclient):
    await message.channel.send("test msg")
    author = message.author.id
