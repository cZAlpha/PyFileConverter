import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.font import Font
import ttkbootstrap as ttk
from PIL import Image  # For file conversion
import os  # For file accessing
# from ttkbootstrap.constants import *

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

        # Set the application icon
        self.root.iconphoto(False, tk.PhotoImage(file="assets/app_icon/png/pyfileconverter_icon.png"))

        # Create list for files
        self.selected_file_list = []

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
                             foreground=UI_COLORS['light'])
        self.style.map('Custom.TRadiobutton', background=[('active', UI_COLORS['primary'])])

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

        # # Dictionary to store delete buttons with their item IDs
        # self.delete_buttons = {}

        # Bind the resizing of the window and allat
        self.root.bind('<Configure>', self.on_configure)

    def create_main_widgets(self):
        # File conversion type options
        self.conversion_type_var = tk.StringVar(value="Select A Filetype")  # Default type

        # Create the title label and place it at the top center
        ttk.Label(self.main_frame, text="PyFile Converter", font=self.custom_font_title).grid(row=0, column=1, pady=10,
                                                                                              padx=(0, 60), sticky="n")
        # Create a frame to house the clear all button
        top_left_frame = ttk.Frame(self.main_frame)
        top_left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Place the clear button
        clear_button = ttk.Button(top_left_frame, text="Clear All", command=self.clear_all_entries, style='danger', width=8)
        clear_button.pack(side=tk.RIGHT)

        # Create a frame to hold the settings button in the top-right corner
        top_right_frame = ttk.Frame(self.main_frame)
        top_right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        # Place the Settings button in the top-right frame using the custom style with larger font
        settings_button = ttk.Button(top_right_frame, text="⚙", command=self.show_settings, style='secondary')
        settings_button.pack(side=tk.RIGHT)

        # Create a frame to hold the import and convert buttons in the middle-rightmost sector
        middle_right_frame = ttk.Frame(self.main_frame)
        middle_right_frame.grid(row=1, column=2, padx=(0, 40), pady=10, sticky="ne")

        # Create the Import button
        import_button = ttk.Button(middle_right_frame, text="Import Files", command=self.on_convert,
                                   style='Custom.TButton')
        import_button.pack(side=tk.TOP, pady=10)

        # Create the Convert button
        convert_button = ttk.Button(middle_right_frame, text="Convert Files", command=lambda: self.convert_file(self.conversion_type_var.get()),
                                    style='Custom.TButton')
        convert_button.pack(side=tk.BOTTOM, pady=10)

        # Create the dropdown for filetype selection
        filetypes = ['.pdf', '.png', '.jpg']  # CHANGE THIS FOR MORE FILE TYPES
        self.filetype_dropdown = ttk.Combobox(middle_right_frame, textvariable=self.conversion_type_var, values=filetypes, state='readonly')
        self.filetype_dropdown.pack(side=tk.RIGHT, pady=5)

        # Create a frame for file listing
        self.file_list_frame = ttk.Frame(self.main_frame)
        self.file_list_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        # Create Treeview for file list
        self.file_list = ttk.Treeview(self.file_list_frame, columns=("No", "File Name", "Additional Info"),
                                      show="headings")
        self.file_list.heading("No", text="#", anchor="e")  # Number of files heading
        self.file_list.heading("File Name", text="File Name", anchor="w")  # File name heading
        self.file_list.heading("Additional Info", text="Output Filetype", anchor="w")  # Additional information heading
        self.file_list.column("No", width=10, anchor="e")  # Number of files column
        self.file_list.column("File Name", width=50, anchor="w")  # File name column
        self.file_list.column("Additional Info", width=50, anchor="w")  # Additional information column

        # Pack the Treeview with padding on the right side
        self.file_list.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)  # Add 20px padding on the right side

        # Configure grid column weights to ensure proper alignment
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=10)  # Skinny leftmost column
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
        if int(column) == 3:
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

        # Dark  mode button
        darkmodeButton = ttk.Button(self.settings_frame, text="Dark Mode", command=self.set_theme_dark, style='Custom.LargeTButton')
        darkmodeButton.pack(pady=5)
        # Light mode button
        lightmodeButton = ttk.Button(self.settings_frame, text="Light Mode", command=self.set_theme_light, style='Custom.LargeTButton')
        lightmodeButton.pack(pady=5)


        # BACK BUTTON
        ttk.Button(self.settings_frame, text="Back", command=self.back_to_main, style='Custom.TButton').pack(side=tk.TOP, padx=10, pady=10)
        # # APPLY BUTTON
        # ttk.Button(self.settings_frame, text="Apply", command=self.confirm_apply, style='Custom.TButton').pack(
        #     side=tk.TOP, padx=10, pady=10)


        # Initially hide the settings frame
        self.settings_frame.pack_forget()

    def show_settings(self):
        self.main_frame.pack_forget()
        self.settings_frame.pack(fill=tk.BOTH, expand=True)

    def show_main(self):
        self.settings_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def set_theme(self, theme_name):
        print("Theme change: " + str(theme_name))
        self.style.theme_use(theme_name)
        self.current_theme = theme_name

    def set_theme_light(self):
        print("Changed to light theme")
        self.set_theme('united')
        self.current_theme = 'united'

    def set_theme_dark(self):
        print("Changed to dark theme")
        self.set_theme('darkly')
        self.current_theme = 'darkly'

    def back_to_main(self):
        print("Going back to the main menu")
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

    def getFileName(self, str=""):
        if str == "":
            print("ERROR: Input string empty")
            return
        else:
            slashIndexList = []  # List to hold the indeces of the slashes within the input filepath string
            index = 0  # Index counter for iteration
            for char in str:
                if char == "/":
                    slashIndexList.append(index)
                else:
                    pass
                index += 1
            if slashIndexList != []:  # If the slash list ain't empty
                lastSlash = slashIndexList[-1]
                returnStr = str[lastSlash + 1:]
                return returnStr

    def on_convert(self):  # THIS FUNCTION DOES NOT CONVERT ANYTHING BUT RATHER HANDLES FILE SELECTION!!!
        # Obtain the currently selected files from the user
        files = self.select_files()

        for file in files:  # Save it to the list!
            self.selected_file_list.append(file)

        # String cut the filepath to only include the filename and the file extensions

        if ( len(files) > 10 ):
            messagebox.showwarning("Too Many Files Selected", "Please select no more than 10 files.")
            return

        if not files:
            messagebox.showwarning("No files selected", "Please select at least one file.")
            return

        conversion_type = self.conversion_type_var.get()
        if not conversion_type:
            messagebox.showwarning("No conversion type", "Please select a conversion type.")
            return

        results = {file: self.convert_file_type(file, conversion_type) for file in files}

        # Clear existing entries in the Treeview
        for item in self.file_list.get_children():
            self.file_list.delete(item)

        # DELETE ALL DELETE BUTTONS BC THIS PROCESS DELETES ALL PREVIOUS ENTRIES INTO THE TABLE/LIST
        # Remove the delete buttons
        # listOfDeleteButtonIDs = []
        # for item_id in self.delete_buttons:
        #     print("Delete Button ID:", item_id, "will be destroyed...")
        #     listOfDeleteButtonIDs.append(item_id)  # Append the current item ID into the list that contains which buttons to delete
        # for deleteButton in listOfDeleteButtonIDs:
        #     self.delete_buttons[deleteButton].destroy()
        #     del self.delete_buttons[deleteButton]

        # Add new entries to the Treeview
        for idx, (file, new_file) in enumerate(results.items(), start=1):  # VERY IMPORTANT: THE LOOP THAT POPULATES THE TABLE IN THE UI
            item_id = self.file_list.insert("", "end", values=(idx, self.getFileName(file), "Select Filetype"))

            # # Add a delete button aligned with the row
            # self.create_delete_button(item_id)

    def clear_all_entries(self):
        for item in self.file_list.get_children():  # Deletes it out of the UI
            self.file_list.delete(item)

        # Delete the internal selected file list to fully clear everything
        self.selected_file_list = []

    def on_configure(self, event):
        self.root.update_idletasks()
        self.root_x = self.root.winfo_rootx()
        self.root_y = self.root.winfo_rooty()
        # print(f"Window moved. New root position: ({self.root_x}, {self.root_y})")

    def convert_file(self, conversion_extension):
        print("SELECTED FILETYPE:", conversion_extension)
        valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.txt']

        if conversion_extension not in valid_extensions:  # Ensure that the inputted new file extension type is valid
            print("ERROR: Invalid conversion extension")
            messagebox.showwarning("No files selected", "Please select at least one file.")
            return  # STOPS function progression if error is detected

        files_to_be_converted = []
        for file in self.selected_file_list:  # Append the files that were previously selected to add them to the list
            try:
                files_to_be_converted.append(file)
            except Exception as e:
                print(f"An error occurred: {e}")

        for file in files_to_be_converted:  # Convert the files
            img = Image.open(file)  # Open the file in question
            output_file = os.path.splitext(file)[0] + conversion_extension  # Splits the filepath into a tuple where the left side is the filepath and the right side is the file extension
            img.save(output_file, conversion_extension.replace(".", "").upper() )  # Saves the new converted image with the name and extension selected by the user
            print(f"Successfully converted {file} to {output_file}")  # Prints that shit to the console rs type shit



if __name__ == "__main__":
    root = ttk.Window(title="Pyfile Converter", themename="united")  # Set initial theme
    root.geometry("700x300")  # Set window size
    app = FileConverterApp(root)
    root.mainloop()
