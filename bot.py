#!/usr/bin/python3
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime
import asyncio
import pickledb
from discord.utils import get

intents = discord.Intents.default()
intents.members = True

MUTE_PRICE = 2000
TEMPMUTE_PRICE = 200

load_dotenv()

bot = commands.Bot(command_prefix='$', intents=intents)
Users = {}

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    db = pickledb.load('user.db', False)
    for member in bot.users:
        if db.get(str(member.id)):
            Users[member] = [datetime.now(), int(float(db.get(str(member.id))))]
    db.dump()

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:  
        if member in Users:
            Users[member][0] = datetime.now()
        else:
            Users[member] = [datetime.now(),0]
    if before.channel is not None and after.channel is None:
        Users[member][1] += int(((datetime.now() - Users[member][0]).total_seconds()) / 60)
        db = pickledb.load('user.db', False)
        db.set(str(member.id), str(Users[member][1]))
        b=db.get(str(member.id))
        db.dump()

@commands.command(pass_context=True)
async def balance(ctx):
    if ctx.author.voice is not None:
        if ctx.author.voice.channel is not None:
            Users[ctx.author][1] += int(((datetime.now() - Users[ctx.author][0]).total_seconds()) / 60)
            Users[ctx.author][0] = datetime.now()
    await ctx.send(f'Vous avez {Users[ctx.author][1]} or')

@commands.command(pass_context=True)
async def mute(ctx, member: discord.Member=None):
    if Users[ctx.author][1] < MUTE_PRICE:
        await ctx.send('Vous n\'avez pas assez d\'or')
    else:
        Users[ctx.author][1] = Users[ctx.author][1] - MUTE_PRICE
        await member.edit(mute=True)

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Je n\'ai pas trouvé cet utilisateur')

@commands.command(pass_context=True)
async def tempmute(ctx, duration:int, member: discord.Member=None):
    if Users[ctx.author][1] < TEMPMUTE_PRICE:
        await ctx.send('Vous n\'avez pas assez d\'or')
    elif duration > 600:
        await ctx.send('Vous ne pouvez pas mute plus de 10 minutes')
    else:
        Users[ctx.author][1] = Users[ctx.author][1] - TEMPMUTE_PRICE
        await member.edit(mute=True)
        await asyncio.sleep(duration)
        await member.edit(mute=False)

@mute.error
async def tempmute_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Je n\'ai pas trouvé cet utilisateur')

bot.add_command(mute)
bot.add_command(tempmute)
bot.add_command(balance)
bot.run(os.getenv('TOKEN'))