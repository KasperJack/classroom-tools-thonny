from thonny import get_workbench
import tkinter as tk
from .exercise import load_exercise, ExerciseView


def load_plugin():
    #print("DEBUG: course checker plugin is loading!")
    
    get_workbench().exercise_code = tk.StringVar(value="")


    get_workbench().add_view(
    ExerciseView,
    "Exercise",  # This is the view name
    "e"  # Right sidebar
    )



    
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
            
            btn2 = tk.Button(toolbar, text="Test", 
                           command=lambda: run_test(get_workbench().exercise_code.get()),
                           width=4)
            btn2.grid(row=0, column=next_column, padx=1, sticky="w")
            next_column += 1
            
            btn3 = tk.Button(toolbar, text="Solution", 
                           command=lambda: pull_solution(get_workbench().exercise_code.get()),
                           width=6)
            btn3.grid(row=0, column=next_column, padx=1, sticky="w")
            
        except Exception as e:
            shell = get_workbench().get_view("ShellView")
            shell.text.direct_insert("end",f"Error adding toolbar widgets: {e}")






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
    
    #short delay to ensure toolbar is ready
    get_workbench().after(200, add_toolbar_widgets)








    

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