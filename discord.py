import discord
import aiohttp
import asyncio
from discord.ext import commands, tasks
import os

TOKEN = os.environ["MTM5NzY3NTU0NzMyMDEyMzQ4Mg.GIT9FG.1eQk9_AvaxHWKimtbnKvD9XKegmqPyiFFL3Lyw"]
CHANNEL_NAME = os.environ["server-status"]
BATTLEMETRICS_SERVER_ID = "33392638"
BATTLEMETRICS_API = f"https://api.battlemetrics.com/servers/33392638"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def get_server_status():
    headers = {"User-Agent": "Mozilla/5.0 (Discord Bot)"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(BATTLEMETRICS_API) as response:
            print(f"[DEBUG] HTTP Status: {response.status}")
            if response.status != 200:
                return None
            data = await response.json()
            attributes = data.get("data", {}).get("attributes", {})
            return {
                "name": attributes.get("name", "Unknown"),
                "players": attributes.get("players", 0),
                "maxPlayers": attributes.get("maxPlayers", 0),
                "status": attributes.get("status", "unknown").capitalize(),
                "map": attributes.get("details", {}).get("map", "Unknown"),
                "updatedAt": attributes.get("updatedAt", "Unknown")
            }

def create_embed(status):
    embed = discord.Embed(
        title="🎮 ARMA Reforger Server Status",
        color=discord.Color.green() if status["status"].lower() == "online" else discord.Color.red()
    )
    embed.add_field(name="Server Name", value=status["name"], inline=False)
    embed.add_field(name="Status", value=status["status"], inline=True)
    embed.add_field(name="Map", value=status["map"], inline=True)
    embed.add_field(name="Players", value=f'{status["players"]}/{status["maxPlayers"]}', inline=True)
    embed.set_footer(text=f"Last Updated: {status['updatedAt']}")
    return embed

@bot.command(name="serverstatus")
async def server_status(ctx):
    status = await get_server_status()
    if status is None:
        await ctx.send("❌ Failed to fetch server status.")
        return
    embed = create_embed(status)
    await ctx.send(embed=embed)

@tasks.loop(minutes=30)
async def periodic_status_update():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == CHANNEL_NAME:
                status = await get_server_status()
                if status:
                    embed = create_embed(status)
                    await channel.send(embed=embed)
                else:
                    await channel.send("❌ Could not fetch server status.")
                return
    print(f"❌ Channel named '{CHANNEL_NAME}' not found.")

@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    periodic_status_update.start()

bot.run(TOKEN)
