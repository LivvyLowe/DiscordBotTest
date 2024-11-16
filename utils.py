import random
import math
import json
import os
import numpy as np
from datetime import datetime


def roll(num_sides = 100):
    return random.randint(1,num_sides)

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


#Dice statistics variation

from scipy.stats import chisquare
import matplotlib.pyplot as plt

# Generate a bar graph showing the distribution of rolls and calculate chi-square test
def generate_randomness_graph(num_rolls=10000, num_sides=100):
    # Step 1: Roll the dice `num_rolls` times
    results = [random.randint(1, num_sides) for _ in range(num_rolls)]

    # Step 2: Calculate frequencies of each result
    frequencies = [results.count(i) for i in range(1, num_sides + 1)]

    # Step 3: Calculate the expected frequency for each result
    expected_frequency = num_rolls / num_sides

    # Step 4: Perform chi-square goodness-of-fit test
    chi_square_stat, p_value = chisquare(frequencies, f_exp=[expected_frequency] * num_sides)

    # Step 5: Plot the frequencies
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, num_sides + 1), frequencies, color='blue')
    plt.xlabel('Roll Result')
    plt.ylabel('Frequency')
    plt.title(f'Distribution of {num_rolls} Rolls of a 1d{num_sides}')
    plt.grid(axis='y', linestyle='--', linewidth=0.7)

    # Step 6: Save the plot to a file
    graph_file_path = "randomness_distribution.png"
    plt.savefig(graph_file_path)
    plt.close()

    return graph_file_path, chi_square_stat, p_value

# Add roll to server's roll history
def add_roll_to_history(server_id, user, roll_result, target_number, success, degrees):
    settings = load_settings()
    server_settings = settings.setdefault(str(server_id), {})
    roll_history = server_settings.setdefault("roll_history", [])

    roll_details = {
        "user": user,
        "roll_result": roll_result,
        "target_number": target_number,
        "success": success,
        "degrees": degrees,
        "timestamp": datetime.now().isoformat()
    }

    roll_history.append(roll_details)

    # Save updated settings back to the file
    save_settings(settings)

# Retrieve roll history for a specific server
def get_roll_history(server_id):
    settings = load_settings()
    server_settings = settings.get(str(server_id), {})
    return server_settings.get("roll_history", [])

# Generate randomness graph and perform statistical analysis for roll history
def generate_randomness_from_history(roll_results, num_sides=100):
    # Step 1: Calculate frequencies of each result
    frequencies = [roll_results.count(i) for i in range(1, num_sides + 1)]

    # Step 2: Calculate the expected frequency for each result
    num_rolls = len(roll_results)
    expected_frequency = num_rolls / num_sides

    # Step 3: Perform chi-square goodness-of-fit test
    chi_square_stat, p_value = chisquare(frequencies, f_exp=[expected_frequency] * num_sides)

    # Step 4: Calculate standard deviation of the roll results
    std_dev = np.std(roll_results)

    # Step 5: Plot the frequencies
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, num_sides + 1), frequencies, color='blue')
    plt.xlabel('Roll Result')
    plt.ylabel('Frequency')
    plt.title(f'Distribution of {num_rolls} Rolls of a 1d{num_sides}')
    plt.grid(axis='y', linestyle='--', linewidth=0.7)

    # Step 6: Save the plot to a file
    graph_file_path = "roll_history_randomness.png"
    plt.savefig(graph_file_path)
    plt.close()

    return graph_file_path, chi_square_stat, p_value, std_dev