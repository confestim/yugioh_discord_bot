import discord
from discord.ext import commands
import yugioh
import asyncio
import requests
import os
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

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


@bot.command()
async def graph(ctx, decks=None):
    class Match:
        def __init__(self, date, player_1, deck_1, player_2, deck_2, winner):
            self.date = date
            self.player_1 = player_1
            self.deck_1 = deck_1
            self.player_2 = player_2
            self.deck_2 = deck_2
            self.winner = winner

    winners = []
    winner_decks = []

    channel = bot.get_channel(847137656549933096)
    messages = await channel.history().flatten()

    removeable = await ctx.send(f"📊 Creating graph from {len(messages)} entries... 📊")

    for i in messages:

        # example entry:
        # 15.06.2021, Sami:Gishki vs Boyan:Spellcaster;Boyan
        message = i.content

        date = message.split(",")[0]
        matchup = message.split(",")[1]

        player_1 = matchup.split("vs")[0]
        player_2 = matchup.split("vs")[1]
        player_2 = player_2.split(";")[0]

        name_1 = player_1.split(":")[0].strip()
        deck_1 = player_1.split(":")[1].strip()

        name_2 = player_2.split(":")[0].strip()
        deck_2 = player_2.split(":")[1].strip()

        winner = message.split(";")[1]

        match = Match(date, name_1, deck_1, name_2, deck_2, winner)
        winners.append(match.winner.strip())

        print(match.winner)
        if match.winner == match.player_1:
            winner_decks.append(match.deck_1.strip())
        elif match.winner == match.player_2:
            winner_decks.append(match.deck_2.strip())

        # await ctx.send(f"{match.player_1}")
    if not decks:
        winner_counter = Counter(winners)
        winner_number = np.array([])
        winner_names = []

        for k, v in winner_counter.items():
            winner_number = np.append(winner_number, int(v))
            winner_names.append(k)

    elif decks == "decks":
        winner_counter = Counter(winner_decks)
        winner_number = np.array([])
        winner_names = []

        for k, v in winner_counter.items():
            winner_number = np.append(winner_number, int(v))
            winner_names.append(k)

    elif decks == "text":
        winner_counter = Counter(winners)
        em = discord.Embed(title="Stats", colour=discord.Colour(0x8c0303))
        for k, v in winner_counter.items():
            em.add_field(name=f"{k}",value=f"{v}")
    plt.pie(winner_number, labels=winner_names, startangle=90, autopct='%1.1f%%')
    plt.savefig("winners.png")
    plt.close()
    await ctx.send(file=discord.File("winners.png"))

    await asyncio.sleep(1)
    await removeable.delete()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(bot.start(os.environ["TOKEN"]))
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
finally:
    loop.close()