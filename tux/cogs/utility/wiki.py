import httpx
from discord.ext import commands
from loguru import logger

from tux.bot import Tux
from tux.ui.embeds import EmbedCreator
from tux.utils.flags import generate_usage


class Wiki(commands.Cog):
    def __init__(self, bot: Tux) -> None:
        self.bot = bot
        self.arch_wiki_base_url = "https://wiki.archlinux.org/api.php"
        self.atl_wiki_base_url = "https://atl.wiki/api.php"
        self.wiki.usage = generate_usage(self.wiki)
        self.arch_wiki.usage = generate_usage(self.arch_wiki)
        self.atl_wiki.usage = generate_usage(self.atl_wiki)

    def query_arch_wiki(self, search_term: str) -> tuple[str, str]:
        """
        Query the ArchWiki API for a search term and return the title and URL of the first search result.

        Parameters
        ----------
        search_term : str
            The search term to query the ArchWiki API with.

        Returns
        -------
        tuple[str, str]
            The title and URL of the first search result.
        """

        search_term = search_term.capitalize()

        params: dict[str, str] = {
            "action": "opensearch",
            "format": "json",
            "limit": "1",
            "search": search_term,
        }

        # Send a GET request to the ArchWiki API
        with httpx.Client() as client:
            response = client.get(self.arch_wiki_base_url, params=params)
            logger.info(f"GET request to {self.arch_wiki_base_url} with params {params}")

        # example response: ["pacman",["Pacman"],[""],["https://wiki.archlinux.org/title/Pacman"]]

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            return (data[1][0], data[3][0]) if data[1] else ("error", "error")
        return "error", "error"

    def query_atl_wiki(self, search_term: str) -> tuple[str, str]:
        """
        Query the atl.wiki API for a search term and return the title and URL of the first search result.

        Parameters
        ----------
        search_term : str
            The search term to query the atl.wiki API with.

        Returns
        -------
        tuple[str, str]
            The title and URL of the first search result.
        """

        search_term = search_term.capitalize()

        params: dict[str, str] = {
            "action": "opensearch",
            "format": "json",
            "limit": "1",
            "search": search_term,
        }

        # Send a GET request to the ATL Wiki API
        with httpx.Client() as client:
            response = client.get(self.atl_wiki_base_url, params=params)
            logger.info(f"GET request to {self.atl_wiki_base_url} with params {params}")

        # example response: ["pacman",["Pacman"],[""],["https://atl.wiki/title/Pacman"]]

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            return (data[1][0], data[3][0]) if data[1] else ("error", "error")
        return "error", "error"

    @commands.hybrid_group(
        name="wiki",
        aliases=["wk"],
    )
    async def wiki(self, ctx: commands.Context[Tux]) -> None:
        """
        Wiki related commands.

        Parameters
        ----------
        ctx : commands.Context[Tux]
            The context object for the command.
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help("wiki")

    @wiki.command(
        name="arch",
    )
    async def arch_wiki(self, ctx: commands.Context[Tux], query: str) -> None:
        """
        Search the Arch Linux Wiki

        Parameters
        ----------
        ctx : commands.Context[Tux]
            The context object for the command.
        query : str
            The search query.
        """

        title: tuple[str, str] = self.query_arch_wiki(query)

        if title[0] == "error":
            embed = EmbedCreator.create_embed(
                bot=self.bot,
                embed_type=EmbedCreator.ERROR,
                user_name=ctx.author.name,
                user_display_avatar=ctx.author.display_avatar.url,
                description="No search results found.",
            )

        else:
            embed = EmbedCreator.create_embed(
                bot=self.bot,
                embed_type=EmbedCreator.INFO,
                user_name=ctx.author.name,
                user_display_avatar=ctx.author.display_avatar.url,
                title=title[0],
                description=title[1],
            )

        await ctx.send(embed=embed)

    @wiki.command(
        name="atl",
    )
    async def atl_wiki(self, ctx: commands.Context[Tux], query: str) -> None:
        """
        Search the All Things Linux Wiki

        Parameters
        ----------
        ctx : commands.Context[Tux]
            The context object for the command.
        query : str
            The search query.
        """

        title: tuple[str, str] = self.query_atl_wiki(query)

        if title[0] == "error":
            embed = EmbedCreator.create_embed(
                bot=self.bot,
                embed_type=EmbedCreator.ERROR,
                user_name=ctx.author.name,
                user_display_avatar=ctx.author.display_avatar.url,
                description="No search results found.",
            )

        else:
            embed = EmbedCreator.create_embed(
                bot=self.bot,
                embed_type=EmbedCreator.INFO,
                user_name=ctx.author.name,
                user_display_avatar=ctx.author.display_avatar.url,
                title=title[0],
                description=title[1],
            )

        await ctx.send(embed=embed)


async def setup(bot: Tux) -> None:
    await bot.add_cog(Wiki(bot))
