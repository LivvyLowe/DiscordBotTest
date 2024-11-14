import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

import utils 

# Load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable intents for reading message content

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='test')
async def test(ctx, inputstr):
    
    tn = utils.parse_math(inputstr)
    
    die = utils.roll()
    outcome, d = utils.degrees(tn, die)
    
    await ctx.reply(f'Target Number: {inputstr} →` {tn} `   \nDice Result: 1d100 → ` {die} ` \n {d} degrees of {outcome}!')

@bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(title="Bot Information", description="A simple Discord bot", color=0x00ff00)
    embed.add_field(name="Author", value="Your Name")
    embed.add_field(name="Version", value="1.0")
    await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)
