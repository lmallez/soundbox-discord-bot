import os
from random import randint
from time import sleep

import discord
from discord.ext import commands
from discord.utils import get

BOT_COMMAND_PREFIX = os.environ.get("BOT_COMMAND_PREFIX", "/")
BOT_DESCRIPTION = os.environ.get("BOT_DESCRIPTION", "...")
BOT_SOUNDS_PATH = os.environ.get("BOT_SOUNDS_PATH", "./sounds")
BOT_ERROR_NOT_FOUND = os.environ.get("BOT_ERROR_NOT_FOUND", "Sound '{}' not found")
BOT_ERROR_NOT_CONNECTED = os.environ.get("BOT_ERROR_NOT_CONNECTED", "You must be connected to a vocal channel")
BOT_REACTIONS = os.environ.get("BOT_REACTIONS", "👌").split(",")

client = commands.Bot(command_prefix=BOT_COMMAND_PREFIX, description=BOT_DESCRIPTION)


@client.event
async def on_ready():
    print("Logged in as {} (#{})".format(client.user.name, client.user.id))


def get_sounds():
    return os.listdir(BOT_SOUNDS_PATH)


@client.command(pass_context=True, no_pm=True)
async def sound_dc(ctx):
    vc = get(ctx.bot.voice_clients, guild=ctx.guild)
    if vc:
        await vc.disconnect()


@client.command(pass_context=True, no_pm=True)
async def sound_list(ctx):
    sounds = [s.split(".")[0] for s in get_sounds()]
    await ctx.message.reply("```{}```".format("\n".join(sounds)))


class NotFound(Exception):
    def __init__(self, sound: str):
        self.sound = sound


def sound_selected(sounds: list, args: list):
    audios = ["{}.mp3".format(arg) for arg in args]
    for audio in audios:
        if audio not in sounds:
            raise NotFound(audio)
    return audios


def sound_random(sounds: list):
    return [sounds[randint(0, len(sounds))]]


@client.command(pass_context=True, no_pm=True)
async def sound(ctx):
    if not ctx.message.author.voice:
        await ctx.message.reply(BOT_ERROR_NOT_CONNECTED)
        return
    channel = ctx.message.author.voice.channel
    sounds = get_sounds()
    args = ctx.args[0].message.clean_content.split(" ")[1:]
    if len(args) > 0:
        try:
            audios = sound_selected(sounds, args)
        except NotFound as e:
            await ctx.message.reply(BOT_ERROR_NOT_FOUND.format(e.sound))
            return
    else:
        audios = sound_random(sounds)
    vc = get(ctx.bot.voice_clients, guild=ctx.guild)
    if not vc:
        vc = await channel.connect()
    await ctx.message.add_reaction(
        str(BOT_REACTIONS[randint(0, len(BOT_REACTIONS) - 1)])
    )
    for audio in audios:
        vc.play(discord.FFmpegPCMAudio("sounds/{}".format(audio)))
        while vc.is_playing():
            sleep(0.1)


token = os.environ.get("DISCORD_TOKEN")
client.run(token)
