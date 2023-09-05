# 🍉 WaterMelonBot 🍉

Bot for managing discord and servers, written in python.

- [🍉 WaterMelonBot 🍉](#-watermelonbot-)
  - [How to contribute](#how-to-contribute)
    - [If you wanted to fix/add new features](#if-you-wanted-to-fix,add-new-features)
    - [If you found a bug](#if-you-found-a-bug)
  - [How to operate the bot (you must have admin rights)](#how-to-operate-the-bot (you-must-have-admin-rights))
  - [Config file](#config-file)
    - [With config file](#with-config-file)
    - [With .env file](#with-env-file)
  - [TO DO](#to-do)
  


# How to contribute

## If you wanted to fix,add new features
- Fork this repo.
- Commits on the fork.
- Make a pull request and wait so that a contributor/repo owner merge the pull request.

## If you found a bug
- Make sure the bug is reproducible.
- Make sure the bug is not reported.
- Open an issue, describe the bug.

# How to operate the bot (you must have admin rights)
- Go to [discord developer portal](https://discord.com/developers) and create an application, create a bot.
- Invite your bot to your server via Oauth bot url.
- Clone this repo.
- Add the bot token to "watermelon.config" file.
- In this directory, execute `pip3 install -r requirements.txt` on terminal.
- Run `python3 main.py`.

# Config file

## With config file
- Create a txt file "watermelon.config"
- Add the following lines to the file:
```json
{
  "prefix": "!",
  "bot_token": "<BOT_TOKEN>",
  "mongo_key": "mongodb+srv://<USER>:<PASS>@<CLUSTER_IP>/<DB_NAME>?retryWrites=true&w=majority&socketTimeoutMS=36000&connectTimeoutMS=36000"
}
```
or

## With .env file
```.env
bot_token=BOT_TOKEN
mongo_key=mongodb+srv://<USER>:<PASS>@<CLUSTER_IP>/<DB_NAME>?retryWrites=true&w=majority&socketTimeoutMS=36000&connectTimeoutMS=36000
```

# To Do
Coming soon
