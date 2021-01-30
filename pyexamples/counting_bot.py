# this bots just reads a file and see if the count is valid, if it is, append to the file. if fails, reset the file

import json


def run_counterbot(message):
    with open("../data/counting_bot.config", "rb") as f:
        data = json.load(f)
    print(data)
