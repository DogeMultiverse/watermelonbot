# 🍉 WaterMelonBot 🍉

Bot for managing discord and servers, written in python.

- [🍉 WaterMelonBot 🍉](#-watermelonbot-)
  - [How to contribute](#how-to-contribute)
    - [If you wanted to fix or add new features](#if-you-wanted-to-fix-or-add-new-features)
    - [If you found a bug](#if-you-found-a-bug)
  - [How to operate the bot (you must have admin rights)](#how-to-operate-the-bot-you-must-have-admin-rights)
  - [Config file](#config-file)
    - [With config file](#with-config-file)
    - [With .env file](#with-env-file)
  - [TO DO](#to-do)
  


# How to contribute 


## If you wanted to fix or add new features
- Fork this repo.
- Commit your changes on the fork.
- Make a pull request and wait so that a contributor/repo owner merge the pull request.

## If you found a bug
- Make sure the bug is reproducible.
- Make sure the bug is not reported.
- Open an issue, describe the bug.

# How to operate the bot (you must have admin rights)
- Go to [discord developer portal](https://discord.com/developers) and create an application, create a bot.
- Invite your bot to your server via Oauth bot url.
- Clone this repo.
- Duplicate the "watermelon.example.config" file and rename it to "watermelon.config"
- Replace `<BOT_TOKEN>` with your bot token in the "watermelon.config" file.
- install python 3.9.1 (use as interpreter for this bot)
- https://code.visualstudio.com/docs/python/environments (create an env) 
  - see docs
- In this directory, execute `pip3 install -r requirements.txt` on terminal.
- Run `python3 main.py`.

# Config file

## With config file
- Create a txt file "watermelon.config" ( or rename the example config file `watermelon.example.config`)
- Add the following lines to the file:
```json
{
  "prefix": "!",
  "bot_token": "<BOT_TOKEN>",
  "mongo_key": "mongodb+srv://<USER>:<PASS>@<CLUSTER_IP>/<DB_NAME>?retryWrites=true&w=majority&socketTimeoutMS=36000&connectTimeoutMS=36000",
  "GUILD_ID1":"785543836608364556",
  "GUILD_ID2":"729946922810605690"
}
```
# other files

must have these folders: `data/mindustry/mods/common/` and `logs` and `data`

change values of GUILD_ID1 and GUILD_ID2 to the GUILD_ID that you own.

# How to upload maps.

- fork this repo
- upload file to repo
    - make sure file location is correct (survival maps for survival folder)
    - make sure files ends with `.msav`
- make PR to master branch.
- wait ( do not ping alex)

## IMPORTANT: DO NOT DELETE the following: 

- for survival: `mazev4.msav`
- for pvp: `SpaceFortressV1.msav`
- for attack: `Ax_Pvp_map_Oh_no_v3.msav`

deleteing these files should only be done by alex.
- will require a change in `config startCommands`

## notes for uploading maps

- map name should be same as the file name.
- no special characters in map name or file name.
    - `[]_` are allowed.
    - use underscores or camelCase in file name and map name.
