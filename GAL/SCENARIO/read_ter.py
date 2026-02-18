import os
from pynput import keyboard
import time

def get_input()-> int:
    #  0 == enter
    # -1 == up
    #  1 == down
    input_value:int|None = None

    with keyboard.Events() as events:
        for event in events:
            if event.key == keyboard.Key.esc:
                raise RuntimeError('Escaped file selection')
            elif event.key == keyboard.Key.enter:
                input_value = 0
                break
            elif event.key == keyboard.Key.up:
                input_value = -1
                break
            elif event.key == keyboard.Key.down:
                input_value = 1
                break
    return input_value

def select_file():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_dirs:list = []
    for filename in os.listdir(dir_path):
        full = os.path.join(dir_path, filename)
        if os.path.isfile(full): 
            if not(full.split('.')[1] == "sen" or full.split('.')[1] == "py"):
                file_dirs.append(full)

    selected_file:bool = False
    selection_index = 0
    while not selected_file:
        if selection_index > len(file_dirs) - 1: selection_index = 0
        elif selection_index < 0: selection_index = len(file_dirs) - 1

        terminal_text:str = " - - - PLEASE SELECT A FILE TO CONVERT - - -\n"
        for file_index in range(len(file_dirs)):
            if file_index == selection_index: terminal_text += f" > | {file_dirs[file_index]}\n" 
            else: terminal_text += f"   | {file_dirs[file_index]}\n"
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(terminal_text, " - - - - - - - - - ")
        time.sleep(0.17)

        input_value = get_input()
        if input_value == None:
            pass
        elif input_value == 0:
            selected_file = True
        else:
            selection_index += input_value

    print(f"You opened \"{file_dirs[selection_index]}\", Confirm[y/n]")
    while True:
        confirm:str = input().strip().lower()
        if confirm == 'y': return file_dirs[selection_index]
        else: return None


def edit_ter(file:str):
    with open(file, "rb") as terrain_data:
        temp = terrain_data.read()
        print(temp)


if __name__ == "__main__":
    try:
        file:str = select_file()
        if file() != None: edit_ter(file)
    except RuntimeError as error:
        input(f"Something went wrong or the user canceled their selection!\n Error Msg = {error}")
    else:
        input("Have a good day!")