
from tkinter import messagebox
from thonny import get_workbench
import tkinter as tk
from tkinter import ttk
import re
import os

from tkinterweb import HtmlFrame
from markdown2 import Markdown


class ExerciseView(ttk.Frame):
    
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        
        self.current_exercise_dir = None  
        self.markdown_converter = Markdown(
            extras=['fenced-code-blocks', 'tables', 'break-on-newline', 'code-friendly']
        )
        
        self.html_frame = HtmlFrame(self)
        self.html_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        self.run_button = None
        self.solution_button = None
    
    def load_exercise(self, markdown_content, exercise_dir=None):

        self.current_exercise_dir = exercise_dir
        
        try:
            html_content = self.markdown_converter.convert(markdown_content)
            
            safe_html = self._sanitize_html(html_content)
            
            full_html = self._create_full_html(safe_html)
            
            self.html_frame.load_html(full_html)
            
            self._update_buttons()
            
        except Exception as e:
            error_msg = f"Error rendering markdown: {str(e)}"
            print(error_msg)
            error_html = self._create_full_html(
                f"<h1>Error</h1><p>{error_msg}</p><pre>{markdown_content}</pre>"
            )
            self.html_frame.load_html(error_html)
    
    def _update_buttons(self):
        if self.run_button:
            self.run_button.destroy()
            self.run_button = None
        if self.solution_button:
            self.solution_button.destroy()
            self.solution_button = None
        
        # If no local directory (e.g., loaded from API), no buttons
        if not self.current_exercise_dir:
            return
        
        # Check for tests.toml
        test_file = os.path.join(self.current_exercise_dir, 'tests.toml')
        
        # Check for solution.py
        solution_file = os.path.join(self.current_exercise_dir, 'solution.py')
        
        # Create Run Tests button if tests exist
        if os.path.exists(test_file):
            self.run_button = ttk.Button(
                self.button_frame,
                text="▶ Run Tests",
                command=self.run_tests
            )
            self.run_button.pack(side=tk.LEFT, padx=5)
        
        # Create Show Solution button if solution exists
        if os.path.exists(solution_file):
            self.solution_button = ttk.Button(
                self.button_frame,
                text="💡 Show Solution",
                command=self.show_solution
            )
            self.solution_button.pack(side=tk.LEFT, padx=5)
    
    def run_tests(self):
        """Run tests for the current exercise"""
        if not self.current_exercise_dir:
            messagebox.showwarning("No Tests", "Tests are not available for this exercise")
            return
        
        # Import here to avoid circular dependency
        from .checker import check_code
        check_code()
    
    def show_solution(self):
        """Show the solution for the current exercise"""
        if not self.current_exercise_dir:
            messagebox.showwarning("No Solution", "Solution is not available for this exercise")
            return
        
        solution_file = os.path.join(self.current_exercise_dir, 'solution.py')
        
        if os.path.exists(solution_file):
            # Open solution in editor
            get_workbench().get_editor_notebook().show_file(solution_file)
        else:
            messagebox.showwarning("No Solution", "Solution file not found")
    
    def _sanitize_html(self, html_content):
        """Remove potentially dangerous HTML elements"""
        # Remove script tags
        cleaned = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        # Remove inline event handlers
        cleaned = re.sub(r'\son\w+\s*=\s*["\'].*?["\']', '', cleaned, flags=re.IGNORECASE)
        # Remove javascript: protocol
        cleaned = re.sub(r'javascript:', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
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
