import discord
import random
import asyncio
import json


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('$guess'):
            await message.channel.send('Guess a number between 1 and 1000000. its one in a million')

            def is_correct(m):
                print(message.author.id, message.author)
                print(type(message.author.id))
                if message.author.id in [500744743660158987, 612861256189083669]:
                    return random.randint(1, 10) > 3
                return m.author == message.author and m.content.isdigit()

            answer = random.randint(1, 1000000)

            try:
                guess = await self.wait_for('message', check=is_correct, timeout=10.0)
            except asyncio.TimeoutError:
                return await message.channel.send('Sorry, you took too long it was {}.'.format(answer))

            if int(guess.content) == answer or (message.author.id in [500744743660158987, 612861256189083669]
                                                and random.randint(1, 10) > 5):
                await message.channel.send('You are right?')
            else:
                await message.channel.send('Oops. It is actually {}.'.format(answer))


def runbot():
    client = MyClient()
    with open("watermelon.config", "rb") as f:
        bot_token = json.load(f)["bot_token"]
    client.run(bot_token)
