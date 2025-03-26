import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class ConfigEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("HSQLDB Config Editor")
        self.root.geometry("800x400")
        
        # Style
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Arial', 10))
        style.configure("TEntry", padding=5)
        style.configure("TButton", padding=5)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Config file path
        self.config_file = "hsqldb_config.json"
        self.config_data = self.load_config()
        
        # Create entry fields
        self.entries = {}
        
        # JDBC Driver
        ttk.Label(main_frame, text="JDBC Driver:").grid(row=0, column=0, sticky=tk.W)
        self.entries["JDBC_DRIVER"] = ttk.Entry(main_frame, width=60)
        self.entries["JDBC_DRIVER"].grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # JDBC URL
        ttk.Label(main_frame, text="JDBC URL:").grid(row=1, column=0, sticky=tk.W)
        self.entries["JDBC_URL"] = ttk.Entry(main_frame, width=60)
        self.entries["JDBC_URL"].grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=2, column=0, sticky=tk.W)
        self.entries["USERNAME"] = ttk.Entry(main_frame, width=60)
        self.entries["USERNAME"].grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Password
        ttk.Label(main_frame, text="Password:").grid(row=3, column=0, sticky=tk.W)
        self.entries["PASSWORD"] = ttk.Entry(main_frame, width=60, show="*")
        self.entries["PASSWORD"].grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # JAR File
        ttk.Label(main_frame, text="JAR File:").grid(row=4, column=0, sticky=tk.W)
        self.entries["JAR_FILE"] = ttk.Entry(main_frame, width=60)
        self.entries["JAR_FILE"].grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Save button
        save_btn = ttk.Button(button_frame, text="Save", command=self.save_config)
        save_btn.grid(row=0, column=0, padx=5)
        
        # Reset button
        reset_btn = ttk.Button(button_frame, text="Reset", command=self.load_values)
        reset_btn.grid(row=0, column=1, padx=5)
        
        # Load initial values
        self.load_values()
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config file: {str(e)}")
            return {}
    
    def load_values(self):
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, self.config_data.get(key, ""))
    
    def save_config(self):
        try:
            # Get values from entries
            new_config = {}
            for key, entry in self.entries.items():
                new_config[key] = entry.get()
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(new_config, f, indent=2)
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")

def main():
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
