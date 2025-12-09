from thonny import get_workbench
import tkinter as tk

import os
from .exercise_view import ExerciseView
from .exercise_loader import create_loader




LOADER_TYPE = "filesystem"
PLUGIN_DIR = os.path.dirname(__file__)



if LOADER_TYPE == "filesystem":
    EXERCISE_LOADER = create_loader("filesystem", plugin_dir=PLUGIN_DIR)
elif LOADER_TYPE == "api":
    # EXERCISE_LOADER = create_loader("api", api_url=API_URL, api_key=API_KEY)
    raise NotImplementedError("API loader not yet configured")
else:
    raise ValueError(f"Unknown loader type: {LOADER_TYPE}")














def load_plugin():
    
    get_workbench().exercise_code = tk.StringVar(value="")

    get_workbench().add_view(ExerciseView,"Exercise", "e")# Right sidebar
    
    get_workbench().after(200, add_toolbar_widgets)










    
def add_toolbar_widgets():
    try:
        toolbar = get_workbench().get_toolbar()
        
        all_widgets = toolbar.grid_slaves(row=0)
        max_column = -1
        for widget in all_widgets:
            col = widget.grid_info().get('column', -1)
            if col > max_column:
                max_column = col
        
        next_column = max_column + 1
        
        #  separator
        sep = tk.Frame(toolbar, width=4, bg="#E0E0E0")
        sep.grid(row=0, column=next_column, padx=2, sticky="ns")
        next_column += 1
        
        #  label
        label = tk.Label(toolbar, text="Exercise:")
        label.grid(row=0, column=next_column, padx=(4, 2), sticky="w")
        next_column += 1
        
        #  entry
        entry = tk.Entry(toolbar, textvariable=get_workbench().exercise_code, 
                        width=12, font=("TkDefaultFont", 9))
        entry.grid(row=0, column=next_column, padx=2, sticky="w")
        next_column += 1
        
        #  buttons
        btn1 = tk.Button(toolbar, text="Pull Ex", 
                        command=lambda: load_exercise(get_workbench().exercise_code.get()),
                        width=6)
        btn1.grid(row=0, column=next_column, padx=1, sticky="w")
        next_column += 1

    except Exception as e:
        shell = get_workbench().get_view("ShellView")
        shell.text.direct_insert("end",f"Error adding toolbar widgets: {e}")







def load_exercise(exercise_code):

    shell = get_workbench().get_view("ShellView")
    
    exercise_code = exercise_code.strip()
    
    if not exercise_code:
        shell.text.direct_insert("end", "ERROR: No input provided\n")
        return
    
    if exercise_code.count("/") > 1:
        shell.text.direct_insert("end", "ERROR: Only one '/' allowed (format: bucket/code)\n")
        return
    
    dangerous_chars = ['\\', '..', '\0']
    if any(char in exercise_code for char in dangerous_chars):
        shell.text.direct_insert("end", "ERROR: Invalid characters in input\n")
        return
    
    # Parse bucket and code
    if "/" in exercise_code:
        parts = exercise_code.split("/", 1)
        bucket = parts[0].strip()
        code = parts[1].strip()
        
        if not bucket or not code:
            shell.text.direct_insert("end", "ERROR: Both bucket and code must be provided\n")
            return
    else:
        bucket = "default"
        code = exercise_code
    
    try:
        shell.text.direct_insert("end", f"Loading exercise: {bucket}/{code}\n")
        
        # Load from source (filesystem or API)
        markdown_content, exercise_dir = EXERCISE_LOADER.load_exercise(code, bucket)
        
        view = get_workbench().get_view("ExerciseView")
        if view:
            view.load_exercise(markdown_content, exercise_dir)
            get_workbench().show_view("ExerciseView")
            shell.text.direct_insert("end", f"✓ Exercise {code} loaded successfully\n")
        else:
            shell.text.direct_insert("end", "ERROR: ExerciseView not found\n")
    
    except FileNotFoundError as e:
        shell.text.direct_insert("end", f"ERROR: Exercise not found - {str(e)}\n")
    except Exception as e:
        shell.text.direct_insert("end", f"ERROR: {str(e)}\n")




































    
"""
def pull_exercise(exercise_code):
    print(f"Pulling exercise: {exercise_code}")
    if not exercise_code:
        print("ERROR: No exercise code provided")
        return
    shell = get_workbench().get_view("ShellView")
    shell.text.direct_insert("end",exercise_code)

def run_test(exercise_code):
    print(f"Running test for exercise: {exercise_code}")
    if not exercise_code:
        print("ERROR: No exercise code provided")
        return
    shell = get_workbench().get_view("ShellView")
    shell.text.direct_insert("end",exercise_code)

def pull_solution(exercise_code):
    print(f"Pulling solution for exercise: {exercise_code}")
    if not exercise_code:
        print("ERROR: No exercise code provided")
        return

    shell = get_workbench().get_view("ShellView")
    shell.text.direct_insert("end",exercise_code)

"""
"""
    get_workbench().add_command(
        command_id="pull_exercise",
        menu_name="run",
        command_label="Pull Exercise",
        handler=lambda: pull_exercise(get_workbench().exercise_code.get()),
        include_in_toolbar=False,  
        group=10
    )
    
    get_workbench().add_command(
        command_id="run_test", 
        menu_name="run",
        command_label="Run Test",
        handler=lambda: run_test(get_workbench().exercise_code.get()),
        include_in_toolbar=False,
        group=10
    )
    
    get_workbench().add_command(
        command_id="pull_solution",
        menu_name="run", 
        command_label="Pull Solution",
        handler=lambda: pull_solution(get_workbench().exercise_code.get()),
        include_in_toolbar=False,
        group=10
    )
"""