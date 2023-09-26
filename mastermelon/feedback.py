import discord
from mastermelon import melon

# class MyModal(discord.ui.Modal): 
#     def __init__(self, *args, **kwargs) -> None: 
#         super().__init__(*args, **kwargs)

#         self.add_item(discord.ui.InputText(label="Title")) 
#         self.add_item(discord.ui.InputText(label="Message", style=discord.InputTextStyle.long)) 

#     async def callback(self, interaction: discord.Interaction):
#         channel = melon.bot.get_channel(785543837488775218) 
#         embed = discord.Embed(title="FeedBack Results") 
#         embed.add_field(name="Title", value=self.children[0].value) 
#         embed.add_field(name="Message", value=self.children[1].value) 
#         embed.add_field(name="Author", value=interaction.user.name) 
#         await channel.send(embeds=[embed]) 
#         await interaction.response.send_message("A message was sent", delete_after=1.0)
