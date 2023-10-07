import discord.ext.commands


def get_user_display_name(ctx: discord.ext.commands.Context, user_id: int):
    member = ctx.message.guild.get_member(user_id)

    if member is None:
        user = ctx.bot.get_user(user_id)

        if user is None:
            return 'Unknown User'

        return user.name
    else:
        return member.display_name
