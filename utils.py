import random
import math
import json
import os



def roll():
    return random.randint(1,100)

def is_admin(user):
    # Placeholder function for admin check
    # Add your own logic to check if the user is an admin
    return user.permissions_in(user.guild).administrator

def degrees(tn, roll):
    tn = int(tn)
    roll = int(roll)
    
    d = math.floor((tn-roll)/10)

    success = False
    if roll <= tn:
        success = True

    degrees = abs(d) + 1
    return success, degrees

def parse_math(math_str):
    try:
        # Check if the input can be directly converted to an integer
        if math_str.isdigit():
            return int(math_str)
        
        # Use eval to compute the result of the mathematical expression
        result = eval(math_str)
        # Return result as integer if it is a whole number, otherwise as a float
        return int(result) if result.is_integer() else result
    except (SyntaxError, ZeroDivisionError, NameError, TypeError, ValueError):
        return "Invalid input"





###SERVER SETTINGS

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "embed_title": "🎲Test Roll🎲",
    "bot_color": "0x1abc9c",
    "command_prefix": "!",  # New default setting for command prefix
    "footer_success": "The Emperor protects!",
    "footer_failure": "The Emperor protects!",
    
}

# Load settings from the file
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If the file is empty or contains invalid JSON, return an empty dictionary
            return {}
    else:
        return {}

# Save settings to the file
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)

# Get settings for a specific server
def get_server_setting(server_id, setting_name, default_value=None):
    settings = load_settings()
    return settings.get(str(server_id), {}).get(setting_name, default_value)

# Set a server-specific setting
def set_server_setting(server_id, setting_name, value):
    settings = load_settings()
    server_settings = settings.setdefault(str(server_id), {})
    server_settings[setting_name] = value
    save_settings(settings)

# Initialize server settings with defaults if they don't exist
def initialize_server_settings(server_id):
    settings = load_settings()
    server_settings = settings.setdefault(str(server_id), {})

    # Ensure all default settings are present
    for key, value in DEFAULT_SETTINGS.items():
        if key not in server_settings:
            server_settings[key] = value

    save_settings(settings)

# Initialize settings for all servers (existing and new)
def initialize_all_servers(bot):
    settings = load_settings()
    for guild in bot.guilds:
        initialize_server_settings(guild.id)