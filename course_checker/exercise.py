from tkinter import messagebox
from thonny import get_workbench
import tkinter as tk
from tkinter import ttk
from .checker import check_code
import re
import os 

# required dependencies
#  tkinterweb markdown2 add them in the setup.py
from tkinterweb import HtmlFrame
from markdown2 import Markdown





class ExerciseView(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        
        # Track current exercise
        self.current_exercise_dir = None
        #self.current_bucket = None
        #self.plugin_dir = os.path.dirname(__file__)
        
        self.markdown_converter = Markdown(
            extras=['fenced-code-blocks', 'tables', 'break-on-newline', 'code-friendly']
        )
        
        
        self.html_frame = HtmlFrame(self)
        self.html_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Button frame (created but buttons added dynamically)
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Button references (will be created/destroyed as needed)
        self.run_button = None
        self.solution_button = None
        
        # Status bar
        #self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN)
        #self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    



    def _update_buttons(self):
        """Create or destroy buttons based on available files"""
        # Clear existing buttons
        if self.run_button:
            self.run_button.destroy()
            self.run_button = None
        if self.solution_button:
            self.solution_button.destroy()
            self.solution_button = None
        
        if not self.current_exercise_dir:
            return
        
        test_file = os.path.join(self.current_exercise_dir, 'tests.toml')
        
        solution_file = os.path.join(self.current_exercise_dir, 'solution.py')
        

        if os.path.exists(test_file):
            self.run_button = ttk.Button(
                self.button_frame,
                text="▶ Run Tests",
                command=self.run_tests
            )
            self.run_button.pack(side=tk.LEFT, padx=5)
        
        if os.path.exists(solution_file):
            self.solution_button = ttk.Button(
                self.button_frame,
                text="💡 Show Solution",
                command=self.show_solution
            )
            self.solution_button.pack(side=tk.LEFT, padx=5)
    


    def load_markdown(self, markdown_text, exercise_dir):
        """Load markdown text and render it as HTML"""
        # Store current exercise info
        self.current_exercise_dir = exercise_dir
        
        try:
            html_content = self.markdown_converter.convert(markdown_text)
            safe_html = self._sanitize_html(html_content)
            full_html = self._create_full_html(safe_html)
            
            self.html_frame.load_html(full_html)
            self.status_bar.config(text="Exercise loaded successfully")
            
            self._update_buttons()
            
        except Exception as e:
            error_msg = f"Error rendering markdown: {str(e)}"
            print(error_msg)
            self.status_bar.config(text=error_msg)
            error_html = self._create_full_html(f"<h1>Error</h1><p>{error_msg}</p><pre>{markdown_text}</pre>")
            self.html_frame.load_html(error_html)




    def run_tests(self):
        """Run the tests for current exercise"""
        check_code()
    
    def show_solution(self):
        """Show the solution"""
        # Open solution.py in editor
        pass



















    def _sanitize_html(self, html_content):
        """Remove potentially dangerous HTML elements"""
        # Remove script tags
        cleaned = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        # Remove inline event handlers
        cleaned = re.sub(r'\son\w+\s*=\s*["\'].*?["\']', '', cleaned, flags=re.IGNORECASE)
        # Remove javascript: protocol
        cleaned = re.sub(r'javascript:', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned


    
        ## main adding was 20
    def _create_full_html(self, content):
        """Create a full HTML document with GitHub-style CSS"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 
                         'Ubuntu', 'Cantarell', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #24292f;
            background-color: #f6f8fa;
            margin: 0;
            padding: 0px; 
            font-size: 19px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 40px 60px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            border-radius: 0px;
        }}
        
        h1 {{
            color: #1f2328;
            border-bottom: 1px solid #d0d7de;
            padding-bottom: 0.3em;
            margin-top: 24px;
            margin-bottom: 16px;
            font-size: 2.1em;
            font-weight: 600;
        }}
        
        h2 {{
            color: #1f2328;
            border-bottom: 1px solid #d0d7de;
            padding-bottom: 0.3em;
            margin-top: 24px;
            margin-bottom: 16px;
            font-size: 1.6em;
            font-weight: 600;
        }}
        
        h3 {{
            color: #1f2328;
            margin-top: 24px;
            margin-bottom: 16px;
            font-size: 1.3em;
            font-weight: 600;
        }}
        
        p {{
            margin-top: 0;
            margin-bottom: 16px;
            font-size: 17px;
        }}
        
        code {{
            background-color: rgba(175,184,193,0.2);
            padding: 0.2em 0.4em;
            border-radius: 6px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 15px;
        }}
        
        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            border: 1px solid #d0d7de;
            margin: 16px 0;
            overflow-x: auto;
            line-height: 1.45;
            font-size: 15px;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            border: none;
            font-size: 15px;
        }}
        
        blockquote {{
            border-left: 4px solid #d0d7de;
            padding: 0 16px;
            margin: 16px 0;
            color: #57606a;
        }}
        
        ul, ol {{
            padding-left: 2em;
            margin: 16px 0;
        }}
        
        li {{
            margin: 0.25em 0;
            font-size: 17px;
        }}
        
        a {{
            color: #0969da;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            margin: 16px 0;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            display: block;
            overflow-x: auto;
        }}
        
        th, td {{
            border: 1px solid #d0d7de;
            padding: 6px 13px;
            text-align: left;
        }}
        
        th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        
        tr:nth-child(even) {{
            background-color: #f6f8fa;
        }}
        
        hr {{
            border: none;
            border-bottom: 1px solid #d0d7de;
            margin: 24px 0;
        }}
        
        .hint {{
            background-color: #fff8c5;
            border: 1px solid #d4c827;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
        }}
        
        .important {{
            background-color: #ddf4ff;
            border: 1px solid #54aeff;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
        }}
        
        .warning {{
            background-color: #fff5b1;
            border: 1px solid #bf8700;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
"""
    







def load_exercise_to_viewer(exercise_code, bucket="default"):
    shell = get_workbench().get_view("ShellView")
    plugin_dir = os.path.dirname(__file__)
    target_file_path = os.path.join(plugin_dir, 'bucket', bucket, exercise_code, 'index.md')
    
    shell.text.direct_insert("end", f"Loading file: {target_file_path}\n")

    try:
        with open(target_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        view = get_workbench().get_view("ExerciseView")
        if view:
            ex_dir =  target_file_path = os.path.join(plugin_dir, 'bucket', bucket, exercise_code)
            view.load_markdown(content,ex_dir)
            get_workbench().show_view("ExerciseView")
            shell.text.direct_insert("end", f"Exercise {exercise_code} loaded successfully\n")
        else:
            shell.text.direct_insert("end", "ERROR: ExerciseView not found\n")
            
    except FileNotFoundError:
        shell.text.direct_insert("end", f"ERROR: File not found: {target_file_path}\n")
    except Exception as e:
        shell.text.direct_insert("end", f"ERROR: {str(e)}\n")
































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
    
    if "/" in exercise_code:
        parts = exercise_code.split("/", 1)
        bucket = parts[0].strip()
        code = parts[1].strip()
        
        if not bucket or not code:
            shell.text.direct_insert("end", "ERROR: Both bucket and code must be provided\n")
            return
        
        load_exercise_to_viewer(code, bucket)
    else:
        load_exercise_to_viewer(exercise_code, "default")
    