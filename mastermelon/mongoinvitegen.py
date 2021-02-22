

# this snippet was used to generate the entries in mongodb

# async def on_ready(self):
#     print('Logged in as', bot.user.name, bot.user.id)
#     for guild in bot.guilds:
#         # Adding each guild's invites to our dict
#         self.invites[guild.id] = await guild.invites()
#         self.inviter_dict[guild.id] = {}
#         invite: discord.guild.Invite
#         for invite in self.invites[guild.id]:
#             await self.update_self_invite_dict(guild, invite)
#         print(json.dumps(self.inviter_dict, indent=4))
#         for guildid, invites in self.inviter_dict.items():
#             if guildid == 785543836608364556:
#                 list_of_dicts = []
#                 for strduuid, vals in invites.items():
#                     print(type(strduuid), strduuid, vals)
#                     list_of_dicts.append(
#                         dict([("duuid", strduuid), ("name", vals["name"]), ("codes", vals["codes"]), ("invited", [])]))
#                 print(list_of_dicts)
#                 discordinvites.insert_many(documents=list_of_dicts)