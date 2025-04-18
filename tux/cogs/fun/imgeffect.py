import io

import discord
import httpx
from discord import app_commands
from discord.ext import commands
from loguru import logger
from PIL import Image, ImageEnhance, ImageOps

from tux.bot import Tux
from tux.ui.embeds import EmbedCreator


class ImgEffect(commands.Cog):
    def __init__(self, bot: Tux) -> None:
        self.bot = bot
        self.allowed_mimetypes = ["image/jpeg", "image/png"]

    imgeffect = app_commands.Group(name="imgeffect", description="Image effects")

    @imgeffect.command(name="deepfry", description="Deepfry an image")
    async def deepfry(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        if not self.is_valid_image(image):
            await self.send_invalid_image_response(interaction)
            return

        await interaction.response.defer(ephemeral=True)

        pil_image = await self.fetch_image(image.url)

        if pil_image:
            deepfried_image = self.deepfry_image(pil_image)
            await self.send_deepfried_image(interaction, deepfried_image)

        else:
            await self.send_error_response(interaction)

    def is_valid_image(self, image: discord.Attachment) -> bool:
        logger.info(f"Content type: {image.content_type}, Filename: {image.filename}, URL: {image.url}")

        return image.content_type in self.allowed_mimetypes

    @staticmethod
    async def fetch_image(url: str) -> Image.Image:
        logger.info("Fetching image from URL with HTTPX...")

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        return Image.open(io.BytesIO(response.content)).convert("RGB")

    @staticmethod
    def deepfry_image(pil_image: Image.Image) -> Image.Image:
        pil_image = pil_image.resize((int(pil_image.width * 0.25), int(pil_image.height * 0.25)))  # type: ignore
        pil_image = ImageEnhance.Sharpness(pil_image).enhance(100.0)

        r = pil_image.split()[0]
        r = ImageEnhance.Contrast(r).enhance(2.0)
        r = ImageEnhance.Brightness(r).enhance(1.5)

        colours = ((254, 0, 2), (255, 255, 15))
        r = ImageOps.colorize(r, colours[0], colours[1])
        pil_image = Image.blend(pil_image, r, 0.75)

        return pil_image.resize((int(pil_image.width * 4), int(pil_image.height * 4)))  # type: ignore

    async def send_invalid_image_response(self, interaction: discord.Interaction) -> None:
        logger.error("The file is not a permitted image.")

        embed = EmbedCreator.create_embed(
            bot=self.bot,
            embed_type=EmbedCreator.ERROR,
            user_name=interaction.user.name,
            user_display_avatar=interaction.user.display_avatar.url,
            title="Invalid File",
            description="The file must be an image. Allowed types are PNG, JPEG, and JPG.",
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def send_error_response(self, interaction: discord.Interaction) -> None:
        logger.error("Error processing the image.")

        embed = EmbedCreator.create_embed(
            bot=self.bot,
            embed_type=EmbedCreator.ERROR,
            user_name=interaction.user.name,
            user_display_avatar=interaction.user.display_avatar.url,
            title="Error",
            description="An error occurred while processing the image.",
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @staticmethod
    async def send_deepfried_image(interaction: discord.Interaction, deepfried_image: Image.Image) -> None:
        arr = io.BytesIO()
        deepfried_image.save(arr, format="JPEG", quality=1)
        arr.seek(0)

        file = discord.File(arr, filename="deepfried.jpg")

        await interaction.followup.send(file=file, ephemeral=True)


async def setup(bot: Tux) -> None:
    await bot.add_cog(ImgEffect(bot))
