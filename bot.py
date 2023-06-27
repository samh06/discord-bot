from pyarr import SonarrAPI
import discord
from discord import app_commands
from json import dump
from button_views import QueueView, NewView
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


# with open("halo.json", 'w') as file:
#     dump(, file, indent=2)


@tree.command(name="queue", description="View Sonarr queue", guild=discord.Object(id=962644497928441916))
async def queue_command(interaction):
    queue = sonarr.get_queue(page_size=9)['records']
    emb = discord.Embed(title="Queue")
    for record in queue:
        episode = sonarr.get_episode(record["episodeId"])
        seriesTitle = episode['series']['title']
        episodeNum = f"{episode['seasonNumber']}x{episode['episodeNumber']}"

        emb.add_field(
            name=f"{seriesTitle} - {episodeNum}", value=f"{size(record['sizeleft'])} - {record['timeleft']}")

    await interaction.response.send_message(embed=emb, ephemeral=True, view=QueueView())


@tree.command(name="new", guild=discord.Object(id=962644497928441916))
async def new_command(interaction, show_name: str):
    """Add a new Sonarr show.

    Parameters
    -----------
    show_name: str
        The name of the show
    """
    shows = sonarr.lookup_series(term=show_name)
    shows.insert(0, show_name)
    emb = discord.Embed(title="Shows")
    for image in shows[1]['images']:
        if image['coverType'] == 'poster':
            emb.set_image(url=image['remoteUrl'])
    emb.add_field(
        name=f"{shows[1]['title']} ({shows[1]['year']}) ({shows[1]['seriesType'].capitalize()})", value=shows[1]['overview'], inline=True)

    await interaction.response.send_message(embed=emb, ephemeral=True, view=NewView(shows=shows, sonarr=sonarr, i=1))


@tree.command(name="shows", description="View Sonarr shows", guild=discord.Object(id=962644497928441916))
async def shows_command(interaction):
    shows = sonarr.get_series()
    emb = discord.Embed(title="Shows")
    i = 0
    for show in shows:
        if i != 10 and show["seriesType"] == "standard":
            emb.add_field(name=show["title"], value=f"")
            i += 1

    await interaction.response.send_message(embed=emb, ephemeral=True, view=QueueView())


@client.event
async def on_ready():
    if environ['GUILD_ID']:
        await tree.sync(guild=discord.Object(id=962644497928441916))

    print("Ready!")

client.run(environ['TOKEN'])
