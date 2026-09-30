import json
import os
import discord
from discord.ext import commands

CONFIG_PATH = "config.json"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


if not os.path.exists(CONFIG_PATH):
    save_config({
        "enabled": True,
        "priority_user_id": 0,
        "blocked_user_ids": []
    })

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


def priority_is_in_voice(guild, priority_id):
    member = guild.get_member(priority_id)
    if member and member.voice and member.voice.channel:
        return member.voice.channel
    return None


@bot.event
async def on_ready():
    print(f"[PriorityVoice] Online come {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_voice_state_update(member, before, after):
    cfg = load_config()
    if not cfg.get("enabled", True):
        return

    priority_id = int(cfg.get("priority_user_id", 0))
    blocked_ids = [int(x) for x in cfg.get("blocked_user_ids", [])]
    guild = member.guild

    if member.id == priority_id and after.channel is not None:
        channel = after.channel
        for uid in blocked_ids:
            blocked = guild.get_member(uid)
            if blocked and blocked.voice and blocked.voice.channel == channel:
                try:
                    await blocked.move_to(None)
                    print(f"[PriorityVoice] {blocked} disconnesso — priorita' entrata.")
                except discord.Forbidden:
                    print(f"[PriorityVoice] Permessi insufficienti per {blocked}.")
        return

    if member.id in blocked_ids and after.channel is not None:
        priority_channel = priority_is_in_voice(guild, priority_id)
        if priority_channel and after.channel == priority_channel:
            try:
                await member.move_to(None)
                print(f"[PriorityVoice] {member} espulso — priorita' presente.")
            except discord.Forbidden:
                print(f"[PriorityVoice] Permessi insufficienti per {member}.")
        return


def run_bot():
    token = os.environ["DISCORD_TOKEN"]
    bot.run(token)
