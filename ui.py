import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.font import Font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Centralized UI color variables
UI_COLORS = {
    'primary': '#f78b6f',  # Bootstrap primary color
    'secondary': '#f25f4c',  # Bootstrap secondary color
    'success': '#28a745',  # Bootstrap success color
    'danger': '#dc3545',  # Bootstrap danger color
    'warning': '#ffc107',  # Bootstrap warning color
    'info': '#17a2b8',  # Bootstrap info color
    'light': '#f8f9fa',  # Bootstrap light color
    'dark': '#343a40'  # Bootstrap dark color
}


class FileConverterApp:
    def __init__(self, root):
        self.root = root
        self.current_theme = "united"  # Default theme

        # Initialize the style
        self.style = ttk.Style()

        # Define a font
        self.custom_font = Font(family="Miracode", size=12)  # Customize as needed
        self.custom_font_title = Font(family="Miracode", size=16)  # Customize as needed

        # Define styles for buttons and radiobuttons
        self.style.configure('Custom.TButton', font=self.custom_font, background=UI_COLORS['primary'],
                             foreground=UI_COLORS['light'])
        self.style.map('Custom.TButton', background=[('active', UI_COLORS['secondary'])])

        self.style.configure('Custom.TRadiobutton', font=self.custom_font, background=UI_COLORS['light'],
                             foreground=UI_COLORS['dark'])
        self.style.map('Custom.TRadiobutton', background=[('active', UI_COLORS['light'])])

        # Define a custom style for settings button with larger font size
        self.style.configure('Large.TButton', font=('Miracode', 18), background=UI_COLORS['primary'],
                             foreground=UI_COLORS['light'])
        self.style.map('Large.TButton', background=[('active', UI_COLORS['secondary'])])

        # Create main and settings frames
        self.main_frame = ttk.Frame(root)
        self.settings_frame = ttk.Frame(root)

        # Pack main frame and initialize settings frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.settings_frame.pack(fill=tk.BOTH, expand=True)

        # Create widgets for the main frame
        self.create_main_widgets()

        # Create widgets for the settings frame
        self.create_settings_widgets()

        # Set initial theme
        self.set_theme(self.current_theme)

    def create_main_widgets(self):
        # File conversion type options
        self.conversion_type_var = tk.StringVar(value="txt")  # Default type

        # Create the title label and place it at the top center
        ttk.Label(self.main_frame, text="PyFile Converter", font=self.custom_font_title).grid(row=0, column=1, pady=10,
                                                                                              padx=10, sticky="n")

        # Create the Import button and place it in the center row
        import_button = ttk.Button(self.main_frame, text="Import Files and Convert", command=self.on_convert,
                                   style='Custom.TButton')
        import_button.grid(row=1, column=1, pady=20, padx=10)

        # Create a frame to hold the settings button in the top-right corner
        top_right_frame = ttk.Frame(self.main_frame)
        top_right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        # Place the Settings button in the top-right frame using the custom style with larger font
        settings_button = ttk.Button(top_right_frame, text="⚙", command=self.show_settings,
                                     style='Large.TButton')
        settings_button.pack(side=tk.RIGHT)

        # Create a frame for file listing
        self.file_list_frame = ttk.Frame(self.main_frame)
        self.file_list_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")

        # Create Treeview for file list
        self.file_list = ttk.Treeview(self.file_list_frame, columns=("Delete", "No", "File Name", "Additional Info"),
                                      show="headings")
        self.file_list.heading("Delete", text="", anchor="w")  # Empty heading for delete column
        self.file_list.heading("No", text="No", anchor="w")
        self.file_list.heading("File Name", text="File Name", anchor="w")
        self.file_list.heading("Additional Info", text="Additional Info", anchor="w")
        self.file_list.column("Delete", width=50, anchor="center")  # Adjust width as needed
        self.file_list.column("No", width=50, anchor="e")  # Shorten width of "No" column
        self.file_list.column("File Name", width=300, anchor="w")  # Adjust width of "File Name" column
        self.file_list.column("Additional Info", width=200, anchor="w")  # New column for additional info

        # Pack the Treeview with padding on the right side
        self.file_list.pack(expand=True, fill=tk.BOTH, padx=(0, 20))  # Add 20px padding on the right side

        # Configure grid column weights to ensure proper alignment
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)  # Center column gets more weight
        self.main_frame.grid_columnconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Ensure the file list expands

        # Bind the Treeview select event to start editing
        self.file_list.bind("<Double-1>", self.on_item_double_click)

    def on_item_double_click(self, event):
        item = self.file_list.selection()
        if not item:
            return

        column = self.file_list.identify_column(event.x)
        column = column.split('#')[1]

        # Adjust to handle the correct column, here we assume column 4 is "Additional Info"
        if int(column) == 4:
            self.start_editing(item[0], int(column))

    def start_editing(self, item_id, column):
        # Remove any existing Entry widget
        if hasattr(self, 'entry'):
            self.entry.destroy()

        # Get the coordinates where the click occurred
        x, y, width, height = self.file_list.bbox(item_id, column)

        # Create and place an Entry widget
        self.entry = tk.Entry(self.file_list_frame)
        self.entry.place(x=x + self.file_list_frame.winfo_rootx(), y=y + self.file_list_frame.winfo_rooty(),
                         width=width)

        # Set the current value in the Entry
        self.entry.insert(0, self.file_list.item(item_id, 'values')[column - 1])

        # Focus on the Entry widget and bind the return key to save the edit
        self.entry.focus_set()
        self.entry.bind('<Return>', lambda e: self.save_edit(item_id, column))

    def save_edit(self, item_id, column):
        # Save the new value and update the Treeview
        new_value = self.entry.get()
        self.file_list.item(item_id, values=self.update_item_values(item_id, column, new_value))
        self.entry.destroy()

    def update_item_values(self, item_id, column, new_value):
        values = list(self.file_list.item(item_id, 'values'))
        values[column - 1] = new_value
        return values

    def create_settings_widgets(self):
        # Widgets for settings
        ttk.Label(self.settings_frame, text="Select Theme:", font=self.custom_font_title).pack(pady=10)

        self.theme_var = tk.StringVar(value=self.current_theme)

        ttk.Radiobutton(self.settings_frame, text="Light Mode", variable=self.theme_var, value="united",
                        style='Custom.TRadiobutton').pack(pady=5)
        ttk.Radiobutton(self.settings_frame, text="Dark Mode", variable=self.theme_var, value="darkly",
                        style='Custom.TRadiobutton').pack(pady=5)

        ttk.Button(self.settings_frame, text="Apply", command=self.confirm_apply, style='Custom.TButton').pack(
            side=tk.LEFT, padx=10, pady=10)
        ttk.Button(self.settings_frame, text="Back", command=self.confirm_back, style='Custom.TButton').pack(
            side=tk.RIGHT, padx=10, pady=10)

        # Initially hide the settings frame
        self.settings_frame.pack_forget()

    def show_settings(self):
        self.main_frame.pack_forget()
        self.settings_frame.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()  # Ensure UI updates immediately

    def show_main(self):
        self.settings_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()  # Ensure UI updates immediately

    def set_theme(self, theme_name):
        # Set theme for the ttkbootstrap window
        self.style.theme_use(theme_name)
        self.current_theme = theme_name

    def confirm_apply(self):
        if messagebox.askyesno("Confirm Apply", "Are you sure you want to apply these changes?"):
            self.set_theme(self.theme_var.get())
            self.show_main()

    def confirm_back(self):
        if messagebox.askyesno("Confirm Back", "Are you sure you want to go back without applying changes?"):
            self.show_main()

    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title='Select files to import',
            filetypes=[('All Files', '*.*')]
        )
        return file_paths

    def convert_file_type(self, file_path, new_extension):
        # Simulate file conversion process (for demo purposes)
        return f"{file_path}.{new_extension}"

    def on_convert(self):
        files = self.select_files()
        if not files:
            messagebox.showwarning("No files selected", "Please select at least one file.")
            return

        conversion_type = self.conversion_type_var.get()
        if not conversion_type:
            messagebox.showwarning("No conversion type", "Please select a conversion type.")
            return

        results = {file: self.convert_file_type(file, conversion_type) for file in files}

        # Clear existing entries in the Treeview ( NOT NECESSARY
        for item in self.file_list.get_children():
            self.file_list.delete(item)

        # Add new entries to the Treeview
        for idx, (file, new_file) in enumerate(results.items(), start=1):
            item_id = self.file_list.insert("", "end", values=("", idx, file, f"Converted to {new_file}"))
            print("Item ID:", item_id[-3:])
            print(int(item_id[-3:]) * 10)

            # Add a delete button aligned with the row
            self.create_delete_button(item_id)

    def create_delete_button(self, item_id):
        # Ensure delete button is correctly placed in the "Delete" column
        x, y, width, height = self.file_list.bbox(item_id, "Delete")

        # Remove any existing delete button
        if hasattr(self, 'delete_button'):
            self.delete_button.destroy()

        # Create a Canvas to draw a rounded button
        canvas = tk.Canvas(self.file_list_frame, width=width, height=height, bd=0, highlightthickness=0)
        canvas.place(x=x + self.file_list_frame.winfo_rootx(), y=y + self.file_list_frame.winfo_rooty())

        # Draw a rounded rectangle (the delete button)
        radius = 10  # Radius for the rounded corners
        canvas.create_arc((0, 0, 2 * radius, 2 * radius), start=0, extent=90, fill=UI_COLORS['danger'], outline='')
        canvas.create_arc((width - 2 * radius, 0, width, 2 * radius), start=90, extent=90, fill=UI_COLORS['danger'],
                          outline='')
        canvas.create_arc((0, height - 2 * radius, 2 * radius, height), start=270, extent=90, fill=UI_COLORS['danger'],
                          outline='')
        canvas.create_arc((width - 2 * radius, height - 2 * radius, width, height), start=180, extent=90,
                          fill=UI_COLORS['danger'], outline='')

        canvas.create_rectangle((radius, 0, width - radius, height), fill=UI_COLORS['danger'], outline='')
        canvas.create_rectangle((0, radius, width, height - radius), fill=UI_COLORS['danger'], outline='')

        # Draw the "X" text on the rounded rectangle
        canvas.create_text(width / 2, height / 2, text="X", fill=UI_COLORS['light'], font=('Arial', 10, 'bold'))

        # Bind the canvas click event to delete the row
        canvas.bind("<Button-1>", lambda e: self.delete_row(item_id))

        # Store reference to the canvas if needed for future updates
        self.delete_button = canvas

    def delete_row(self, item_id):
        # Remove the delete button
        if hasattr(self, 'delete_button'):
            self.delete_button.destroy()

        # Remove the selected row
        self.file_list.delete(item_id)


if __name__ == "__main__":
    root = ttk.Window(themename="united")  # Set initial theme
    root.geometry("800x600")  # Set window size
    app = FileConverterApp(root)
    root.mainloop()
