import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, UnidentifiedImageError # Import UnidentifiedImageError
import pandas as pd
import os # Import os for path manipulation

# Import your updated backend file
import backend

class DataAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyzer")
        self.root.geometry("1400x850")
        self.root.minsize(width=1000, height=700)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Initialize the DataAnalyzer from backend3
        self.data_analyzer = backend.DataAnalyzer()
        self.df = None

        # Attributes for plot display
        self.current_plot_images = []
        self.plot_display_frame = None

        self.entries = {}
        self.file_path = ctk.StringVar(value="No file selected")
        self.data_source = ctk.StringVar(value="--- Select Source ---")

        # New StringVars for multilingual support
        self.input_language_var = ctk.StringVar(value="English")
        self.output_language_var = ctk.StringVar(value="English")

        self.tabview = None
        self.loading_label_data_load = None
        self.loading_label_summary = None
        self.loading_label_analysis = None
        self.submit_source_button = None
        self.connect_load_button = None
        self.summarize_button = None
        self.analyze_button = None
        self.summary_output_textbox = None
        self.result_label = None
        self.prompt_entry = None
        self.input_section = None
        self.input_section_placeholder_label = None
        # self.data_preview_label = None # This label is now completely removed

        self.copy_analysis_button = None
        self.copy_summary_button = None

        # Multilingual specific widgets
        self.input_text_box = None
        self.output_text_box = None
        self.translate_button = None
        self.reset_languages_button = None
        self.translation_loading_label = None

        # Placeholder flags for textboxes
        self.input_text_box_placeholder_active = True
        self.output_text_box_placeholder_active = True


        # Load icons for tabs at initialization
        self.icon_data_connection = self.load_icon("data_connection_icon.png", (24, 24))
        self.icon_summarize_data = self.load_icon("summarize_data_icon.png", (24, 24))
        self.icon_analyze_data = self.load_icon("analyze_data_icon.png", (24, 24))
        self.icon_multilingual = self.load_icon("multilingual_icon.png", (24, 24)) # New icon for multilingual tab
        self.icon_file_upload = self.load_icon("upload_icon.png", (20, 20))
        self.icon_database = self.load_icon("database_icon.png", (20, 20))
        self.icon_sharepoint = self.load_icon("sharepoint_icon.png", (20, 20))
        self.icon_reset = self.load_icon("reset_icon.png", (20, 20))
        self.icon_summarize_dataset = self.load_icon("summarize_icon.png", (20, 20))
        self.data_connection_tab_icon = self.load_icon("database_icon_large.png", (200, 200))
        self.summary_feature_image = self.load_icon("summary_feature_image.png", (300, 200))
        self.icon_copy = self.load_icon("copy_icon.png", (20, 20))

        self.build_main_layout()

    def load_icon(self, path, size):
        """Helper to load and resize images for icons."""
        try:
            img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except (FileNotFoundError, UnidentifiedImageError) as e: # Catch both errors
            print(f"Warning: {path} not found or cannot be identified ({e}). Icon will not be displayed, using placeholder.")
            # Create a simple placeholder image if the file is not found or corrupted
            placeholder_img = Image.new('RGB', size, color = 'grey')
            return ctk.CTkImage(light_image=placeholder_img, dark_image=placeholder_img, size=size)


    def build_main_layout(self):
        # Reset internal state variables
        self.data_analyzer = backend.DataAnalyzer()
        self.df = None
        self.entries = {}
        self.file_path.set("No file selected")
        self.data_source.set("--- Select Source ---")
        self.current_plot_images = []

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(fg_color="#4B0082")

        self.main_container_frame = ctk.CTkFrame(self.root, fg_color="#4B0082", corner_radius=0)
        self.main_container_frame.pack(fill="both", expand=True)

        self.main_container_frame.grid_columnconfigure(0, weight=0)
        self.main_container_frame.grid_columnconfigure(1, weight=1)
        self.main_container_frame.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self.main_container_frame,
                                          width=280,
                                          corner_radius=0,
                                          fg_color="#3A2B5B")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.main_content_scroll_frame = ctk.CTkScrollableFrame(self.main_container_frame,
                                                                 corner_radius=0,
                                                                 fg_color="#5D40A4",
                                                                 scrollbar_button_color="#7B68EE",
                                                                 scrollbar_button_hover_color="#9B7AEF")
        self.main_content_scroll_frame.grid(row=0, column=1, sticky="nsew")

        self.main_content_frame = ctk.CTkFrame(self.main_content_scroll_frame,
                                               corner_radius=0,
                                               fg_color="#5D40A4")
        self.main_content_frame.pack(fill="both", expand=True)

        self.sidebar_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 9, 10), weight=0)
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        current_row = 0

        try:
            app_icon_img = Image.open("icon_app_analyzer.png").resize((50, 50), Image.Resampling.LANCZOS)
            self.app_icon_ctk = ctk.CTkImage(light_image=app_icon_img, dark_image=app_icon_img, size=(50, 50))
            ctk.CTkLabel(self.sidebar_frame, text="", image=self.app_icon_ctk).grid(row=current_row, column=0, padx=20, pady=(30, 5), sticky="nw")
        except FileNotFoundError:
            ctk.CTkLabel(self.sidebar_frame, text="📊", font=("Arial", 24), text_color="white").grid(row=current_row, column=0, padx=20, pady=(30, 5), sticky="nw")
            print("Warning: icon_app_analyzer.png not found. Showing text placeholder.")

        ctk.CTkLabel(self.sidebar_frame, text="Data Analyzer",
                     font=("Arial", 30, "bold"), text_color="white").grid(row=current_row, column=1, padx=(0, 20), pady=(30, 5), sticky="nw")
        current_row += 1

        self.sidebar_frame.grid_columnconfigure(0, weight=0)
        self.sidebar_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="✨ AI-Powered",
                     font=("Arial", 18), text_color="#A9A9A9").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(0, 30), sticky="w")
        current_row += 1

        ctk.CTkLabel(self.sidebar_frame, text="Your Personal Assistant in the Digital Realm",
                     font=("Arial", 20, "bold"), text_color="white", wraplength=240, justify="left").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")
        current_row += 1

        ctk.CTkLabel(self.sidebar_frame, text="Connect, analyze, and discover insights from your data with the power of artificial intelligence.",
                     font=("Arial", 16), text_color="#D3D3D3", wraplength=240, justify="left").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="w")
        current_row += 1

        ctk.CTkLabel(self.sidebar_frame, text="Key Features",
                     font=("Arial", 25, "bold"), text_color="white").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(40, 10), sticky="w")
        current_row += 1

        def create_feature_item(parent, icon_ctk_image, title, description, row_num):
            item_frame = ctk.CTkFrame(parent, fg_color="transparent")
            item_frame.grid(row=row_num, column=0, columnspan=2, sticky="ew", padx=20, pady=8)
            item_frame.grid_columnconfigure(0, weight=0)
            item_frame.grid_columnconfigure(1, weight=1)

            if icon_ctk_image:
                ctk.CTkLabel(item_frame, text="", image=icon_ctk_image).grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="nw")
            else:
                ctk.CTkLabel(item_frame, text="•", font=("Arial", 25), text_color="#87CEEB").grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="nw")

            ctk.CTkLabel(item_frame, text=title, font=("Arial", 20, "bold"), text_color="white", anchor="w").grid(row=0, column=1, sticky="ew")
            ctk.CTkLabel(item_frame, text=description, font=("Arial", 14), text_color="#D3D3D3", wraplength=180, justify="left", anchor="w").grid(row=1, column=1, sticky="ew")

            return item_frame

        create_feature_item(self.sidebar_frame, self.load_icon("icon_multi_source.png", (30, 30)),
                            "Multi-Source Connection", "Excel, SQL, SharePoint", current_row)
        current_row += 1

        create_feature_item(self.sidebar_frame, self.load_icon("icon_summarization.png", (30, 30)),
                            "Smart Summarization", "Instant data insights", current_row)
        current_row += 1

        create_feature_item(self.sidebar_frame, self.load_icon("icon_ai_analysis.png", (30, 30)),
                            "AI Analysis", "Natural language queries", current_row)
        current_row += 1

        create_feature_item(self.sidebar_frame, self.icon_multilingual,
                            "Multilingual Support", "Input/output in multiple languages", current_row)
        current_row += 1


        self.sidebar_frame.grid_rowconfigure(current_row, weight=1)
        current_row += 1

        self.reset_button = ctk.CTkButton(self.sidebar_frame,
                                          text="Reset Application",
                                          command=self.reset_application,
                                          font=("Arial", 18, "bold"),
                                          fg_color="#8B0000",
                                          hover_color="#DC143C",
                                          height=45,
                                          image=self.icon_reset,
                                          compound="left",
                                          anchor="center")
        self.reset_button.grid(row=current_row, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        current_row += 1

        try:
            bottom_image_path = "org_logo.png"
            bottom_img = Image.open(bottom_image_path).resize((300, 80), Image.Resampling.LANCZOS)
            self.bottom_img_ctk = ctk.CTkImage(light_image=bottom_img, dark_image=bottom_img, size=(300, 80))
            ctk.CTkLabel(self.sidebar_frame, text="", image=self.bottom_img_ctk).grid(row=current_row, column=0, columnspan=2, pady=(20, 20), sticky="s")
        except FileNotFoundError:
            ctk.CTkLabel(self.sidebar_frame, text="[Your Organization Logo]", font=("Arial", 14), text_color="#D3D3D3").grid(row=current_row, column=0, columnspan=2, pady=(20, 20), sticky="s")
            print(f"Warning: {bottom_image_path} not found. Showing text placeholder.")


        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=0)
        self.main_content_frame.grid_rowconfigure(1, weight=0)
        self.main_content_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self.main_content_frame, text="🚀 Data Analyzer",
                     font=("Arial", 30, "bold"), text_color="white", anchor="w").grid(row=0, column=0, padx=40, pady=(30, 10), sticky="ew")

        ctk.CTkFrame(self.main_content_frame, height=2, fg_color="#7B68EE", corner_radius=0).grid(row=1, column=0, padx=30, pady=(0, 20), sticky="ew")


        self.tabview = ctk.CTkTabview(self.main_content_frame,
                                       fg_color="#4B0082",
                                       segmented_button_fg_color="#3A2B5B",
                                       segmented_button_selected_color="#6A5ACD",
                                       segmented_button_selected_hover_color="#7B68EE",
                                       segmented_button_unselected_color="#3A2B5B",
                                       segmented_button_unselected_hover_color="#5D40A4",
                                       text_color="white",
                                       width=1100,
                                       height=700,
                                       corner_radius=10,
                                       border_width=2,
                                       border_color="#7B68EE"
                                      )
        self.tabview.grid(row=2, column=0, padx=30, pady=(0, 30), sticky="nsew")

        if hasattr(self.tabview, '_segmented_button'):
            self.tabview._segmented_button.configure(font=("Arial", 20, "bold"))

        tab_data = [
            ("1. Data Connection", self.icon_data_connection),
            ("2. Summarize Data", self.icon_summarize_data),
            ("3. Analyze Data", self.icon_analyze_data),
            ("4. Multilingual Support", self.icon_multilingual)
        ]

        for text, icon in tab_data:
            tab = self.tabview.add(text)
            if hasattr(self.tabview, '_segmented_button'):
                for child in self.tabview._segmented_button.winfo_children():
                    if isinstance(child, ctk.CTkButton) and child.cget("text") == text:
                        if icon:
                            child.configure(image=icon, compound="left")
                        child.configure(command=lambda t=text: self.on_tab_select(t))
                        break

        self.tabview.set("1. Data Connection")

        self.build_data_connection_tab()
        self.build_summarize_data_tab()
        self.build_analyze_data_tab()
        self.build_multilingual_support_tab()
        self.root.after(100, self.update_summary_tab_state)

    def on_tab_select(self, tab_name):
        """Handles tab selection and ensures correct tab is displayed."""
        self.tabview.set(tab_name)

    def clear_frame_widgets(self, frame):
        """Helper method to destroy all widgets within a given frame."""
        for widget in frame.winfo_children():
            widget.destroy()

    def build_data_connection_tab(self):
        """Builds the content for the '1. Data Connection' tab."""
        tab = self.tabview.tab("1. Data Connection")
        self.clear_frame_widgets(tab)

        tab.grid_columnconfigure(0, weight=1)
        # Configure rows for layout
        tab.grid_rowconfigure(0, weight=0) # For icon
        tab.grid_rowconfigure(1, weight=0) # For title
        tab.grid_rowconfigure(2, weight=0) # For "Select Data Source" label
        tab.grid_rowconfigure(3, weight=0) # For data source option menu
        tab.grid_rowconfigure(4, weight=0) # For submit source button
        tab.grid_rowconfigure(5, weight=1) # For input_section (expandable)
        tab.grid_rowconfigure(6, weight=0) # For Connect & Load Data button
        tab.grid_rowconfigure(7, weight=0) # For loading label
        tab.grid_rowconfigure(8, weight=1) # For extra space at the bottom

        current_row = 0

        if self.data_connection_tab_icon:
            ctk.CTkLabel(tab, text="", image=self.data_connection_tab_icon).grid(row=current_row, column=0, pady=(30, 10))
        else:
            ctk.CTkLabel(tab, text="🗄️", font=("Arial", 100), text_color="#ADFF2F").grid(row=current_row, column=0, pady=(30, 10))
        current_row += 1

        ctk.CTkLabel(tab, text="Establish Your Data Connection",
                     font=("Arial", 26, "bold"), text_color="white").grid(row=current_row, column=0, pady=(15, 15))
        current_row += 1

        ctk.CTkLabel(tab, text="Select Data Source:", font=("Arial", 18, "bold"), text_color="#D3D3D3").grid(row=current_row, column=0, pady=(10, 5), sticky="w", padx=50)
        current_row += 1

        self.data_source_optionmenu = ctk.CTkOptionMenu(tab,
                                                        values=["--- Select Source ---", "CSV/Excel File", "Database (SQL)", "SharePoint List"],
                                                        variable=self.data_source,
                                                        command=self.on_data_source_select,
                                                        font=("Arial", 16),
                                                        dropdown_font=("Arial", 16),
                                                        width=300,
                                                        height=40,
                                                        fg_color="#6A5ACD",
                                                        button_color="#5D40A4",
                                                        button_hover_color="#7B68EE",
                                                        text_color="white",
                                                        dropdown_fg_color="#4B0082",
                                                        dropdown_hover_color="#5D40A4",
                                                        dropdown_text_color="white"
                                                       )
        self.data_source_optionmenu.grid(row=current_row, column=0, pady=(0, 20), sticky="ew", padx=50)
        current_row += 1

        self.submit_source_button = ctk.CTkButton(tab,
                                                  text="Submit Source Type",
                                                  command=self.show_source_input_fields,
                                                  font=("Arial", 18, "bold"),
                                                  fg_color="#6A5ACD",
                                                  hover_color="#7B68EE",
                                                  height=45,
                                                  state="disabled" if self.data_source.get() == "--- Select Source ---" else "normal"
                                                  )
        self.submit_source_button.grid(row=current_row, column=0, pady=(0, 20), sticky="ew", padx=50)
        current_row += 1

        self.input_section = ctk.CTkFrame(tab, fg_color="transparent")
        self.input_section.grid(row=5, column=0, pady=10, sticky="nsew", padx=50)
        self.input_section.grid_columnconfigure(0, weight=1)
        self.input_section.grid_rowconfigure(0, weight=1)

        self.input_section_placeholder_label = ctk.CTkLabel(self.input_section,
                                                            text="Click 'Submit Source Type' to see connection fields.",
                                                            font=("Arial", 16), text_color="#A9A9A9")
        self.input_section_placeholder_label.grid(row=0, column=0, pady=50, sticky="nsew")

        self.connect_load_button = ctk.CTkButton(tab,
                                                 text="Connect & Load Data",
                                                 command=self.load_data,
                                                 font=("Arial", 20, "bold"),
                                                 fg_color="#6A5ACD",
                                                 hover_color="#7B68EE",
                                                 height=50)
        self.loading_label_data_load = ctk.CTkLabel(tab, text="", font=("Arial", 16), text_color="#ADFF2F")


    def on_data_source_select(self, choice):
        """Handles the selection of a data source from the OptionMenu."""
        self.clear_frame_widgets(self.input_section)
        if choice == "--- Select Source ---":
            self.submit_source_button.configure(state="disabled")
            self.input_section_placeholder_label = ctk.CTkLabel(self.input_section,
                                                                text="Click 'Submit Source Type' to see connection fields.",
                                                                font=("Arial", 16), text_color="#A9A9A9")
            self.input_section_placeholder_label.grid(row=0, column=0, pady=50, sticky="nsew")
            self.connect_load_button.grid_forget()
            self.loading_label_data_load.grid_forget()
        else:
            self.submit_source_button.configure(state="normal")
            self.input_section_placeholder_label = ctk.CTkLabel(self.input_section,
                                                                text=f"Selected {choice}. Click 'Submit Source Type' to configure.",
                                                                font=("Arial", 16), text_color="#A9A9A9")
            self.input_section_placeholder_label.grid(row=0, column=0, pady=50, sticky="nsew")
            self.connect_load_button.grid_forget()
            self.loading_label_data_load.grid_forget()
        self.root.update_idletasks()


    def show_source_input_fields(self):
        """Displays the appropriate input fields based on the selected data source."""
        choice = self.data_source.get()
        self.clear_frame_widgets(self.input_section)
        self.entries = {}

        self.input_section.grid_columnconfigure(0, weight=1)
        self.input_section.grid_columnconfigure(1, weight=0)
        for i in range(6):
            self.input_section.grid_rowconfigure(i, weight=0)
        self.input_section.grid_rowconfigure(6, weight=1)

        if choice == "CSV/Excel File":
            self.build_file_input_fields()
        elif choice == "Database (SQL)":
            self.build_database_input_fields()
        elif choice == "SharePoint List":
            self.build_sharepoint_input_fields()
        else:
            self.input_section_placeholder_label = ctk.CTkLabel(self.input_section,
                                                                text="Please select a data source to continue.",
                                                                font=("Arial", 16), text_color="#A9A9A9")
            self.input_section_placeholder_label.grid(row=0, column=0, pady=50, sticky="nsew")
            self.connect_load_button.configure(state="disabled")
            return

        tab = self.tabview.tab("1. Data Connection")
        self.connect_load_button.grid(row=6, column=0, pady=(20, 10), sticky="ew", padx=50)
        self.connect_load_button.configure(state="normal")
        self.loading_label_data_load.grid(row=7, column=0, pady=(0, 10), padx=50)
        self.root.update_idletasks()


    def build_file_input_fields(self):
        """Builds input fields for CSV/Excel file selection."""
        self.input_section.grid_columnconfigure(0, weight=1)
        self.input_section.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(self.input_section, text="File Path:", font=("Arial", 16), text_color="#D3D3D3").grid(row=0, column=0, sticky="w", pady=(10,5))
        self.file_path_entry = ctk.CTkEntry(self.input_section,
                                            textvariable=self.file_path,
                                            width=400,
                                            height=35,
                                            font=("Arial", 14),
                                            placeholder_text="e.g., /home/user/data.csv or C:/data/data.xlsx")
        self.file_path_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew", pady=(0,10))
        self.entries['file_path_entry'] = self.file_path_entry

        self.browse_button = ctk.CTkButton(self.input_section,
                                          text="Browse",
                                          command=self.browse_file,
                                          font=("Arial", 16),
                                          fg_color="#5D40A4",
                                          hover_color="#7B68EE",
                                          image=self.icon_file_upload,
                                          compound="left",
                                          height=35,
                                          width=100)
        self.browse_button.grid(row=1, column=1, sticky="w", pady=(0,10))

    def build_database_input_fields(self):
        """Builds input fields for database connection."""
        self.input_section.grid_columnconfigure(0, weight=0)
        self.input_section.grid_columnconfigure(1, weight=1)

        fields = [
            ("Dialect (e.g., postgresql, mysql, sqlite)", "dialect"),
            ("Host", "host"),
            ("Port", "port"),
            ("Database Name", "database_name"),
            ("Username", "username"),
            ("Password", "password")
        ]

        for i, (label_text, entry_key) in enumerate(fields):
            ctk.CTkLabel(self.input_section, text=f"{label_text}:", font=("Arial", 16), text_color="#D3D3D3").grid(row=i, column=0, sticky="w", pady=5, padx=(0,10))
            entry_widget = ctk.CTkEntry(self.input_section,
                                        width=400,
                                        height=35,
                                        font=("Arial", 14),
                                        placeholder_text=f"Enter {label_text.lower()}")
            if entry_key == "password":
                entry_widget.configure(show="*")
            entry_widget.grid(row=i, column=1, sticky="ew", pady=5)
            self.entries[entry_key] = entry_widget

        ctk.CTkLabel(self.input_section, text="Note: For security, sensitive information is not saved.",
                     font=("Arial", 12, "italic"), text_color="#A9A9A9").grid(row=len(fields), column=0, columnspan=2, pady=(10,0), sticky="w")


    def build_sharepoint_input_fields(self):
        """Builds input fields for SharePoint connection."""
        self.input_section.grid_columnconfigure(0, weight=0)
        self.input_section.grid_columnconfigure(1, weight=1)

        fields = [
            ("SharePoint Site URL", "site_url"),
            ("List Name", "list_name"),
            ("Client ID (Azure AD App)", "client_id"),
            ("Client Secret (Azure AD App)", "client_secret")
        ]

        for i, (label_text, entry_key) in enumerate(fields):
            ctk.CTkLabel(self.input_section, text=f"{label_text}:", font=("Arial", 16), text_color="#D3D3D3").grid(row=i, column=0, sticky="w", pady=5, padx=(0,10))
            entry_widget = ctk.CTkEntry(self.input_section,
                                        width=400,
                                        height=35,
                                        font=("Arial", 14),
                                        placeholder_text=f"Enter {label_text.lower()}")
            if entry_key == "client_secret":
                entry_widget.configure(show="*")
            entry_widget.grid(row=i, column=1, sticky="ew", pady=5)
            self.entries[entry_key] = entry_widget

        ctk.CTkLabel(self.input_section, text="Ensure your Azure AD App has 'Sites.Read.All' or similar permissions.",
                     font=("Arial", 12, "italic"), text_color="#A9A9A9", wraplength=450).grid(row=len(fields), column=0, columnspan=2, pady=(10,0), sticky="w")

    def browse_file(self):
        """Opens a file dialog for CSV/Excel file selection."""
        filetypes = [("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.file_path.set(path)
            self.loading_label_data_load.configure(text=f"Selected: {os.path.basename(path)}", text_color="#ADFF2F")
            if 'file_path_entry' in self.entries:
                self.entries['file_path_entry'].delete(0, ctk.END)
                self.entries['file_path_entry'].insert(0, path)
        else:
            self.loading_label_data_load.configure(text="File selection cancelled.", text_color="orange")

    def load_data(self):
        """Initiates data loading based on the selected source using DataAnalyzer."""
        current_source = self.data_source.get()
        self.loading_label_data_load.configure(text="Loading data...", text_color="yellow")
        self.df = None

        try:
            if current_source == "CSV/Excel File":
                file_path = self.file_path.get()
                if not file_path or file_path == "No file selected":
                    raise ValueError("Please select a file first.")
                self.df = self.data_analyzer.load_data("file", file_path=file_path)
                self.loading_label_data_load.configure(text=f"Data loaded successfully from {os.path.basename(file_path)}!", text_color="#ADFF2F")
                messagebox.showinfo("Success", f"Data loaded successfully from {os.path.basename(file_path)}!")

            elif current_source == "Database (SQL)":
                db_config = {key: self.entries[key].get() for key in ["dialect", "host", "port", "database_name", "username", "password"]}
                if not all(db_config.values()):
                    raise ValueError("Please fill all database fields.")
                dummy_sql_query = "SELECT * FROM some_default_table;"
                self.df = self.data_analyzer.load_data(
                    "sql",
                    dialect=db_config['dialect'],
                    username=db_config['username'],
                    password=db_config['password'],
                    host=db_config['host'],
                    port=db_config['port'],
                    database=db_config['database_name'],
                    sql_query=dummy_sql_query
                )
                self.loading_label_data_load.configure(text="Data loaded successfully from SQL database!", text_color="#ADFF2F")
                messagebox.showinfo("Success", "Data loaded successfully from SQL database!")

            elif current_source == "SharePoint List":
                sp_config = {key: self.entries[key].get() for key in ["site_url", "list_name", "client_id", "client_secret"]}
                if not all(sp_config.values()):
                    raise ValueError("Please fill all SharePoint fields.")
                self.df = self.data_analyzer.load_data(
                    "sharepoint",
                    site_url=sp_config['site_url'],
                    list_name=sp_config['list_name'],
                    client_id=sp_config['client_id'],
                    client_secret=sp_config['client_secret']
                )
                self.loading_label_data_load.configure(text="Data loaded successfully from SharePoint!", text_color="#ADFF2F")
                messagebox.showinfo("Success", "Data loaded successfully from SharePoint list!")

            else:
                raise ValueError("Please select a data source type from the dropdown.")

            self.tabview.set("2. Summarize Data")
            self.update_summary_tab_state()

        except Exception as e:
            self.df = None
            self.loading_label_data_load.configure(text=f"Error: {e}", text_color="red")
            messagebox.showerror("Loading Error", f"Failed to load data: {e}")
            self.update_summary_tab_state()

    def reset_application(self):
        """Resets the application to its initial state."""
        response = messagebox.askyesno("Reset Application", "Are you sure you want to reset the application? All loaded data will be cleared.")
        if response:
            self.build_main_layout()
            messagebox.showinfo("Reset", "Application has been reset.")

    def build_summarize_data_tab(self):
        """Builds the content for the '2. Summarize Data' tab."""
        tab = self.tabview.tab("2. Summarize Data")
        self.clear_frame_widgets(tab)

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=3)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tab, text="📊 Data Summary & Insights",
                     font=("Arial", 28, "bold"), text_color="white").grid(row=0, column=0, columnspan=2, pady=(30, 20), sticky="ew", padx=30)

        # Left Frame: Summary Controls
        left_frame = ctk.CTkFrame(tab, fg_color="#3A2B5B", corner_radius=10, border_width=2, border_color="#7B68EE")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(30, 15), pady=(0, 30))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure((0,1,2,3,4,5,6), weight=0)
        left_frame.grid_rowconfigure(7, weight=1)

        current_row_left = 0
        ctk.CTkLabel(left_frame, text="Generate Data Summary", font=("Arial", 22, "bold"), text_color="white").grid(row=current_row_left, column=0, pady=(20, 10))
        current_row_left += 1

        if self.summary_feature_image:
            ctk.CTkLabel(left_frame, text="", image=self.summary_feature_image).grid(row=current_row_left, column=0, pady=(10, 20))
        else:
            ctk.CTkLabel(left_frame, text="📈", font=("Arial", 80), text_color="#ADFF2F").grid(row=current_row_left, column=0, pady=(10, 20))
        current_row_left += 1

        ctk.CTkLabel(left_frame, text="Click below to get an AI-powered summary of your loaded dataset.",
                     font=("Arial", 16), text_color="#D3D3D3", wraplength=350, justify="center").grid(row=current_row_left, column=0, padx=20, pady=(0, 20))
        current_row_left += 1

        self.summarize_button = ctk.CTkButton(left_frame,
                                              text="Summarize Data",
                                              command=self.summarize_data,
                                              font=("Arial", 20, "bold"),
                                              fg_color="#6A5ACD",
                                              hover_color="#7B68EE",
                                              height=50,
                                              image=self.icon_summarize_dataset,
                                              compound="left",
                                              state="disabled" if self.df is None else "normal")
        self.summarize_button.grid(row=current_row_left, column=0, padx=30, pady=(0, 20), sticky="ew")
        current_row_left += 1

        self.loading_label_summary = ctk.CTkLabel(left_frame, text="", font=("Arial", 16), text_color="#ADFF2F")
        self.loading_label_summary.grid(row=current_row_left, column=0, pady=(0, 10))
        current_row_left += 1

        ctk.CTkLabel(left_frame, text="Quick Navigation:", font=("Arial", 18, "bold"), text_color="white").grid(row=current_row_left, column=0, pady=(30, 10), sticky="w", padx=30)
        current_row_left += 1

        data_conn_button = ctk.CTkButton(left_frame,
                                         text="Go to Data Connection",
                                         command=lambda: self.on_tab_select("1. Data Connection"),
                                         font=("Arial", 16),
                                         fg_color="#5D40A4",
                                         hover_color="#7B68EE",
                                         height=40,
                                         image=self.icon_data_connection,
                                         compound="left")
        data_conn_button.grid(row=current_row_left, column=0, padx=30, pady=(5, 5), sticky="ew")
        current_row_left += 1

        analyze_data_button = ctk.CTkButton(left_frame,
                                            text="Go to Analyze Data",
                                            command=lambda: self.on_tab_select("3. Analyze Data"),
                                            font=("Arial", 16),
                                            fg_color="#5D40A4",
                                            hover_color="#7B68EE",
                                            height=40,
                                            image=self.icon_analyze_data,
                                            compound="left",
                                            state="disabled" if self.df is None else "normal")
        analyze_data_button.grid(row=current_row_left, column=0, padx=30, pady=(5, 20), sticky="ew")
        current_row_left += 1

        # Right Frame: Summary Output and Plots
        right_frame = ctk.CTkFrame(tab, fg_color="#3A2B5B", corner_radius=10, border_width=2, border_color="#7B68EE")
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(15, 30), pady=(0, 30))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=0)
        right_frame.grid_rowconfigure(1, weight=2)
        right_frame.grid_rowconfigure(2, weight=0)
        right_frame.grid_rowconfigure(3, weight=3)

        ctk.CTkLabel(right_frame, text="AI Summary Results", font=("Arial", 22, "bold"), text_color="white").grid(row=0, column=0, pady=(20, 10))

        self.summary_output_textbox = ctk.CTkTextbox(right_frame,
                                                     wrap="word",
                                                     font=("Arial", 16),
                                                     text_color="white",
                                                     fg_color="#4B0082",
                                                     border_width=1,
                                                     border_color="#7B68EE",
                                                     corner_radius=5)
        self.summary_output_textbox.insert("0.0", "Your AI-powered data summary will appear here after loading data and clicking 'Summarize Data'.")
        self.summary_output_textbox.configure(state="disabled")
        self.summary_output_textbox.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self.copy_summary_button = ctk.CTkButton(right_frame,
                                                  text="Copy Summary",
                                                  command=self.copy_summary_to_clipboard,
                                                  font=("Arial", 16, "bold"),
                                                  fg_color="#5D40A4",
                                                  hover_color="#7B68EE",
                                                  height=40,
                                                  image=self.icon_copy,
                                                  compound="left",
                                                  state="disabled")
        self.copy_summary_button.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="e")

        self.plot_display_frame = ctk.CTkScrollableFrame(right_frame,
                                                         fg_color="#4B0082",
                                                         border_width=1,
                                                         border_color="#7B68EE",
                                                         corner_radius=5)
        self.plot_display_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.plot_display_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.plot_display_frame, text="Visualizations will appear here.",
                     font=("Arial", 16), text_color="#A9A9A9").pack(pady=50)


    def summarize_data(self):
        """Triggers the data summarization process using the DataAnalyzer."""
        if self.df is None:
            messagebox.showwarning("No Data", "Please load data first in the 'Data Connection' tab.")
            self.loading_label_summary.configure(text="No data loaded.", text_color="orange")
            return

        self.loading_label_summary.configure(text="Generating summary and plots...", text_color="yellow")
        self.summary_output_textbox.configure(state="normal")
        self.summary_output_textbox.delete("0.0", ctk.END)
        self.copy_summary_button.configure(state="disabled")
        self.clear_frame_widgets(self.plot_display_frame)
        self.current_plot_images = []

        try:
            summary_text, plot_paths = self.data_analyzer.get_data_summary()
            self.summary_output_textbox.insert("0.0", summary_text)
            self.loading_label_summary.configure(text="Summary generated successfully!", text_color="#ADFF2F")
            self.copy_summary_button.configure(state="normal")

            if plot_paths:
                self.display_plots(plot_paths)
            else:
                ctk.CTkLabel(self.plot_display_frame, text="No relevant plots generated for this dataset.",
                             font=("Arial", 16), text_color="#A9A9A9").pack(pady=20)

        except Exception as e:
            self.summary_output_textbox.insert("0.0", f"Error generating summary: {e}")
            self.loading_label_summary.configure(text=f"Error: {e}", text_color="red")
            ctk.CTkLabel(self.plot_display_frame, text=f"Error generating plots: {e}",
                         font=("Arial", 16), text_color="red").pack(pady=20)
        finally:
            self.summary_output_textbox.configure(state="disabled")
            self.update_summary_tab_state()

    def display_plots(self, plot_paths):
        """Displays generated plot images in the plot_display_frame."""
        self.clear_frame_widgets(self.plot_display_frame)
        self.current_plot_images = []

        if not plot_paths:
            ctk.CTkLabel(self.plot_display_frame, text="No plots to display.", font=("Arial", 16), text_color="#A9A9A9").pack(pady=20)
            return

        for i, plot_path in enumerate(plot_paths):
            try:
                img = Image.open(plot_path)
                self.plot_display_frame.update_idletasks()
                max_width = self.plot_display_frame.winfo_width() - 40
                max_height = 400

                img_width, img_height = img.size

                if img_width > max_width or img_height > max_height:
                    width_ratio = max_width / img_width
                    height_ratio = max_height / img_height
                    scale_factor = min(width_ratio, height_ratio)
                    new_width = int(img_width * scale_factor)
                    new_height = int(img_height * scale_factor)
                else:
                    new_width = img_width
                    new_height = img_height

                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(new_width, new_height))
                self.current_plot_images.append(ctk_img)

                plot_label = ctk.CTkLabel(self.plot_display_frame, text="", image=ctk_img)
                plot_label.pack(pady=10)
                ctk.CTkLabel(self.plot_display_frame, text=f"Plot {i+1}: {os.path.basename(plot_path)}",
                             font=("Arial", 14, "bold"), text_color="#D3D3D3").pack(pady=(0, 5))

            except FileNotFoundError:
                ctk.CTkLabel(self.plot_display_frame, text=f"Plot file not found: {os.path.basename(plot_path)}",
                             font=("Arial", 14), text_color="red").pack(pady=5)
            except Exception as e:
                ctk.CTkLabel(self.plot_display_frame, text=f"Error loading plot {os.path.basename(plot_path)}: {e}",
                             font=("Arial", 14), text_color="red").pack(pady=5)


    def copy_summary_to_clipboard(self):
        """Copies the content of the summary output textbox to the clipboard."""
        summary_text = self.summary_output_textbox.get("0.0", ctk.END).strip()
        if summary_text and summary_text != "Your AI-powered data summary will appear here after loading data and clicking 'Summarize Data'.":
            self.root.clipboard_clear()
            self.root.clipboard_append(summary_text)
            messagebox.showinfo("Copied", "Summary copied to clipboard!")
        else:
            messagebox.showwarning("No Summary", "There is no summary to copy yet.")

    def copy_analysis_to_clipboard(self):
        """Copies the content of the analysis output textbox to the clipboard."""
        analysis_text = self.result_label.get("0.0", ctk.END).strip()
        if analysis_text and analysis_text != "AI analysis results will appear here after you ask a question and click 'Analyze Data'.":
            self.root.clipboard_clear()
            self.root.clipboard_append(analysis_text)
            messagebox.showinfo("Copied", "Analysis result copied to clipboard!")
        else:
            messagebox.showwarning("No Analysis", "There is no analysis result to copy yet.")


    def update_summary_tab_state(self):
        """Updates the state of buttons and elements in the 'Summarize Data' and 'Analyze Data' tabs based on whether data is loaded."""
        data_loaded = self.data_analyzer.df is not None and not self.data_analyzer.df.empty
        self.df = self.data_analyzer.df

        if self.summarize_button and self.summarize_button.winfo_exists():
            self.summarize_button.configure(state="normal" if data_loaded else "disabled")

        if self.prompt_entry and self.prompt_entry.winfo_exists():
            self.prompt_entry.configure(state="normal" if data_loaded else "disabled")
            if not data_loaded:
                self.prompt_entry.delete(0, ctk.END)

        if self.result_label and self.result_label.winfo_exists():
            self.result_label.configure(state="normal")
            if not data_loaded:
                self.result_label.delete("0.0", ctk.END)
                self.result_label.insert("0.0", "AI analysis results will appear here after you ask a question and click 'Analyze Data'.")
            self.result_label.configure(state="disabled")

        if self.analyze_button and self.analyze_button.winfo_exists():
            self.analyze_button.configure(state="normal" if data_loaded else "disabled")

        if self.copy_analysis_button and self.copy_analysis_button.winfo_exists():
            self.copy_analysis_button.configure(state="normal" if data_loaded else "disabled")

        if self.summary_output_textbox and self.summary_output_textbox.winfo_exists():
            self.summary_output_textbox.configure(state="normal")
            if not data_loaded:
                self.summary_output_textbox.delete("0.0", ctk.END)
                self.summary_output_textbox.insert("0.0", "Your AI-powered data summary will appear here after loading data and clicking 'Summarize Data'.")
            self.summary_output_textbox.configure(state="disabled")

        if self.copy_summary_button and self.copy_summary_button.winfo_exists():
            is_summary_placeholder = self.summary_output_textbox.get("0.0", ctk.END).strip() == "Your AI-powered data summary will appear here after loading data and clicking 'Summarize Data'."
            self.copy_summary_button.configure(state="normal" if data_loaded and not is_summary_placeholder else "disabled")


        if not data_loaded and self.plot_display_frame and self.plot_display_frame.winfo_exists():
            self.clear_frame_widgets(self.plot_display_frame)
            ctk.CTkLabel(self.plot_display_frame, text="Visualizations will appear here.",
                         font=("Arial", 16), text_color="#A9A9A9").pack(pady=50)
            self.current_plot_images = []

        summary_tab = self.tabview.tab("2. Summarize Data")
        if summary_tab and summary_tab.winfo_exists():
            for widget in summary_tab.winfo_children():
                if isinstance(widget, ctk.CTkFrame) and widget.winfo_exists():
                    for child_widget in widget.winfo_children():
                        if isinstance(child_widget, ctk.CTkButton) and "Go to Analyze Data" in child_widget.cget("text") and child_widget.winfo_exists():
                            child_widget.configure(state="normal" if data_loaded else "disabled")
                            break

        if self.translate_button and self.translate_button.winfo_exists():
            self.translate_button.configure(state="normal")
        if self.reset_languages_button and self.reset_languages_button.winfo_exists():
            self.reset_languages_button.configure(state="normal")


    def build_analyze_data_tab(self):
        """Builds the content for the '3. Analyze Data' tab."""
        tab = self.tabview.tab("3. Analyze Data")
        self.clear_frame_widgets(tab)

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_rowconfigure(2, weight=0)
        tab.grid_rowconfigure(3, weight=0)

        ctk.CTkLabel(tab, text="🧠 AI Data Analysis",
                     font=("Arial", 28, "bold"), text_color="white").grid(row=0, column=0, pady=(30, 20), sticky="ew", padx=30)

        analysis_content_frame = ctk.CTkFrame(tab, fg_color="#3A2B5B", corner_radius=10, border_width=2, border_color="#7B68EE")
        analysis_content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        analysis_content_frame.grid_columnconfigure(0, weight=1)
        analysis_content_frame.grid_rowconfigure(0, weight=0)
        analysis_content_frame.grid_rowconfigure(1, weight=0)
        analysis_content_frame.grid_rowconfigure(2, weight=0)
        analysis_content_frame.grid_rowconfigure(3, weight=0)
        analysis_content_frame.grid_rowconfigure(4, weight=1)
        analysis_content_frame.grid_rowconfigure(5, weight=0)

        ctk.CTkLabel(analysis_content_frame, text="Ask your data a question:",
                     font=("Arial", 18, "bold"), text_color="#D3D3D3").grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)

        self.prompt_entry = ctk.CTkEntry(analysis_content_frame,
                                         placeholder_text="e.g., What is the average sales per region?",
                                         font=("Arial", 16),
                                         width=600,
                                         height=40,
                                         fg_color="#4B0082",
                                         text_color="white",
                                         border_color="#7B68EE",
                                         border_width=1,
                                         state="disabled")
        self.prompt_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.analyze_button = ctk.CTkButton(analysis_content_frame,
                                            text="Analyze Data",
                                            command=self.analyze_data,
                                            font=("Arial", 20, "bold"),
                                            fg_color="#6A5ACD",
                                            hover_color="#7B68EE",
                                            height=50,
                                            state="disabled")
        self.analyze_button.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")

        self.loading_label_analysis = ctk.CTkLabel(analysis_content_frame, text="", font=("Arial", 16), text_color="#ADFF2F")
        self.loading_label_analysis.grid(row=3, column=0, pady=(0, 10))

        self.result_label = ctk.CTkTextbox(analysis_content_frame,
                                            wrap="word",
                                            font=("Arial", 16),
                                            text_color="white",
                                            fg_color="#4B0082",
                                            border_width=1,
                                            border_color="#7B68EE",
                                            corner_radius=5,
                                            state="disabled")
        self.result_label.insert("0.0", "AI analysis results will appear here after you ask a question and click 'Analyze Data'.")
        self.result_label.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self.copy_analysis_button = ctk.CTkButton(analysis_content_frame,
                                                  text="Copy Analysis",
                                                  command=self.copy_analysis_to_clipboard,
                                                  font=("Arial", 16, "bold"),
                                                  fg_color="#5D40A4",
                                                  hover_color="#7B68EE",
                                                  height=40,
                                                  image=self.icon_copy,
                                                  compound="left",
                                                  state="disabled")
        self.copy_analysis_button.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="e")

        nav_frame = ctk.CTkFrame(tab, fg_color="transparent")
        nav_frame.grid(row=2, column=0, pady=(0, 20), sticky="ew", padx=30)
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(1, weight=1)

        data_conn_button = ctk.CTkButton(nav_frame,
                                         text="Go to Data Connection",
                                         command=lambda: self.on_tab_select("1. Data Connection"),
                                         font=("Arial", 16),
                                         fg_color="#5D40A4",
                                         hover_color="#7B68EE",
                                         height=40,
                                         image=self.icon_data_connection,
                                         compound="left")
        data_conn_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        summarize_data_button = ctk.CTkButton(nav_frame,
                                              text="Go to Summarize Data",
                                              command=lambda: self.on_tab_select("2. Summarize Data"),
                                              font=("Arial", 16),
                                              fg_color="#5D40A4",
                                              hover_color="#7B68EE",
                                              height=40,
                                              image=self.icon_summarize_data,
                                              compound="left")
        summarize_data_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")


    def build_multilingual_support_tab(self):
        """Builds the content for the '4. Multilingual Support' tab."""
        tab = self.tabview.tab("4. Multilingual Support")
        self.clear_frame_widgets(tab)

        tab.grid_columnconfigure(0, weight=1)
        # Define rows for specific elements, allow the last row to expand
        tab.grid_rowconfigure(0, weight=0) # Title
        tab.grid_rowconfigure(1, weight=0) # Description
        tab.grid_rowconfigure(2, weight=0) # Input language and text box frame
        tab.grid_rowconfigure(3, weight=0) # Output language and text box frame
        tab.grid_rowconfigure(4, weight=0) # Translate button and loading label frame
        tab.grid_rowconfigure(5, weight=0) # Combined bottom buttons frame
        tab.grid_rowconfigure(6, weight=0) # Note about future feature
        tab.grid_rowconfigure(7, weight=1) # Expandable space at the bottom

        current_row = 0

        ctk.CTkLabel(tab, text="🌐 Multilingual Text Translation",
                     font=("Arial", 28, "bold"), text_color="white").grid(row=current_row, column=0, pady=(30, 20), sticky="ew", padx=30)
        current_row += 1

        ctk.CTkLabel(tab, text="Translate text between different languages.",
                     font=("Arial", 16), text_color="#D3D3D3", wraplength=800, justify="center").grid(row=current_row, column=0, pady=(0, 30), padx=50)
        current_row += 1

        # Input Language Selection and Text Box
        input_section_frame = ctk.CTkFrame(tab, fg_color="transparent")
        input_section_frame.grid(row=current_row, column=0, padx=50, pady=(10, 20), sticky="ew")
        input_section_frame.grid_columnconfigure(0, weight=0) # For dropdown
        input_section_frame.grid_columnconfigure(1, weight=1) # For textbox

        ctk.CTkLabel(input_section_frame, text="Input Language:",
                     font=("Arial", 16, "bold"), text_color="white").grid(row=0, column=0, pady=(0, 5), sticky="w")

        languages = ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Hindi", "Arabic"] # Example languages
        self.input_language_optionmenu = ctk.CTkOptionMenu(input_section_frame,
                                                            values=languages,
                                                            variable=self.input_language_var,
                                                            font=("Arial", 14),
                                                            dropdown_font=("Arial", 14),
                                                            width=150,
                                                            height=35,
                                                            fg_color="#6A5ACD",
                                                            button_color="#5D40A4",
                                                            button_hover_color="#7B68EE",
                                                            text_color="white",
                                                            dropdown_fg_color="#4B0082",
                                                            dropdown_hover_color="#5D40A4",
                                                            dropdown_text_color="white"
                                                           )
        self.input_language_optionmenu.grid(row=1, column=0, padx=(0, 10), pady=(0, 10), sticky="nw")

        self.input_text_box = ctk.CTkTextbox(input_section_frame,
                                             wrap="word",
                                             font=("Arial", 16),
                                             text_color="#A9A9A9",
                                             fg_color="#4B0082",
                                             border_width=1,
                                             border_color="#7B68EE",
                                             corner_radius=5,
                                             height=150)
        self.input_text_box.insert("0.0", "Enter text here to translate...")
        self.input_text_box.grid(row=0, column=1, rowspan=2, padx=(0, 0), pady=(0, 10), sticky="nsew")
        self.input_text_box.bind("<FocusIn>", self._clear_placeholder_input)
        self.input_text_box.bind("<FocusOut>", self._restore_placeholder_input)
        current_row += 1

        # Output Language Selection and Text Box
        output_section_frame = ctk.CTkFrame(tab, fg_color="transparent")
        output_section_frame.grid(row=current_row, column=0, padx=50, pady=(10, 20), sticky="ew")
        output_section_frame.grid_columnconfigure(0, weight=0)
        output_section_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(output_section_frame, text="Output Language:",
                     font=("Arial", 16, "bold"), text_color="white").grid(row=0, column=0, pady=(0, 5), padx=0, sticky="w")

        self.output_language_optionmenu = ctk.CTkOptionMenu(output_section_frame,
                                                             values=languages,
                                                             variable=self.output_language_var,
                                                             font=("Arial", 14),
                                                             dropdown_font=("Arial", 14),
                                                             width=150,
                                                             height=35,
                                                             fg_color="#6A5ACD",
                                                             button_color="#5D40A4",
                                                             button_hover_color="#7B68EE",
                                                             text_color="white",
                                                             dropdown_fg_color="#4B0082",
                                                             dropdown_hover_color="#5D40A4",
                                                             dropdown_text_color="white"
                                                            )
        self.output_language_optionmenu.grid(row=1, column=0, padx=(0, 10), pady=(0, 10), sticky="nw")

        self.output_text_box = ctk.CTkTextbox(output_section_frame,
                                              wrap="word",
                                              font=("Arial", 16),
                                              text_color="#A9A9A9",
                                              fg_color="#4B0082",
                                              border_width=1,
                                              border_color="#7B68EE",
                                              corner_radius=5,
                                              height=150,
                                              state="disabled")
        self.output_text_box.insert("0.0", "Translated text will appear here.")
        self.output_text_box.grid(row=0, column=1, rowspan=2, padx=(0, 0), pady=(0, 10), sticky="nsew")
        self.output_text_box.bind("<FocusIn>", self._clear_placeholder_output)
        self.output_text_box.bind("<FocusOut>", self._restore_placeholder_output)
        current_row += 1

        # Translate Button and Loading Label
        translate_button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        translate_button_frame.grid(row=current_row, column=0, padx=50, pady=(0, 20), sticky="ew")
        translate_button_frame.grid_columnconfigure(0, weight=1)
        translate_button_frame.grid_columnconfigure(1, weight=1)

        self.translate_button = ctk.CTkButton(translate_button_frame,
                                              text="Translate Text (Future Feature)",
                                              command=self._perform_translation_placeholder,
                                              font=("Arial", 18, "bold"),
                                              fg_color="#6A5ACD",
                                              hover_color="#7B68EE",
                                              height=45)
        self.translate_button.grid(row=0, column=0, columnspan=2, padx=(0, 10), sticky="ew")
        
        self.translation_loading_label = ctk.CTkLabel(translate_button_frame, text="", font=("Arial", 16), text_color="yellow")
        self.translation_loading_label.grid(row=1, column=0, columnspan=2, pady=(5,0), sticky="n")
        current_row += 1

        # Combined Reset and Navigation buttons
        bottom_buttons_frame = ctk.CTkFrame(tab, fg_color="transparent")
        bottom_buttons_frame.grid(row=current_row, column=0, padx=50, pady=(0, 20), sticky="ew")
        bottom_buttons_frame.grid_columnconfigure(0, weight=1) # Reset button column
        bottom_buttons_frame.grid_columnconfigure(1, weight=1) # Data Connection button column
        bottom_buttons_frame.grid_columnconfigure(2, weight=1) # Summarize Data button column

        self.reset_languages_button = ctk.CTkButton(bottom_buttons_frame,
                                                    text="Reset Languages & Text",
                                                    command=self._reset_languages_and_text,
                                                    font=("Arial", 16, "bold"),
                                                    fg_color="#8B0000",
                                                    hover_color="#DC143C",
                                                    height=40)
        self.reset_languages_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        data_conn_button = ctk.CTkButton(bottom_buttons_frame,
                                         text="Go to Data Connection",
                                         command=lambda: self.on_tab_select("1. Data Connection"),
                                         font=("Arial", 16),
                                         fg_color="#5D40A4",
                                         hover_color="#7B68EE",
                                         height=40,
                                         image=self.icon_data_connection,
                                         compound="left")
        data_conn_button.grid(row=0, column=1, padx=(10, 10), sticky="ew")

        summarize_data_button = ctk.CTkButton(bottom_buttons_frame,
                                              text="Go to Summarize Data",
                                              command=lambda: self.on_tab_select("2. Summarize Data"),
                                              font=("Arial", 16),
                                              fg_color="#5D40A4",
                                              hover_color="#7B68EE",
                                              height=40,
                                              image=self.icon_summarize_data,
                                              compound="left")
        summarize_data_button.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        current_row += 1 # Increment row for the combined button frame

        ctk.CTkLabel(tab, text="Note: Actual translation functionality will be implemented in future updates.",
                     font=("Arial", 14, "italic"), text_color="#A9A9A9", wraplength=800, justify="center").grid(row=current_row, column=0, pady=(20, 30), padx=50)
        current_row += 1

        tab.grid_rowconfigure(current_row, weight=1) # Push content to top

    def _clear_placeholder_input(self, event):
        """Clears the placeholder text from the input textbox when focused."""
        if self.input_text_box_placeholder_active:
            self.input_text_box.delete("0.0", ctk.END)
            self.input_text_box.configure(text_color="white")
            self.input_text_box_placeholder_active = False

    def _restore_placeholder_input(self, event):
        """Restores the placeholder text to the input textbox if left empty."""
        if not self.input_text_box.get("0.0", ctk.END).strip():
            self.input_text_box.insert("0.0", "Enter text here to translate...")
            self.input_text_box.configure(text_color="#A9A9A9")
            self.input_text_box_placeholder_active = True

    def _clear_placeholder_output(self, event):
        """Clears the placeholder text from the output textbox when focused."""
        if self.output_text_box_placeholder_active:
            self.output_text_box.configure(state="normal")
            self.output_text_box.delete("0.0", ctk.END)
            self.output_text_box.configure(text_color="white")
            self.output_text_box_placeholder_active = False
            self.output_text_box.configure(state="disabled")

    def _restore_placeholder_output(self, event):
        """Restores the placeholder text to the output textbox if left empty."""
        if not self.output_text_box.get("0.0", ctk.END).strip():
            self.output_text_box.configure(state="normal")
            self.output_text_box.insert("0.0", "Translated text will appear here.")
            self.output_text_box.configure(text_color="#A9A9A9")
            self.output_text_box_placeholder_active = True
            self.output_text_box.configure(state="disabled")


    def _perform_translation_placeholder(self):
        """Placeholder for actual translation logic."""
        input_text = self.input_text_box.get("0.0", ctk.END).strip()
        if not input_text or input_text == "Enter text here to translate...":
            messagebox.showwarning("No Text", "Please enter text to translate.")
            return

        self.translation_loading_label.configure(text="Translating...", text_color="yellow")
        self.output_text_box.configure(state="normal")
        self.output_text_box.delete("0.0", ctk.END)
        self.translate_button.configure(state="disabled")
        self.root.update_idletasks()

        self.root.after(2000, self._complete_translation_placeholder)

    def _complete_translation_placeholder(self):
        """Completes the placeholder translation."""
        input_text = self.input_text_box.get("0.0", ctk.END).strip()
        input_lang = self.input_language_var.get()
        output_lang = self.output_language_var.get()

        translated_text = f"'{input_text}' (from {input_lang}) translated to {output_lang}."
        self.output_text_box.insert("0.0", translated_text)
        self.output_text_box.configure(state="disabled")
        self.translation_loading_label.configure(text="Translation complete!", text_color="#ADFF2F")
        self.translate_button.configure(state="normal")


    def _reset_languages_and_text(self):
        """Resets the input and output language selections and clears text boxes."""
        self.input_language_var.set("English")
        self.output_language_var.set("English")

        self.input_text_box.configure(state="normal")
        self.input_text_box.delete("0.0", ctk.END)
        self.input_text_box.insert("0.0", "Enter text here to translate...")
        self.input_text_box.configure(text_color="#A9A9A9")
        self.input_text_box_placeholder_active = True

        self.output_text_box.configure(state="normal")
        self.output_text_box.delete("0.0", ctk.END)
        self.output_text_box.insert("0.0", "Translated text will appear here.")
        self.output_text_box.configure(text_color="#A9A9A9")
        self.output_text_box_placeholder_active = True
        self.output_text_box.configure(state="disabled")

        self.translation_loading_label.configure(text="")
        messagebox.showinfo("Reset", "Languages and text fields have been reset.")


    def analyze_data(self):
        """Triggers the data analysis process using the DataAnalyzer's analyse_dataframe."""
        if self.df is None:
            messagebox.showwarning("No Data", "Please load data first in the 'Data Connection' tab.")
            self.loading_label_analysis.configure(text="No data loaded.", text_color="orange")
            return

        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showwarning("No Query", "Please enter a question to analyze your data.")
            self.loading_label_analysis.configure(text="Please enter a question.", text_color="orange")
            return

        self.loading_label_analysis.configure(text="Analyzing data... Please wait, this may take a moment.", text_color="yellow")
        self.result_label.configure(state="normal")
        self.result_label.delete("0.0", ctk.END)
        self.copy_analysis_button.configure(state="disabled")
        self.analyze_button.configure(state="disabled")

        self.root.update_idletasks()

        try:
            analysis_result = self.data_analyzer.analyse_dataframe(self.df, prompt)
            self.result_label.insert("0.0", analysis_result)
            self.loading_label_analysis.configure(text="Analysis complete! ✅", text_color="#ADFF2F")
            self.copy_analysis_button.configure(state="normal")
        except Exception as e:
            self.result_label.insert("0.0", f"Error during analysis: {e}")
            self.loading_label_analysis.configure(text=f"Error: {e}", text_color="red")
        finally:
            self.result_label.configure(state="disabled")
            self.analyze_button.configure(state="normal")


# --- Application Entry Point ---
if __name__ == "__main__":
    root = ctk.CTk()
    app = DataAnalyzerApp(root)
    root.mainloop()
