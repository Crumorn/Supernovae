import os
import msvcrt as m
import time

documents_dir:str = os.path.expanduser("~\\Documents\\EFS_Tooling\\Terrain_Editor")
if not(os.path.exists(documents_dir)): os.makedirs(documents_dir)

settings_file_dir:str = os.path.join(documents_dir, "read_ter.cfg")

default_settings:str = """truncate_ter_scrape:True"""

def parse_settings_str(settings_str:str)->dict:
    settings:dict = {}
    for line in settings_str.split("\n"):
        key_value = line.split(":")
        key = key_value[0]
        value = key_value[1]
        settings[key] = value
    return settings

settings:dict
try:
    with open(settings_file_dir, "x") as settings_file:
        settings_file.write(default_settings)
    
    settings = parse_settings_str(default_settings)
except:
    with open(settings_file_dir) as settings_file:
        settings = parse_settings_str(settings_file.read())


def save_settings():
    options_str:str = ""
    for k,v in settings.items():
        options_str += f"{k}:{v}"

    with open(settings_file_dir, "w") as options_file:
        options_file.write(options_str)


def change_settings():
    pass


def get_input() ->int:
    input_value:int|None = None
    while input_value == None:
        b1:bytes = m.getch()
        if b1 == b"\x00":
            b2 = m.getch()
            if b2 == b"H":
                input_value = -1
            elif b2 == b"P":
                input_value = 1
        elif b1 == b"\r":
            input_value = 0
        elif b1 == b"\x1b":
            raise RuntimeError("User Escaped Input")

    return input_value

def select_option(selections:list[str]):
    selection_index:int = 0
    while True:
        terminal_text:str = " - - - PLEASE SELECT A FILE TO CONVERT - - -\n"
        for option in range(len(selections)):
            if option == selection_index: terminal_text += f" > | {selections[option]}\n" 
            else: terminal_text += f"   | {selections[option]}\n"
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(terminal_text, "- - - - - - - - - - - - - - - - - - - - - - ")
        time.sleep(0.20)

        selected_option:str|None = None
        input_value = get_input()
        if input_value == 0:
            selected_option = selections[selection_index]
            break
        else:
            selection_index += input_value

        if selection_index > len(selections) - 1: selection_index = 0
        elif selection_index < 0: selection_index = len(selections) - 1


    return selected_option

def select_file():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_dirs:list = []
    for filename in os.listdir(dir_path):
        full = os.path.join(dir_path, filename)
        if os.path.isfile(full): 
            if full.split('.')[-1] == "ter":
                file_dirs.append(full)

    return select_option(file_dirs)

def scrape_ter(file:str, truncate:bool = True):
    file_bytes:bytes
    with open(file, "r+b") as terrain_data:
        file_bytes = terrain_data.read()

    terrain_data = list(file_bytes)

    scrape_data:str = ""
    if truncate:
        for terrain_byte in range(len(terrain_data)):
            if terrain_data[terrain_byte] != 0 or terrain_data[terrain_byte] != 1:
                scrape_data += f"[pos:{terrain_byte}, value{terrain_data[terrain_byte]}],"
    else:
        scrape_data = str(terrain_data)

    file_name:str = os.path.basename(file)
    scrape_path:str = os.path.join(documents_dir, file_name+".scraped")

    with open(scrape_path, "a") as scrape_file:
        scrape_file.write(scrape_data)

    print(f"Added \"{scrape_data}\" to \"{scrape_path}\"")

def edit_ter(file:str):
    with open(file, "rb") as terrain_data:
        temp = list(terrain_data.read())
        print(temp)


if __name__ == "__main__":
    try:
        selections:list[str] = ["Edit Terrain", "Scrape Terrain", "Change Settings"]
        selections.append("Quit")
        running:bool = True
        while running:
            selected_option = select_option(selections)

            if selected_option == None:
                continue

            if selected_option == "Edit Terrain":
                try:
                    file:str = select_file()
                    if file != None: edit_ter(file)
                    input("Enter to continue")
                except RuntimeError as error:
                    input(f"Something went wrong or the user canceled their selection!\n Error Msg = {error}")
            elif selected_option == "Scrape Terrain":
                try:
                    file:str = select_file()
                    if file != None: scrape_ter(file)
                    input("Enter to continue")
                except RuntimeError as error:
                    input(f"Something went wrong or the user canceled their selection!\n Error Msg = {error}")
            elif select_option == "Change Settings":
                change_settings()
            elif selected_option == "Quit":
                selecting_option = False
                break
            else: raise ValueError("Somehow an invalid option was selected, check that selection list is upto date...")
            
    except RuntimeError as error:
        input(f"Something went wrong or the user canceled their selection!\n Error Msg = {error}")
    except ValueError as error:
        input(f"A Value Error was Raised.\n Error Msg = {error}")
    else:
        input("Have a good day!")
