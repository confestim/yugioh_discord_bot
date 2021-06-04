import discord
from discord.ext import commands
import yugioh
import asyncio
import requests
import os

bot = commands.Bot(command_prefix='y!',
                   description='''Card price checker bot''')

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    game = discord.Game("Check card prices! | y!help ")
    await bot.change_presence(activity=game, status=discord.Status.dnd)

@bot.command()
async def card(ctx, *, name=None):
    try:

        card = yugioh.get_card(card_name=name)
        r = requests.get(f"https://db.ygoprodeck.com/api/v7/cardinfo.php?id={card.id}")
        r = r.json()
        print(r)

        em = discord.Embed(title=f"{card.name}", color=discord.Colour(0x8c0303))
        em.set_thumbnail(url=r["data"][0]["card_images"][0]["image_url"])
        em.add_field(name="Description", value=f"{card.description}")
        em.add_field(name = "Price", value=f"{card.cardmarket_price}$")
        em.set_footer(text="Prices taken from cardmarket.com")
        
        await ctx.send(embed=em)
    
    except Exception as e:
        await ctx.send(e)

@bot.command()
async def archetype(ctx, *, name=None):
    try:

        card_list = yugioh.get_cards_by_name(keyword=name)
        
        em = discord.Embed(title=f"{name}", color=discord.Colour(0x8c0303))
        em.set_thumbnail(url="https://static.wikia.nocookie.net/yugioh/images/3/36/CardTrooper-TF04-JP-VG.jpg/revision/latest?cb=20120423204704")
        for i in card_list.list:
            card = yugioh.get_card(card_name=i)      
            em.add_field(name=f"{card.name}", value=f"{card.cardmarket_price}$")
            em.set_footer(text="Prices taken from cardmarket.com")
            
        await ctx.send(embed=em)
        
    except Exception as e:
        await ctx.send(e)

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(bot.start(os.environ["TOKEN"]))
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
finally:
    loop.close()