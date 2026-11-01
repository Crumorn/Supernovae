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


def get_keystroke() ->str:
    input_key:int|None = None
    while input_key == None:
        b1:bytes = m.getch()
        if b1 == b"\x00":
            b2 = m.getch()
            if b2 == b"H":
                input_key = "up"
            elif b2 == b"P":
                input_key = "down"
            elif b2 == b"K":
                input_key = "left"
            elif b2 == b"M":
                input_key = "right"
        elif b1 == b"\r":
            input_key = "enter"
        elif b1 == b"\x1b":
            input_key = "esc"

    return input_key

def get_input() ->int:
    input_value:int|None = None
    key_press = get_keystroke()
    while input_value == None:
        if key_press == "up": input_value = -1
        elif key_press == "down": input_value = 1
        elif key_press == "enter": input_value = 0
        elif key_press == "esc": raise RuntimeError("User escaped input")

    return input_value

def select_option(selections:list[str], prefix:str = "", suffix:str = "", heading:str = "PLEASE SELECT A FILE TO CONVERT"):
    header:str = f"{prefix}\n - - - {heading} - - -\n"
    style_bars:str = "- - - "
    for index in range(len(heading)):
        if  index % 2 == 0:
            style_bars += "-"
        else:
            style_bars += " "
    if style_bars[-1] == "-":
        style_bars += " - - -"
    else:
        style_bars += "- - -"
    
    selection_index:int = 0
    while True:
        terminal_text:str = header
        
        for option in range(len(selections)):
            if option == selection_index: terminal_text += f" > | {selections[option]}\n {style_bars}\n" 
            else: terminal_text += f"   | {selections[option]}\n"
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(terminal_text, f"{style_bars}\n{suffix}")
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

def select_file(prefix:str = "", suffix:str = "", heading:str = ""):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_dirs:list = []
    for filename in os.listdir(dir_path):
        full = os.path.join(dir_path, filename)
        if os.path.isfile(full): 
            if full.split('.')[-1] == "ter":
                file_dirs.append(full)

    return select_option(file_dirs, prefix, suffix, heading)

def scrape_ter(file:str, truncate:bool = True):
    file_bytes:bytes
    with open(file, "r+b") as terrain_data:
        file_bytes = terrain_data.read()

    terrain_data = list(file_bytes)

    scrape_data:str = ""
    if truncate:
        for terrain_byte in range(len(terrain_data)):
            if terrain_data[terrain_byte] != 0 and terrain_data[terrain_byte] != 1:
                scrape_data += f"[pos: {terrain_byte}, value: {terrain_data[terrain_byte]}],"
    else:
        scrape_data = str(terrain_data)

    file_name:str = os.path.basename(file)
    scrape_path:str = os.path.join(documents_dir, file_name+".scraped")

    with open(scrape_path, "a") as scrape_file:
        scrape_file.write(scrape_data)

    print(f"Added \"{scrape_data}\" to \"{scrape_path}\"")
    input("Enter to continue")

def find_diff(file_1:str = None, file_2:str = None):
    if file_1 == None:
        file_1 = select_file(heading="Selecting File 1")
    if file_2 == None:
        file_2 = select_file(heading="Selecting File 2")


    file_1_bytes:bytes
    with open(file_1, "r+b") as terrain_data:
        file_1_bytes = terrain_data.read()

    file_2_bytes:bytes
    with open(file_2, "r+b") as terrain_data:
        file_2_bytes = terrain_data.read()

    comparison:str = ""
    pos:int = 0
    for byte_1, byte_2 in zip(file_1_bytes, file_2_bytes):
        if byte_1 != byte_2: comparison += f"[pos:{pos}, file_1_byte:{byte_1}, file_2_byte:{byte_2}],\n"
        pos += 1
    
    file_1_name = os.path.basename(file_1)
    file_2_name = os.path.basename(file_2)
    compare_file:str = f"{file_1_name.split('.')[0]}_compared_to_{file_2_name.split('.')[0]}.txt"
    compare_dir:str = os.path.join(documents_dir, "Comparisons")

    if not(os.path.exists(compare_dir)): os.makedirs(compare_dir)

    compare_dir = os.path.join(compare_dir, compare_file)

    with open(compare_dir, "w") as file:
        file.write(comparison)

    mode = input(comparison + f"\nCompared {file_1_name} and {file_2_name}\n\n 1 |Compare Two New\n 2 |Keep File 1\n 3 |Keep File 2\n   |Or just hit enter to continue\n > | ")
    try:
        mode = int(mode)
        if mode == 1:
            find_diff()
        elif mode == 2:
            find_diff(file_1=file_1)
        elif mode == 3:
            find_diff(file_2=file_2)
    except ValueError:
        pass

def compare_ter(file_1:str = None, file_2:str = None):
    if file_1 == None:
        file_1 = select_file(prefix="\tFile 1 Will be Displayed on Top\n", heading="Selecting File 1")
    if file_2 == None:
        file_2 = select_file(prefix="\tFile 2 Will be Displayed on the Bottom\n", heading="Selecting File 2")

        file_1_bytes:bytes
    with open(file_1, "r+b") as terrain_data:
        file_1_bytes = terrain_data.read()

    file_2_bytes:bytes
    with open(file_2, "r+b") as terrain_data:
        file_2_bytes = terrain_data.read()

    diff:list = []
    pos:int = 0
    for byte_1, byte_2 in zip(file_1_bytes, file_2_bytes):
        if byte_1 != byte_2: diff.append(pos)
        pos += 1

    def left_pad(text:str, text_len:int) ->str:
        text = str(text)
        if len(text) >= text_len: return text
        while len(text) < text_len:
            text = " " + text
        return text


    def console_text(pos:int, file_1_bytes:bytes, file_2_bytes:bytes, view_window_len:int = 16)->str:
        top_text:str = "Position       |"
        mid_text:str = "File 1 Bytes   |" 
        bot_text:str = "File 2 Bytes   |" 
        for i in range(view_window_len):
            top_text += f"{left_pad(pos + i, 6)}|"
            if pos+i < len(file_1_bytes):
                mid_text += f"{left_pad(int(file_1_bytes[pos+i]), 6)}|"
            else:
                mid_text +=f"{left_pad("NULL ", 6)}|"
            if pos+i < len(file_1_bytes):
                bot_text += f"{left_pad(int(file_2_bytes[pos+i]), 6)}|"
            else:
                bot_text +=f"{left_pad("NULL ", 6)}|"
        
        style_bars:str = ""
        for i in range(len(top_text)):
            style_bars += "-"
        controls:str = """
 - - - - - - CONTROLS - - - - - -
    Left Arrow  | Slides View Window Left
    Right Arrow | Slides View Window Right
    Up Arrow    | Moves to the Beginning
    Down Arrow  | Moves to the End
    Enter       | Moves Window To Next Position With a Difference (Wraps Around)
    Esc         | Exits Comparison"""

        return f"View Window Length: {view_window_len}\n{style_bars}\n{top_text}\n{style_bars}\n{mid_text}\n{style_bars}\n{bot_text}\n{style_bars}\n{controls}"

    view_window_len:int
    
    try:
        view_window_len = int(input("Please Set View Window Length (Default is 16): "))
        if view_window_len < 1 or view_window_len == "" or view_window_len == None:
            view_window_len = 16
    except ValueError:
        view_window_len = 16

    pos:int = 0
    max_pos_value:int
    if len(file_1_bytes) >= len(file_2_bytes) : max_pos_value = len(file_1_bytes)-(view_window_len+1)
    else: max_pos_value = len(file_2_bytes)-(view_window_len+1)

    input_value:int
    
    while True:
        if pos > max_pos_value: pos = -view_window_len
        elif pos < -view_window_len: pos = max_pos_value

        os.system('cls' if os.name == 'nt' else 'clear')
        print(console_text(pos, file_1_bytes, file_2_bytes, view_window_len))
        time.sleep(0.1)

        try:
            input_value = get_keystroke()
            if input_value == "esc": raise RuntimeError
        except RuntimeError:
            input("Exiting Comparison... Enter to Continue")
            break

        if input_value == None:
            continue
        elif input_value == "enter":
            old_pos:int = pos
            for value in diff:
                if pos < value: 
                    pos = value
                    break
            if old_pos == pos:
                pos = diff[0]
        elif input_value == "up":
            pos = 0
        elif input_value == "down":
            pos = max_pos_value
        elif input_value == "left":
            pos += -1
        elif input_value == "right":
            pos += 1
            

def edit_ter(file:str):
    with open(file, "rb") as terrain_data:
        temp = list(terrain_data.read())
        print(temp)
    input("Enter to continue")

if __name__ == "__main__":
    try:
        selections:list[str] = ["Edit Terrain", "Scrape Terrain", "Difference Terrain", "Compare Terrain","Change Settings"]
        selections.append("Quit")
        running:bool = True
        while running:
            selected_option = select_option(selections, heading="Please Select an Option Below")

            if selected_option == None:
                continue

            if selected_option == selections[0]:
                try:
                    file:str = select_file()
                    if file != None: edit_ter(file)
                except RuntimeError as error:
                    input(f"Something went wrong or the user canceled their selection!\n Error Msg = {error}")

            elif selected_option == selections[1]:
                try:
                    file:str = select_file()
                    if file != None: scrape_ter(file)
                except RuntimeError as error:
                    input(f"Something went wrong or the user canceled their selection!\n Error Msg = {error}")

            elif selected_option == selections[2]:
                find_diff()

            elif selected_option == selections[3]:
                compare_ter()

            elif selected_option == selections[-2]:
                change_settings()

            elif selected_option == selections[-1]:
                selecting_option = False
                break

            else: raise ValueError("Somehow an invalid option was selected, check that selection list is upto date...")
            
    except RuntimeError as error:
        input(f"Something went wrong or the user canceled their selection!\n Error Msg = {error}")
    except ValueError as error:
        input(f"A Value Error was Raised.\n Error Msg = {error}")
    else:
        input("Have a good day!")
