import pymongo








def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
from mastermelon import guessing_game
from mastermelon import melon

if __name__ == '__main__':
    print_hi('PyCharm')
    #guessing_game.runbot()
    try:
        melon.runbot()
    except RuntimeError or KeyboardInterrupt:
        print("exiting here")

