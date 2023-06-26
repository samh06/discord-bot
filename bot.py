from pyarr import SonarrAPI
import discord
from discord import app_commands
from json import dump
from queue_view import QueueView
from hurry.filesize import size
from dotenv import load_dotenv
from os import environ
load_dotenv()
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Set Host URL and API-Key
host_url = environ['HOST_URL']

# You can find your API key in Settings > General.
api_key = environ['API_KEY']

# Instantiate SonarrAPI Object
sonarr = SonarrAPI(host_url, api_key)


# Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
@tree.command(name="queue", description="View Sonarr queue", guild=discord.Object(id=962644497928441916))
async def first_command(interaction):
    returnStr = ""
    queue = sonarr.get_queue(page_size=9)['records']
    emb = discord.Embed(title="Queue")
    for record in queue:
        episode = sonarr.get_episode(record["episodeId"])
        seriesTitle = episode['series']['title']
        episodeNum = f"{episode['seasonNumber']}x{episode['episodeNumber']}"

        emb.add_field(
            name=f"{seriesTitle} - {episodeNum}", value=f"{size(record['sizeleft'])} - {record['timeleft']}")

    await interaction.response.send_message(embed=emb, ephemeral=True, view=QueueView())


@client.event
async def on_ready():
    if environ['GUILD_ID']:
        await tree.sync(guild=discord.Object(id=962644497928441916))
    print("Ready!")

client.run(environ['TOKEN'])
