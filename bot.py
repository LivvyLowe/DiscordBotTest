import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

from utils import roll, is_admin, degrees

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
async def test(ctx, tn):
    
    die = roll()
    outcome, d = degrees(tn, die)
    
    await ctx.reply(f'Target Number: {tn} \nDice Result: {die} \n {d} degrees of {outcome}!')
    

# Run the bot
bot.run(TOKEN)
