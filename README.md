# 🍉 WaterMelonBot 🍉

watermelon bot for managing discord and servers. written in python

### how to contribute:
- fork this repo
- make edits
- make pull req


### how to run the bot for your server (you must have admin rights):
- go to discord bot dev and create an application, create a bot
- invite bot to your server via url
- clone this repo and
- add the bot token to the "watermelon.config" file.
- in this directory, run `pip3 install -r requirements.txt`
- run `python3 main.py`

### watermelon.config file
- create a txt file "watermelon.config"
- populate it with this:
```json
{
  "prefix": "!",
  "bot_token": "<BOT_TOKEN>",
  "mongo_key": "mongodb+srv://<USER>:<PASS>@<CLUSTER_IP>/<DB_NAME>?retryWrites=true&w=majority&socketTimeoutMS=36000&connectTimeoutMS=36000"
}
```