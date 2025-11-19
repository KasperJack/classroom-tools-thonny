import subprocess
from tkinter import messagebox
from thonny import get_workbench

def run_tests():
    editor = get_workbench().get_editor_notebook().get_current_editor()
    current_script = editor.get_filename()
        
    if not current_script:
        messagebox.showerror("Error", "Please save your current file first.")
        return
    
    

    editor.save_file()
    shell = get_workbench().get_view("ShellView")

    shell.text.direct_insert("end",current_script)
    return

    
    shell.text.direct_insert("end", "\n=== Running Exercise Check ===\n", ("stderr",))
    
    cmd = ["python", current_script]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    output = result.stdout.strip()
    errors = result.stderr.strip()
    
    if output:
        shell.text.direct_insert("end", f"Program output: {output}\n", ("stdout",))
    
    if result.returncode != 0:
        shell.text.direct_insert("end", f"Errors:\n{errors}\n", ("stderr",))
        shell.text.direct_insert("end", "check failed due to errors\n", ("stderr",))
        return
    
    if output == "10":
        shell.text.direct_insert("end", "correct! Output is 10.\n", ("stdout",))
    else:
        shell.text.direct_insert("end", f"output was '{output}', expected '10'.\n", ("stderr",))
    
    shell.text.direct_insert("end", "=========================\n\n", ("stderr",))
    
    shell.text.see("end")