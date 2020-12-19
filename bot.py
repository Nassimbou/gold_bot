#!/usr/bin/python3
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime

MUTE_PRICE = 2000

load_dotenv()

bot = commands.Bot(command_prefix='$')
Users = {}

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if member in Users:
            Users[member][0] = datetime.now()
            print(f'{member.name} joined at {Users[member][0]}')
        else:
            Users[member] = [datetime.now(),0]
            print(f'{member.name} joined at {Users[member][0]}')

    if before.channel is not None and after.channel is None:
        Users[member][1] += (datetime.now() - Users[member][0]).total_seconds() 

@commands.command(pass_context=True)
async def balance(ctx):
    await ctx.send(f'Vous avez {Users[ctx.author][1]} or')

@commands.command(pass_context=True)
async def mute(ctx, member: discord.Member=None):
    if Users[member][1] < MUTE_PRICE:
        await ctx.send('Vous n\'avez pas assez d\'or')
    else:
        Users[member][1] = Users[member][1] - MUTE_PRICE
        await member.edit(mute=True)

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Je n\'ai pas trouvé cet utilisateur')

bot.add_command(mute)
bot.add_command(balance)
bot.run(os.getenv('TOKEN'))