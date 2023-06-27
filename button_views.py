import discord
from pyarr import SonarrAPI
from json import dump


class QueueView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Next Page", style=discord.ButtonStyle.gray)
    async def gray_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"This is an edited button response!")


class SelectedView(discord.ui.View):
    def __init__(self, *, show, sonarr, prev, info, timeout=180):
        self.show = show
        self.sonarr: SonarrAPI = sonarr
        self.prev: str = prev
        self.info = info
        self.media_types: list = ["TV", "Anime"]
        super().__init__(timeout=timeout)

    async def create_buttons(self):
        i = 0
        if self.prev == 'None':
            for quality in self.sonarr.get_quality_profile():
                button = discord.ui.Button(
                    label=f"{quality['name']}", style=discord.ButtonStyle.gray)
                button.custom_id = f"{quality['id']}"
                button.callback = self.quality_callback
                self.add_item(button)

        elif self.prev == 'Quality':
            for type in self.media_types:
                button = discord.ui.Button(
                    label=f"{type}", style=discord.ButtonStyle.gray)
                button.custom_id = type
                button.callback = self.type_callback
                self.add_item(button)

    async def quality_callback(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="Type", description="What type of media is this?")
        view = SelectedView(
            show=self.show, sonarr=self.sonarr, info=[interaction.data['custom_id']], prev='Quality')
        await view.create_buttons()
        await interaction.response.edit_message(embed=emb, view=view)

    async def type_callback(self, interaction: discord.Interaction):
        if interaction.data['custom_id'] == 'Anime':
            language = 2
            rootDir = "E:\\Media\\Anime"
        else:
            language = 1
            rootDir = "E:\\Media\\TV Shows"
        self.sonarr.add_series(
            series=self.show, quality_profile_id=int(self.info[0]), language_profile_id=language, root_dir=rootDir, search_for_missing_episodes=True)
        emb = discord.Embed(
            title="Added", description=f"Added {self.show['title']}!")
        await interaction.response.edit_message(embed=emb, view=None)


class NewView(discord.ui.View):
    def __init__(self, *, shows, i, sonarr, timeout=180):
        self.shows: list = shows
        self.i: int = i
        self.sonarr: SonarrAPI = sonarr
        self.current_wanted = -1
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Previous Show", style=discord.ButtonStyle.gray)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i > 1:
            self.i -= 1
        await self.replaceShowEmbed(interaction=interaction, button=button)

    @discord.ui.button(label="Next Show", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i < len(self.shows):
            self.i += 1
        await self.replaceShowEmbed(interaction=interaction, button=button)

    @discord.ui.button(label="Select Show", style=discord.ButtonStyle.gray)
    async def select_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = SelectedView(
            show=self.shows[self.i], sonarr=self.sonarr, info=[], prev='None')
        await view.create_buttons()
        embed = discord.Embed(title="Quality",
                              description=f"Select a quality to download {self.shows[self.i]['title']} in.")
        await interaction.response.edit_message(embed=embed, view=view)

    async def replaceShowEmbed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if button.label == "Select Show":
            emb = discord.Embed(title="Added")
            emb.add_field(
                "Episodes", value=f"Added {len(self.sonarr.get_wanted())-self.current_wanted} to the queue.")
            await interaction.response.edit_message(embed=emb)
        else:
            emb = discord.Embed(title="Shows")
            for image in self.shows[self.i]['images']:
                if image['coverType'] == 'poster':
                    emb.set_image(url=image['remoteUrl'])

            emb.add_field(
                name=f"{self.shows[self.i]['title']} ({self.shows[self.i]['year']}) ({self.shows[self.i]['seriesType'].capitalize()})",
                value=self.shows[self.i]['overview'], inline=True)

            await interaction.response.edit_message(embed=emb, view=NewView(shows=self.shows, sonarr=self.sonarr, i=self.i))
