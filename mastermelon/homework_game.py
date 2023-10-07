import asyncio
import random

import discord.message

from mastermelon import emojis as ej
from time import time as t
import json
import pymongo
from mastermelon.utils.get_user_display_name import get_user_display_name

with open("watermelon.config", "rb") as f:
    js = json.load(f)
    mongo_key: str = js["mongo_key"]
    prefix: str = js["prefix"]

if prefix in ["w?", "t?"]:
    client = pymongo.MongoClient(mongo_key)
    db = client.get_database("AlexMindustry")
    homework_high_score_collection = db["homeworkHighScore"]


def d1(value: int):
    return "" if value == 1 else str(value) + "*"


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
    string = f"Find the roots of \n`x² " + \
             val1 + sign2 + f"{x1 * x2 + c} = {c}`\n"
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
        print(
            f"Correct, you took {time_taken:.2f}s.{vfast}" if correct else f"Wrong, its {sol}.")
    except ValueError:
        print("Input error. Follow instructions exactly.")


def generate_findx():
    char = random.choice([x for x in "xyz😃🤢🎉😴🎅🛒🍔🍟🌭🥓"])
    x = random.randint(1, 5)
    a, b = random.randint(1, 20 // x), random.randint(2, 6)
    string = f"What is the value of '{char}' in the following statement?\n"
    string += random.choice([f"{d1(a)}{char} + {b} = {a * x + b}",
                             f"{b} + {d1(a)}{char} = {a * x + b}",
                             f"{a * x + b} = {d1(a)}{char} + {b}",
                             f"{a * x + b} = {b} + {d1(a)}{char}"])
    return x, string


async def run_homeworkgame(ctx, bot):
    sol, string = generate_findx()
    t0 = t()
    await ctx.channel.send(f"Homework for {ctx.author.display_name}. (BETA 2.0)\n"
                           f"{string}\nReward: 0 {ej.ax_emoji}. (practise for now)")
    party_emoji = "🥳"
    kekw_emoji = ej.kekw_emoji

    def check(message: discord.message.Message):
        return message.author == ctx.message.author and ctx.channel == message.channel

    try:
        ans: discord.message.Message = await bot.wait_for('message', timeout=120, check=check)
        time_taken = t() - t0
        correct = int(ans.content) == int(sol)
        vfast = " Thats really fast." if time_taken < 3 else ""
        reply = f"Correct! You took {time_taken:.2f}s.{vfast}" if correct else f"Wrong! Its {sol}."
        msg = await ctx.channel.send(reply)
        await msg.add_reaction(party_emoji if correct else kekw_emoji)
        if correct:
            player_id = ctx.author.id
            player_in_high_score = homework_high_score_collection.find_one({"_id": player_id})

            if player_in_high_score is None:
                homework_high_score_collection.insert_one(
                    {"_id": player_id, "score": time_taken})
            else:
                current_score = player_in_high_score['score']

                if current_score > time_taken:
                    homework_high_score_collection.update_one(
                        {"_id": player_id}, {"$set": {"score": time_taken}})

        high_scores = homework_high_score_collection.find().sort("score").limit(5)

        scores = [
            f"`{i + 1}`  `{high_score['score']:.2f}s`  : {get_user_display_name(ctx, high_score['_id'])}"
            for
            i, high_score
            in
            enumerate(high_scores)]

        await ctx.channel.send("Homework (BETA 2.0) `Leaderboard`\n" + "\n".join(scores))
    except ValueError:
        await ctx.channel.send("Input error. Follow instructions exactly.")
    except asyncio.TimeoutError:  # Indent error here, delete one tabulation
        await ctx.channel.send(f"Homework for {ctx.author.display_name}.\n"
                               f"You took too long to answer. Timed out.")
