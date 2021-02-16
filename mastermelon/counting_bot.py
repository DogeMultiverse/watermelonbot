# this bots just reads a file and see if the count is valid, if it is, append to the file. if fails, reset the file

import json
from mastermelon import emojis as ej


def read_data():
    try:
        with open("data/counting_bot.config", "rb") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(str(e))
        with open("data/counting_bot.config", "w") as f:
            data = {"highscore": 0, "highscore_players": [], "highscore_griefer": 804602034036539442,
                    "current_count": 0, "current_players": []}
            json.dump(data, f)
        return {"highscore": 0, "highscore_players": [], "highscore_griefer": 804602034036539442, "current_count": 0,
                "current_players": []}


def start_counter_bot(channel):
    data = read_data()
    current_count = data["current_count"]
    channel.send(f"bot has restarted, last count is:{current_count}. Please continue from there.")


def save_data_inc_count(current_count, id, data):
    data["current_count"] = current_count
    data["current_players"].append(id)
    with open("data/counting_bot.config", "w") as f:
        json.dump(data, f)


def save_data_reset_count(data):
    data["current_count"] = 0
    data["current_players"] = []
    with open("data/counting_bot.config", "w") as f:
        json.dump(data, f)


async def run_counterbot(message, self):
    data = read_data()
    current_count = data["current_count"]
    try:
        if int(message.content) == (current_count + 1):
            save_data_inc_count(int(message.content), message.author.id, data)
            return
    except Exception as e:
        # print(str(e))
        pass
    await message.channel.send(f"FAILED! {message.author.mention} CAN'T COUNT {ej.kekw_emoji}!!")
    if current_count > data["highscore"]:
        data["highscore"] = current_count
        data["highscore_players"] = data["current_players"]
        data["highscore_griefer"] = message.author.id
        data["current_count"] = 0
        data["current_players"] = []
        save_data_reset_count(data)
        await message.channel.send(f"New highscore!")
        topic = "EXTREME Hardcore counting (10sec cd). If any subsequent count is wrong, the bot RESTARTS the count. " \
                "Lets see what is the highest score we can get. "
        playersstr = ""
        for playerid in set(data["highscore_players"]):
            player = self.get_user(playerid)
            if player is not None:
                playersstr += player.name + "#" + player.discriminator + ", "
        if len(playersstr) > 0:
            playersstr = playersstr[:-2]
            await message.channel.edit(topic=topic + f"Highscore: {current_count}. By " + playersstr)
    else:
        highscore = data["highscore"]
        contribution = len(set(data["highscore_players"]))
        add_s = "s" if contribution > 1 else ""
        save_data_reset_count(data)
        await message.channel.send(
            f"Previous highscore was: {highscore}. With contribution from {contribution} player{add_s}.")

    await message.channel.send("Current count is 0. Please continue...")
