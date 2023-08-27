import discord
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw,ImageOps
from discord import File
import io
import random

warm_colors = [(70,56,41),(87,51,22),(64,79,36),(78,90,100)]

async def getwelcomeimage(name: str = "nobody", avatar: discord.Asset = None):
    font_colors = random.choice(warm_colors)
    img: Image = Image.open("image_data/fancyborder.jpg")
    draw = ImageDraw.Draw(img)
    buffer_avatar = io.BytesIO()
    await avatar.save(buffer_avatar)
    buffer_avatar.seek(0)
    avatar_image = Image.open(buffer_avatar)
    AVATAR_SIZE = 55
    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE))
    circle_image = Image.new('L', (AVATAR_SIZE, AVATAR_SIZE))
    circle_draw = ImageDraw.Draw(circle_image)
    circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
    circle_image2 = Image.new('RGBA', (AVATAR_SIZE + 4, AVATAR_SIZE + 4), color=(255, 255, 255, 0))
    circle_draw2 = ImageDraw.Draw(circle_image2)
    circle_draw2.ellipse((0, 0, AVATAR_SIZE + 4, AVATAR_SIZE + 4),
                         fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    img.paste(circle_image2, (101, 88))
    img.paste(avatar_image, (103, 90), circle_image)
    font = ImageFont.truetype("fonts/BrannbollStencil_PERSONAL_USE.ttf", 16)
    font_title = ImageFont.truetype("fonts/arial.ttf", 20)
    font_name = ImageFont.truetype("fonts/DejaVuSansMono.ttf", 14 )
    draw.text((50, 20), f"Certificate of Entry", (25, 25, 25), font=font_title, align="center")
    draw.text((49, 19), f"Certificate of Entry", (255, 215, 0), font=font_title, align="center")
    draw.text((115, 48), "Alex Multiverse", fill=font_colors, font=ImageFont.truetype("fonts/arial.ttf", 16))
    draw.text((40, 50), f"Welcome to", fill=font_colors, font=font)
    name1 = [c for c in name if c.isalnum() or c in "_!@#$%^ &*()-=+~`'[],.?;:"]
    name1 = "".join(name1)
    name1 = name1[:28] + "..." if len(name1) > 28 else name1
    draw.text((18, 70), f"{name1: ^30}", (25, 25, 25), font=font_name)
    draw.text((35, 147), "Have fun and make some friends.", fill=font_colors, font=font, align="center")
    admins = ["Alex", "Lin", "Sylerfire", "Unjown", "Watermelon","Doge"]
    admin = random.choice(admins)
    draw.text((160 - len(admin) * 5, 167), f"from, {admin}", fill=font_colors, font=font)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='png')
    img_byte_arr.seek(0)
    return File(fp=img_byte_arr, filename="welcome.png")
