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

# Fixation des prix
MUTE_PRICE = 2000
TEMPMUTE_PRICE = 200

load_dotenv()

bot = commands.Bot(command_prefix='$', intents=intents)
# Un utilisateur est constitué de sont id en key et de [time actuel, argent] en value
Users = {}

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    db = pickledb.load('user.db', False)
    # Tout les membres du serveur sont ajoutés à la liste
    for member in bot.users:
        # Si ils existent déjà dans la bdd, ont reprend leur valeur
        if db.get(str(member.id)):
            Users[member] = [datetime.now(), int(float(db.get(str(member.id))))]
        # Sinon on les crée
        else:
            Users[member] = [datetime.now(), 0]
    db.dump()

@bot.event
async def on_voice_state_update(member, before, after):
    # Si le membre entre dans un channel depuis un non channel
    if before.channel is None and after.channel is not None:  
        # Si il existe, il prend juste la valeur du temps actuelle
        if member in Users:
            Users[member][0] = datetime.now()
        # Sinon on le crée
        else:
            Users[member] = [datetime.now(),0]
    # Si l'utilisateur quitte un channel vocal, on met à jour et on enregistre sa value d'or dans la bdd
    if before.channel is not None and after.channel is None:
        Users[member][1] += int(((datetime.now() - Users[member][0]).total_seconds()) / 60)
        db = pickledb.load('user.db', False)
        db.set(str(member.id), str(Users[member][1]))
        db.dump()

@commands.command(pass_context=True)
async def balance(ctx):
    # Si l'utilisateur est dans un channel vocal
    if ctx.author.voice is not None:
        # Et si il es bien dans un channel vocal (sinon la value est null)
        if ctx.author.voice.channel is not None:
            # On met à jour la value dans le contexte
            Users[ctx.author][1] += int(((datetime.now() - Users[ctx.author][0]).total_seconds()) / 60)
            Users[ctx.author][0] = datetime.now()
            db = pickledb.load('user.db', False)
            db.set(str(ctx.author.id), str(Users[ctx.author][1]))
            db.dump()
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