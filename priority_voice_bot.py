import os
import discord
from discord.ext import commands

TOKEN = os.environ["DISCORD_TOKEN"]
PRIORITY_USER_ID = 695466927568715796            # tu

BLOCKED_USER_IDS = [
    1534059631956070540,   # primo utente bloccato
    1251774468699979857,   # secondo utente bloccato
]

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


def priority_is_in_voice(guild):
    member = guild.get_member(PRIORITY_USER_ID)
    if member and member.voice and member.voice.channel:
        return member.voice.channel
    return None


@bot.event
async def on_ready():
    print(f"[PriorityVoice] Online come {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild

    # Caso 1: entri tu (utente prioritario)
    if member.id == PRIORITY_USER_ID and after.channel is not None:
        channel = after.channel
        for uid in BLOCKED_USER_IDS:
            blocked = guild.get_member(uid)
            if blocked and blocked.voice and blocked.voice.channel == channel:
                try:
                    await blocked.move_to(None)
                    print(f"[PriorityVoice] {blocked} disconnesso — priorita' entrata.")
                except discord.Forbidden:
                    print(f"[PriorityVoice] Permessi insufficienti per {blocked}.")
        return

    # Caso 2: prova a entrare uno degli utenti bloccati
    if member.id in BLOCKED_USER_IDS and after.channel is not None:
        priority_channel = priority_is_in_voice(guild)
        if priority_channel and after.channel == priority_channel:
            try:
                await member.move_to(None)
                print(f"[PriorityVoice] {member} espulso — priorita' presente.")
            except discord.Forbidden:
                print(f"[PriorityVoice] Permessi insufficienti per {member}.")
        return


bot.run(TOKEN)
