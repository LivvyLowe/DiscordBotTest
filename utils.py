import random
import math

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

    if tn < roll:
        outcome = "failure"
    else:
        outcome = "success"

    degrees = abs(d) + 1
    
    return outcome, degrees
