# 🍉 WaterMelonBot 🍉

watermelon bot for managing discord and servers. written in python

### how to contribute:
- Fork this repo
- Create a Commit
- Make a pull request until a repo owner/contributors merge a pull request


### how to run the bot for your server (you must have admin rights):
- go to [discord developer portal](https://discord.com/developers) and create an application, create a bot
- invite your bot to your server via Oauth bot url
- clone this repo and
- add the bot token to "watermelon.config" file.
- in this directory, execute `pip3 install -r requirements.txt` on terminal
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
