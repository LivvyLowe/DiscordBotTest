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
