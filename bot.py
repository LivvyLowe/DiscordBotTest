import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

import utils 

#constants
COMMAND_PREFIX = '!'
RPG_TEST_WORD = 'test'



# Load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable intents for reading message content

# Create bot instance
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Avoid responding to the bot's own messages
    if message.author == bot.user:
        return

    # Detect if the message starts with the word "test"
    if message.content.lower().startswith(RPG_TEST_WORD):
        try:
            # Extract the target number after the keyword "test"
            content = message.content.lower().replace(RPG_TEST_WORD, "").strip()

            #Converty content into target number
            target_number = utils.parse_math(content)
            roll = utils.roll() # Roll 1d100

            # Calculate degrees of success or failure using the utility function
            success, degrees = utils.degrees(target_number, roll)
            
            outcome_phrase = f"❌ Failed with ***{degrees} degrees of failure!*** ❌"
            if success:
                outcome_phrase = f"✅ Passed with ***{degrees} degrees of success!*** ✅"
            

            # Create an embed to display the result of the test roll
            embed = discord.Embed(
                title="🎲Test Roll🎲",
                description=f"Rolling 1d100 against target number `{target_number}`",
                color=0x1abc9c
            )
            embed.add_field(name="Target Number (TN)", value=f"{content} → `{target_number}`")
            embed.add_field(name="Dice Result", value=str(roll), inline=False)
            embed.add_field(name="Outcome", value=outcome_phrase, inline=False)
            embed.set_footer(text="The Emperor Protects!")

            # Reply to the user's message with the embed
            await message.reply(embed=embed, mention_author=True)

        except Exception as e:
            # If there's an error parsing the input, respond with an error message
            await message.reply(f"Invalid test format! Please use something like 'test 75'. Error: {e}", mention_author=True)

    # Allow the bot to continue processing other commands, if any are present
    await bot.process_commands(message)
    
@bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(title="Bot Information", description="A FFG test rolling bot by Livvy", color=0x00ff00)
    embed.add_field(name="Author", value="Livvy")
    embed.add_field(name="Version", value="0.5.1")
    await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)
