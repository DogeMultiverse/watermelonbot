import asyncio


async def run_highlowgame(ctx):
    await ctx.message.channel.send("test msg2")
    author = ctx.message.author.id
    await ctx.channel.send(ctx.author.name)
