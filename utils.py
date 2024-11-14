import random

def roll():
    return random.randint(1,100)

def is_admin(user):
    # Placeholder function for admin check
    # Add your own logic to check if the user is an admin
    return user.permissions_in(user.guild).administrator