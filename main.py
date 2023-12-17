# Press the green button in the gutter to run the script.
from mastermelon import melon
from datetime import datetime

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}, started at {datetime.utcnow()}')  # Press Ctrl+F8 to toggle the breakpoint.


if __name__ == '__main__':
    # todo: create required folders on first initalisation
    # folders: logs, mods, (maybe more)
    print_hi('PyCharm')
    # guessing_game.runbot()
    try:
        melon.runbot()
    except RuntimeError or KeyboardInterrupt:
        print("exiting here")
