import os
import re
from dotenv import load_dotenv
import discord
from discord.ext import commands
import matplotlib

import utils 

#constants
RPG_TEST_WORD = 'test'
OWNER_ID = 109626591377649664


# Load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable intents for reading message content

# Create bot instance
bot = commands.Bot(command_prefix=utils.DEFAULT_SETTINGS["command_prefix"], intents=intents)

# Custom check to see if the user is either the bot owner or an administrator
def is_owner_or_admin(ctx):
    return ctx.author.id == OWNER_ID or ctx.author.guild_permissions.administrator

@bot.event
async def on_guild_join(guild):
    # Initialize server settings when the bot joins a new server
    utils.initialize_server_settings(guild.id)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Avoid responding to the bot's own messages
    if message.author == bot.user:
        return

    server_id = message.guild.id
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
            
            
            
            ###         setting embed formatting & style
             
            # Load the custom bot color from server settings and convert it to a discord.Colour
            bot_color_hex = utils.get_server_setting(server_id, "bot_color", utils.DEFAULT_SETTINGS["bot_color"])
            bot_color = discord.Colour(int(bot_color_hex, 16))

            outcome_phrase = f"❌ Failed with ***{degrees} degrees of failure!*** ❌"
            footer_text = utils.get_server_setting(server_id, "footer_failure", "")
            if success:
                outcome_phrase = f"✅ Passed with ***{degrees} degrees of success!*** ✅"
                footer_text = utils.get_server_setting(server_id, "footer_success", "")
            
            #getting embed title from server settings
            embed_title = utils.get_server_setting(server_id, "embed_title", "🎲Test Roll🎲")
            
            
            

            # Create an embed to display the result of the test roll
            embed = discord.Embed(
                title=embed_title,
                description=f"Rolling 1d100 against target number `{target_number}`",
                color=bot_color
            )
            embed.add_field(name="Target Number (TN)", value=f"{content} → `{target_number}`")
            embed.add_field(name="Dice Result", value=str(roll), inline=False)
            embed.add_field(name="Outcome", value=outcome_phrase, inline=False)
            embed.set_footer(text=footer_text)

            # Reply to the user's message with the embed
            await message.reply(embed=embed, mention_author=True)
            
             # Record the roll in the server's roll history
            utils.add_roll_to_history(
                server_id=server_id,
                user=str(message.author),
                roll_result=roll,
                target_number=target_number,
                success=success,
                degrees=degrees
            )

        except Exception as e:
            # If there's an error parsing the input, respond with an error message
            await message.reply(f"Invalid test format! Please use something like 'test 75'. Error: {e}", mention_author=True)

    # Allow the bot to continue processing other commands, if any are present
    await bot.process_commands(message)

@bot.command(name='settings')
@commands.check(is_owner_or_admin)
async def settings(ctx, setting_name: str = None, *, value: str = None):
    """
    Generalized command to update server settings.
    Usage: !settings <setting_name> <value>
    """
    server_id = ctx.guild.id

    # If no arguments are provided, list all available settings
    if setting_name is None:
        available_settings = ', '.join(utils.DEFAULT_SETTINGS.keys())
        await ctx.send(f"Available settings: {available_settings}\n\nUsage: `!settings <setting_name> <value>`")
        return

    # Check if the setting name is valid
    if setting_name not in utils.DEFAULT_SETTINGS:
        await ctx.send(f"Invalid setting name `{setting_name}`. Available settings: {', '.join(utils.DEFAULT_SETTINGS.keys())}")
        return

    # Ensure a value is provided for the setting
    if value is None:
        await ctx.send(f"Please provide a value for `{setting_name}`.\n\nUsage: `!settings {setting_name} <value>`")
        return
    
   # If updating the bot_color setting, validate it
    if setting_name == "bot_color":
        # Ensure the color is a valid hexadecimal value
        if not re.match(r'^0x[0-9a-fA-F]{6}$', value):
            await ctx.send(f"Invalid color value `{value}`. Please provide a valid hex color code (e.g., 0x1abc9c).")
            return
    
    # Update the server setting
    utils.set_server_setting(server_id, setting_name, value)
    await ctx.send(f"Setting `{setting_name}` updated to: `{value}`")

@bot.command(name='show_randomness')
@commands.check(is_owner_or_admin)
async def show_randomness(ctx, num_rolls: int = 10000):
    """
    Command to generate a bar graph showing the randomness of the bot's rolls and calculate the chi-square test.
    Usage: !show_randomness <num_rolls>
    """
    await ctx.send(f"Generating randomness graph with {num_rolls} rolls...")

    # Step 1: Generate the graph and calculate chi-square statistic
    graph_file_path, chi_square_stat, p_value = utils.generate_randomness_graph(num_rolls=num_rolls)

    # Step 2: Send the graph to the channel
    if os.path.exists(graph_file_path):
        with open(graph_file_path, 'rb') as f:
            file = discord.File(f, filename=graph_file_path)
            await ctx.send(
                content=(
                    f"Here's a bar graph demonstrating the randomness of the dice rolls:\n\n"
                    f"**Chi-Square Statistic**: {chi_square_stat:.2f}\n"
                    f"**P-Value**: {p_value:.4f}\n\n"
                    f"{'The results are consistent with randomness.' if p_value > 0.05 else 'The results are not consistent with randomness.'}"
                ),
                file=file
            )
    else:
        await ctx.send("Sorry, an error occurred while generating the graph.")



@bot.command(name='roll_history')
@commands.check(is_owner_or_admin)
async def roll_history(ctx, user_query: str = None, limit: int = 10):
    """
    Command to retrieve and show the roll history for the server or a specific user.
    Usage: !roll_history <user_query> <limit>
    """
    server_id = ctx.guild.id
    roll_history = utils.get_roll_history(server_id)

    # Filter the roll history by user if user_query is provided
    if user_query:
        roll_history = [roll for roll in roll_history if user_query.lower() in roll['user'].lower()]

    # Limit the number of rolls displayed
    roll_history_to_display = roll_history[-limit:]

    if not roll_history_to_display:
        await ctx.send("No roll history available for the specified query.")
        return

    # Prepare the message with roll details
    history_message = f"**Roll History (last {len(roll_history_to_display)} rolls):**\n"
    for roll in roll_history_to_display:
        history_message += (
            f"- **User**: {roll['user']}, **Roll**: {roll['roll_result']}, **Target**: {roll['target_number']}, "
            f"**Success**: {'✅' if roll['success'] else '❌'}, **Degrees**: {roll['degrees']}, "
            f"**Time**: {roll['timestamp']}\n"
        )

    await ctx.send(history_message)
    
@bot.command(name='history_randomness')
@commands.check(is_owner_or_admin)
async def history_randomness(ctx, user_query: str = None):
    """
    Command to generate a bar graph showing the randomness of the roll history on the server.
    Optionally, specify a user to only include their rolls.
    Usage: !history_randomness <user_query>
    """
    server_id = ctx.guild.id
    roll_history = utils.get_roll_history(server_id)

    # Filter the roll history by user if user_query is provided
    if user_query:
        roll_history = [roll for roll in roll_history if user_query.lower() in roll['user'].lower()]

    if not roll_history:
        await ctx.send("No roll history available for the specified query.")
        return

    # Extract roll results from the filtered history
    roll_results = [roll['roll_result'] for roll in roll_history]

    # Generate the graph and calculate randomness statistics
    graph_file_path, chi_square_stat, p_value, std_dev = utils.generate_randomness_from_history(roll_results)

    # Send the graph to the channel
    if os.path.exists(graph_file_path):
        with open(graph_file_path, 'rb') as f:
            file = discord.File(f, filename=graph_file_path)
            await ctx.send(
                content=(
                    f"Here's a bar graph demonstrating the randomness of the roll history:\n\n"
                    f"**Chi-Square Statistic**: {chi_square_stat:.2f}\n"
                    f"**P-Value**: {p_value:.4f}\n"
                    f"**Standard Deviation**: {std_dev:.2f}\n\n"
                    f"{'The results are consistent with randomness.' if p_value > 0.05 else 'The results are not consistent with randomness.'}"
                ),
                file=file
            )
    else:
        await ctx.send("Sorry, an error occurred while generating the graph.")

@bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(title="Bot Information", description="A FFG test rolling bot by Livvy", color=0x00ff00)
    embed.add_field(name="Author", value="Livvy")
    embed.add_field(name="Version", value="0.7")
    await ctx.send(embed=embed)


# Run the bot
bot.run(TOKEN)
