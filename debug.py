import os

DEBUG = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
