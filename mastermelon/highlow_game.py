import asyncio
import random
from mastermelon import emojis as ej

async def run_highlowgame(ctx, bot):
    base_msg = await ctx.channel.send(f"Highlow guess number game for {ctx.author.display_name}."
                                      f"\nGuess the correct number between 1-100 inclusive."
                                      f"\nInitial guess is 50. Higher or lower?")
    up_emoji = "⬆"
    down_emoji = "⬇"
    party_emoji = "🥳"
    kekw_emoji = ej.kekw_emoji
    await base_msg.add_reaction(up_emoji)
    await base_msg.add_reaction(down_emoji)

    def check(reaction1, user1):
        # print("someone reacted", str(reaction1.emoji), user1, ctx.message.author)
        return user1 == ctx.message.author and str(reaction1.emoji) in [up_emoji, down_emoji]

    try:
        upperbound = 100
        lowerbound = 1
        currentguess = 50
        ans = random.randint(1, 100)
        print(ans)
        presses = 0
        withinlimits = True
        while (currentguess != ans) or withinlimits or presses < 10:
            reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
            presses += 1
            if reaction.emoji == up_emoji:
                lowerbound = currentguess + 1
                withinlimits = ans >= lowerbound
            elif reaction.emoji == down_emoji:
                upperbound = currentguess - 1
                withinlimits = ans <= upperbound
            currentguess = (lowerbound + upperbound) // 2
            if (not withinlimits) or (currentguess == ans) or (presses > 10):
                break
            await base_msg.edit(content=f"Highlow guess number game for {ctx.author.display_name}.\n"
                                        f"Guess the correct number between {lowerbound}-{upperbound} inclusive.\n"
                                        f"Current guess is {currentguess}. Higher or lower?")
            await base_msg.clear_reactions()
            await base_msg.add_reaction(up_emoji)
            await base_msg.add_reaction(down_emoji)
        if ans == currentguess:
            await base_msg.edit(content=f"Highlow guess number game for {ctx.author.display_name}.\n"
                                        f"You got it, answer was {ans} and you took {presses} guesses.")
            await base_msg.clear_reactions()
            await base_msg.add_reaction(party_emoji)
        else:
            await base_msg.edit(content=f"Highlow guess number game for {ctx.author.display_name}.\n"
                                        f"You failed, answer was {ans} and you took {presses} guesses.")
            await base_msg.clear_reactions()
            await base_msg.add_reaction(kekw_emoji)
    except asyncio.TimeoutError:  # Indent error here, delete one tabulation
        await base_msg.edit(content=f"Highlow guess number game for {ctx.author.display_name}.\n"
                                    f"You took too long to react. Timed out.")
