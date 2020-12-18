#!/usr/bin/python3
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@commands.command(pass_context=True)
async def mute(ctx, member: discord.Member=None):
    await member.edit(mute=True)

@mute.error
async def info_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('I could not find that user')

bot.add_command(mute)
bot.run(os.getenv('TOKEN'))