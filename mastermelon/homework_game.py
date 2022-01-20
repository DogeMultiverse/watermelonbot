import asyncio
import random

import discord.message

from mastermelon import emojis as ej
from time import time as t

highscores = []


def generate_find2root():
    x1, x2 = random.randint(-5, 5), random.randint(-5, 5)
    if x1 == x2:
        x2 += 1
    solution = (x1, x2)
    c = random.randint(0, 10)
    if x1 + x2 != 0:
        sign1 = "+" if x1 + x2 <= 0 else ""
        val1 = sign1 + f"{0 - x1 - x2}x "
    else:
        val1 = ""
    sign2 = "+" if x1 * x2 + c >= 0 else ""
    string = f"Find the roots of \n`x² " + val1 + sign2 + f"{x1 * x2 + c} = {c}`\n"
    string += f"Input your answer with a `,` in between.\n"
    return solution, string


def check_find2root():
    sol, string = generate_find2root()
    t0 = t()
    ans = input(string)
    time_taken = t() - t0
    try:
        anss = tuple([int(i) for i in ans.split(",")])
        correct = anss == sol or anss == (sol[1], sol[0])
        vfast = " Thats really fast." if time_taken < 3 else ""
        print(f"Correct, you took {time_taken:.2f}s.{vfast}" if correct else f"Wrong, its {sol}.")
    except ValueError:
        print("Input error. Follow instructions exactly.")


async def run_homeworkgame(ctx, bot):
    sol, string = generate_find2root()
    t0 = t()
    await ctx.channel.send(f"Homework for {ctx.author.display_name}. (BETA)\n"
                           f"{string}\nReward: 0 {ej.ax_emoji}. (practise for now)")
    party_emoji = "🥳"
    kekw_emoji = ej.kekw_emoji

    def check(message: discord.message.Message):
        return message.author == ctx.message.author and ctx.channel == message.channel

    try:
        ans: discord.message.Message = await bot.wait_for('message', timeout=30, check=check)
        time_taken = t() - t0
        anss = tuple([int(i) for i in ans.content.split(",")])
        correct = anss == sol or anss == (sol[1], sol[0])
        vfast = " Thats really fast." if time_taken < 3 else ""
        reply = f"Correct! You took {time_taken:.2f}s.{vfast}" if correct else f"Wrong! Its {sol[0]},{sol[1]}."
        msg = await ctx.channel.send(reply)
        await msg.add_reaction(party_emoji if correct else kekw_emoji)
        if correct:
            highscores.append((time_taken, ctx.author))
        scores = [f"`{rank + 1}`  `{time:.2f}s`  : {name}" for rank, (time, name) in
                  enumerate(sorted(highscores[:5]))]
        await ctx.channel.send("Homework (BETA) `Leaderboard`\n" + "\n".join(scores))
    except ValueError:
        await ctx.channel.send("Input error. Follow instructions exactly.")
    except asyncio.TimeoutError:  # Indent error here, delete one tabulation
        await ctx.channel.send(f"Homework for {ctx.author.display_name}.\n"
                               f"You took too long to answer. Timed out.")
