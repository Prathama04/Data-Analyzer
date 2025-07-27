import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk 
import pandas as pd 

import backend 

class DataAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyzer")
        self.root.geometry("1400x850") 
        self.root.minsize(width=1000, height=700) 

        ctk.set_appearance_mode("light") 
        ctk.set_default_color_theme("blue") 

        self.df = None 
        self.entries = {} 
        
        self.file_path = ctk.StringVar(value="No file selected")
        self.data_source = ctk.StringVar(value="--- Select Source ---") 

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
        self.data_preview_label = None 

        # Load icons for tabs at initialization
        self.icon_data_connection = self.load_icon("data_connection_icon.png", (24, 24))
        self.icon_summarize_data = self.load_icon("summarize_data_icon.png", (24, 24))
        self.icon_analyze_data = self.load_icon("analyze_data_icon.png", (24, 24))
        self.icon_file_upload = self.load_icon("upload_icon.png", (20, 20)) 
        self.icon_database = self.load_icon("database_icon.png", (20, 20)) 
        self.icon_sharepoint = self.load_icon("sharepoint_icon.png", (20, 20)) 
        self.icon_reset = self.load_icon("reset_icon.png", (20, 20)) 
        self.icon_summarize_dataset = self.load_icon("summarize_icon.png", (20, 20)) 
        self.data_connection_tab_icon = self.load_icon("database_icon_large.png", (200, 200))
        self.summary_feature_image = self.load_icon("summary_feature_image.png", (300, 200)) 

        self.build_main_layout()

    def load_icon(self, path, size):
        """Helper to load and resize images for icons."""
        try:
            img = Image.open(path).resize(size)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except FileNotFoundError:
            print(f"Warning: {path} not found. Icon will not be displayed.")
            return None 

    def build_main_layout(self):
        # Reset internal state variables
        self.df = None 
        self.entries = {} 
        self.file_path.set("No file selected")
        self.data_source.set("--- Select Source ---") 

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
            app_icon_img = Image.open("icon_app_analyzer.png").resize((50, 50)) 
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

        def create_feature_item(parent, icon_path, title, description, row_num): 
            item_frame = ctk.CTkFrame(parent, fg_color="transparent")
            item_frame.grid(row=row_num, column=0, columnspan=2, sticky="ew", padx=20, pady=8) 
            item_frame.grid_columnconfigure(0, weight=0) 
            item_frame.grid_columnconfigure(1, weight=1) 

            try:
                icon_img = Image.open(icon_path).resize((30, 30)) 
                icon_ctk = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(30, 30))
                ctk.CTkLabel(item_frame, text="", image=icon_ctk).grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="nw") 
            except FileNotFoundError:
                ctk.CTkLabel(item_frame, text="•", font=("Arial", 25), text_color="#87CEEB").grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="nw") 
                print(f"Warning: {icon_path} not found. Showing text placeholder.")

            ctk.CTkLabel(item_frame, text=title, font=("Arial", 20, "bold"), text_color="white", anchor="w").grid(row=0, column=1, sticky="ew")
            ctk.CTkLabel(item_frame, text=description, font=("Arial", 14), text_color="#A9A9A9", wraplength=180, justify="left", anchor="w").grid(row=1, column=1, sticky="ew")

            return item_frame

        create_feature_item(self.sidebar_frame, "icon_multi_source.png", 
                            "Multi-Source Connection", "Excel, SQL, SharePoint", current_row)
        current_row += 1

        create_feature_item(self.sidebar_frame, "icon_summarization.png", 
                            "Smart Summarization", "Instant data insights", current_row)
        current_row += 1

        create_feature_item(self.sidebar_frame, "icon_ai_analysis.png", 
                            "AI Analysis", "Natural language queries", current_row)
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
            bottom_img = Image.open(bottom_image_path).resize((300, 80)) 
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
            ("3. Analyze Data", self.icon_analyze_data)
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
        # You'll call build_analyze_data_tab later for the third tab

    def clear_frame_widgets(self, frame):
        """Helper method to destroy all widgets within a given frame."""
        for widget in frame.winfo_children():
            widget.destroy()

    def build_data_connection_tab(self):
        """Builds the content for the '1. Data Connection' tab."""
        tab = self.tabview.tab("1. Data Connection")
        self.clear_frame_widgets(tab) 

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0) 
        tab.grid_rowconfigure(6, weight=1) 
        tab.grid_rowconfigure(7, weight=0) 
        tab.grid_rowconfigure(8, weight=0) 
        tab.grid_rowconfigure(9, weight=0) 

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
        self.input_section.grid(row=current_row, column=0, pady=10, sticky="nsew", padx=50)
        self.input_section.grid_columnconfigure(0, weight=1) 
        self.input_section_placeholder_label = ctk.CTkLabel(self.input_section, 
                                                            text="Click 'Submit Source Type' to see connection fields.", 
                                                            font=("Arial", 16), text_color="#A9A9A9")
        self.input_section_placeholder_label.pack(pady=50)
        
        self.connect_load_button = ctk.CTkButton(tab, 
                                                 text="Connect & Load Data",
                                                 command=self.load_data,
                                                 font=("Arial", 20, "bold"),
                                                 fg_color="#6A5ACD",
                                                 hover_color="#7B68EE",
                                                 height=50) 

        self.loading_label_data_load = ctk.CTkLabel(tab, text="", font=("Arial", 16), text_color="#ADFF2F")
        self.data_preview_label = ctk.CTkLabel(tab, text="Loaded Data Preview will appear here...", 
                                               font=("Arial", 16), text_color="#A9A9A9")


    def on_data_source_select(self, choice):
        """Handles the selection of a data source from the OptionMenu."""
        if choice == "--- Select Source ---":
            self.submit_source_button.configure(state="disabled")
            self.clear_frame_widgets(self.input_section)
            self.input_section_placeholder_label = ctk.CTkLabel(self.input_section, 
                                                                text="Click 'Submit Source Type' to see connection fields.", 
                                                                font=("Arial", 16), text_color="#A9A9A9")
            self.input_section_placeholder_label.pack(pady=50)
            self.connect_load_button.grid_forget()
            self.loading_label_data_load.grid_forget()
            self.data_preview_label.grid_forget()
        else:
            self.submit_source_button.configure(state="normal")
            self.clear_frame_widgets(self.input_section)
            self.input_section_placeholder_label = ctk.CTkLabel(self.input_section, 
                                                                text=f"Selected {choice}. Click 'Submit Source Type' to configure.", 
                                                                font=("Arial", 16), text_color="#A9A9A9")
            self.input_section_placeholder_label.pack(pady=50)
            self.connect_load_button.grid_forget()
            self.loading_label_data_load.grid_forget()
            self.data_preview_label.grid_forget()


    def show_source_input_fields(self):
        choice = self.data_source.get()
        self.clear_frame_widgets(self.input_section) 
        self.entries = {} 

        tab = self.tabview.tab("1. Data Connection") 
        input_section_row = self.input_section.grid_info()['row'] 
        
        self.connect_load_button.grid(row=input_section_row + 1, column=0, pady=20, sticky="ew", padx=50)
        self.loading_label_data_load.grid(row=input_section_row + 2, column=0, pady=(0, 10))
        self.data_preview_label.grid(row=input_section_row + 3, column=0, pady=20)
        self.connect_load_button.configure(state="normal") 

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
            self.input_section_placeholder_label.pack(pady=50)
            self.connect_load_button.configure(state="disabled")

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
            self.loading_label_data_load.configure(text=f"Selected: {path.split('/')[-1]}", text_color="#ADFF2F")
            if 'file_path_entry' in self.entries:
                self.entries['file_path_entry'].delete(0, ctk.END)
                self.entries['file_path_entry'].insert(0, path)
        else:
            self.loading_label_data_load.configure(text="File selection cancelled.", text_color="orange")

    def load_data(self):
        """Initiates data loading based on the selected source."""
        current_source = self.data_source.get()
        self.loading_label_data_load.configure(text="Loading data...", text_color="yellow")
        self.df = None 

        if current_source == "CSV/Excel File":
            file_path = self.file_path.get()
            if file_path and file_path != "No file selected":
                try:
                    self.df = backend.load_excel_csv(file_path) 
                    self.loading_label_data_load.configure(text=f"Data loaded successfully from {file_path.split('/')[-1]}!", text_color="#ADFF2F")
                    messagebox.showinfo("Success", f"Data loaded successfully from {file_path.split('/')[-1]}!")
                    self.tabview.set("2. Summarize Data") 
                except Exception as e:
                    self.loading_label_data_load.configure(text=f"Error loading file: {e}", text_color="red")
                    messagebox.showerror("Loading Error", f"Failed to load data: {e}")
            else:
                self.loading_label_data_load.configure(text="Please select a file first.", text_color="orange")
                messagebox.showwarning("No File Selected", "Please select a file to load.")

        elif current_source == "Database (SQL)":
            db_config = {key: self.entries[key].get() for key in ["dialect", "host", "port", "database_name", "username", "password"]}
            
            if not all(db_config.values()): 
                self.loading_label_data_load.configure(text="Please fill all database fields.", text_color="orange")
                messagebox.showwarning("Missing Fields", "Please fill all database connection details.")
                return

            try:
                self.loading_label_data_load.configure(text="Connecting to database...", text_color="yellow")
                dummy_sql_query = "SELECT * FROM some_default_table;" 
                self.df = backend.load_sql_table(
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
                self.tabview.set("2. Summarize Data") 
            except Exception as e:
                self.loading_label_data_load.configure(text=f"Database error: {e}", text_color="red")
                messagebox.showerror("Database Error", f"Failed to load data from database: {e}")

        elif current_source == "SharePoint List": 
            sp_config = {key: self.entries[key].get() for key in ["site_url", "list_name", "client_id", "client_secret"]}

            if not all(sp_config.values()):
                self.loading_label_data_load.configure(text="Please fill all SharePoint fields.", text_color="orange")
                messagebox.showwarning("Missing Fields", "Please fill all SharePoint connection details.")
                return

            try:
                self.loading_label_data_load.configure(text="Connecting to SharePoint and fetching data...", text_color="yellow")
                self.df = backend.load_sharepoint_list(
                    site_url=sp_config['site_url'],
                    list_name=sp_config['list_name'],
                    client_id=sp_config['client_id'],
                    client_secret=sp_config['client_secret']
                )
                self.loading_label_data_load.configure(text="Data loaded successfully from SharePoint!", text_color="#ADFF2F")
                messagebox.showinfo("Success", "Data loaded successfully from SharePoint list!")
                self.tabview.set("2. Summarize Data") 
            except Exception as e:
                self.loading_label_data_load.configure(text=f"SharePoint error: {e}", text_color="red")
                messagebox.showerror("SharePoint Error", f"Failed to load data from SharePoint: {e}")

        else:
            self.loading_label_data_load.configure(text="Please select a data source.", text_color="red")
            messagebox.showwarning("No Source Selected", "Please select a data source type from the dropdown.")

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

        # Set column weights: Left (Generate Summary) small, Right (AI Summary Results) very large
        tab.grid_columnconfigure(0, weight=1)  # Left section (Generate Summary)
        tab.grid_columnconfigure(1, weight=8)  # Right section (AI Summary Results) - now 8x the space
        tab.grid_rowconfigure(0, weight=0) 
        tab.grid_rowconfigure(1, weight=1) 

        ctk.CTkLabel(tab, text="📊 Data Summary & Insights", 
                     font=("Arial", 28, "bold"), text_color="white").grid(row=0, column=0, columnspan=2, pady=(30, 20), sticky="ew")

        # --- Left Section: Generate Summary ---
        generate_summary_frame = ctk.CTkFrame(tab, fg_color="transparent")
        generate_summary_frame.grid(row=1, column=0, sticky="nsew", padx=(30, 15), pady=20)
        generate_summary_frame.grid_columnconfigure(0, weight=1)
        generate_summary_frame.grid_rowconfigure((0, 1, 2, 3), weight=0)
        generate_summary_frame.grid_rowconfigure(4, weight=1) 

        ctk.CTkLabel(generate_summary_frame, text="✨ Generate Summary", 
                     font=("Arial", 22, "bold"), text_color="white", anchor="w").grid(row=0, column=0, pady=(0, 10), sticky="ew")

        if self.summary_feature_image:
            ctk.CTkLabel(generate_summary_frame, text="", image=self.summary_feature_image).grid(row=1, column=0, pady=(10, 20))
        else:
            ctk.CTkLabel(generate_summary_frame, text="[Summary Feature Image]", font=("Arial", 16), text_color="#A9A9A9").grid(row=1, column=0, pady=(10, 20))

        ctk.CTkLabel(generate_summary_frame, 
                     text="Our AI will analyze your dataset and provide comprehensive insights about data quality, patterns, and key statistics.", 
                     font=("Arial", 16), text_color="#D3D3D3", wraplength=180, justify="center").grid(row=2, column=0, pady=(0, 30))
        
        self.loading_label_summary = ctk.CTkLabel(generate_summary_frame, text="", font=("Arial", 16), text_color="yellow")
        self.loading_label_summary.grid(row=3, column=0, pady=(0, 10))

        self.summarize_button = ctk.CTkButton(generate_summary_frame,
                                              text="Summarize Dataset",
                                              command=self.trigger_data_summary_generation, 
                                              font=("Arial", 20, "bold"),
                                              fg_color="#E066FF", 
                                              hover_color="#EE82EE", 
                                              height=55,
                                              image=self.icon_summarize_dataset, 
                                              compound="left")
        self.summarize_button.grid(row=4, column=0, pady=(0, 20), sticky="s") 

        # --- Right Section: AI Summary Results ---
        ai_summary_results_frame = ctk.CTkFrame(tab, fg_color="#3A2B5B", corner_radius=10) 
        ai_summary_results_frame.grid(row=1, column=1, sticky="nsew", padx=(15, 30), pady=20)
        ai_summary_results_frame.grid_columnconfigure(0, weight=1)
        ai_summary_results_frame.grid_rowconfigure(0, weight=0)
        ai_summary_results_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(ai_summary_results_frame, text="🤖 AI Summary Results", 
                     font=("Arial", 22, "bold"), text_color="white", anchor="w").grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.summary_output_textbox = ctk.CTkTextbox(ai_summary_results_frame, 
                                                     font=("Arial", 16), 
                                                     text_color="#D3D3D3", 
                                                     wrap="word", 
                                                     activate_scrollbars=True,
                                                     fg_color="#4B0082", 
                                                     scrollbar_button_color="#7B68EE",
                                                     scrollbar_button_hover_color="#9B7AEF",
                                                     border_width=1,
                                                     border_color="#6A5ACD"
                                                    )
        self.summary_output_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.summary_output_textbox.insert("end", "AI summary will appear here.")
        self.summary_output_textbox.configure(state="disabled") 

    def on_tab_select(self, tab_name):
        """Callback when a tab button is clicked. Refreshes content based on the selected tab."""
        if tab_name == "2. Summarize Data":
            if self.df is None or self.df.empty:
                self.summary_output_textbox.configure(state="normal")
                self.summary_output_textbox.delete("1.0", "end")
                self.summary_output_textbox.insert("end", "No data loaded. Please connect to a data source on the 'Data Connection' tab before generating a summary.")
                self.summary_output_textbox.configure(state="disabled")
                self.summarize_button.configure(state="disabled") 
            else:
                self.summary_output_textbox.configure(state="normal")
                self.summary_output_textbox.delete("1.0", "end")
                self.summary_output_textbox.insert("end", "Click 'Summarize Dataset' to generate an AI summary.")
                self.summary_output_textbox.configure(state="disabled")
                self.summarize_button.configure(state="normal") 
            self.loading_label_summary.configure(text="") 

    def trigger_data_summary_generation(self):
        """
        Triggers the generation of the data summary when the "Summarize Dataset" button is clicked.
        """
        if self.df is None or self.df.empty:
            messagebox.showwarning("No Data", "Please load a dataset on the 'Data Connection' tab first.")
            self.summary_output_textbox.configure(state="normal")
            self.summary_output_textbox.delete("1.0", "end")
            self.summary_output_textbox.insert("end", "No data loaded to summarize.")
            self.summary_output_textbox.configure(state="disabled")
            return

        self.loading_label_summary.configure(text="Generating summary...", text_color="yellow")
        self.summary_output_textbox.configure(state="normal")
        self.summary_output_textbox.delete("1.0", "end")
        self.summary_output_textbox.insert("end", "Analyzing data... Please wait.")
        self.summary_output_textbox.configure(state="disabled")
        self.summarize_button.configure(state="disabled") 

        self.root.after(100, self._generate_and_display_summary_async) 

    def _generate_and_display_summary_async(self):
        """
        Internal method to generate the summary (can be called asynchronously).
        This is where the actual pandas describe/info/value_counts logic goes.
        """
        try:
            summary_report = self.generate_detailed_summary_string(self.df)
            
            self.summary_output_textbox.configure(state="normal")
            self.summary_output_textbox.delete("1.0", "end")
            self.summary_output_textbox.insert("end", summary_report)
            self.summary_output_textbox.configure(state="disabled")
            self.loading_label_summary.configure(text="Summary generated successfully!", text_color="#ADFF2F")
            self.summarize_button.configure(state="normal")

        except Exception as e:
            self.summary_output_textbox.configure(state="normal")
            self.summary_output_textbox.delete("1.0", "end")
            self.summary_output_textbox.insert("end", f"Error generating summary: {e}")
            self.summary_output_textbox.configure(state="disabled")
            self.loading_label_summary.configure(text="Error generating summary.", text_color="red")
            self.summarize_button.configure(state="normal")
            messagebox.showerror("Summary Error", f"Failed to generate summary: {e}")

    def generate_detailed_summary_string(self, df):
        """
        Generates a comprehensive summary string from the DataFrame.
        This is the "AI Summary" part, mimicking what an AI might produce.
        """
        if df is None or df.empty:
            return "No data available to generate a summary."

        summary_parts = []

        summary_parts.append("### Dataset Summary Report\n")

        # Data Overview
        summary_parts.append("#### Data Overview:")
        summary_parts.append(f"- Total Rows: {df.shape[0]:,}")
        summary_parts.append(f"- Total Columns: {df.shape[1]}")
        summary_parts.append(f"- Memory Usage: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB\n")

        # Data Types
        summary_parts.append("#### Data Types:")
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        boolean_cols = df.select_dtypes(include=['bool']).columns.tolist()

        if numerical_cols:
            summary_parts.append(f"- Numerics ({len(numerical_cols)} columns): {', '.join(numerical_cols[:5])}{'...' if len(numerical_cols) > 5 else ''}")
        if text_cols:
            summary_parts.append(f"- Text ({len(text_cols)} columns): {', '.join(text_cols[:5])}{'...' if len(text_cols) > 5 else ''}")
        if date_cols:
            summary_parts.append(f"- Date ({len(date_cols)} columns): {', '.join(date_cols[:5])}{'...' if len(date_cols) > 5 else ''}")
        if boolean_cols:
            summary_parts.append(f"- Boolean ({len(boolean_cols)} columns): {', '.join(boolean_cols[:5])}{'...' if len(boolean_cols) > 5 else ''}")
        summary_parts.append("\n")

        # Missing Values Analysis
        missing_values = df.isnull().sum()
        missing_percentage = (df.isnull().sum() / len(df)) * 100
        missing_info = pd.DataFrame({'Missing Count': missing_values, 'Percentage': missing_percentage})
        missing_info = missing_info[missing_info['Missing Count'] > 0].sort_values(by='Missing Count', ascending=False)

        summary_parts.append("#### Missing Values Analysis:")
        if missing_info.empty:
            summary_parts.append("- All columns: Complete data ✅")
        else:
            for index, row in missing_info.iterrows():
                summary_parts.append(f"- {index}: {int(row['Missing Count'])} missing values ({row['Percentage']:.1f}%)")
            if len(df.columns) > len(missing_info):
                summary_parts.append("- All other columns: Complete data ✅")
        summary_parts.append("\n")

        # Key Statistics (for numerical columns)
        summary_parts.append("#### Key Statistics:")
        num_df = df.select_dtypes(include=['number'])
        if not num_df.empty:
            for col in num_df.columns:
                try:
                    mean_val = num_df[col].mean()
                    min_val = num_df[col].min()
                    max_val = num_df[col].max()
                    
                    summary_parts.append(f"- **{col}**: Average: {mean_val:,.2f}, Range: {min_val:,.2f} - {max_val:,.2f}")
                except Exception:
                    summary_parts.append(f"- **{col}**: (Statistics not calculable or non-numeric data)")
        else:
            summary_parts.append("- No numerical columns found for key statistics.")
        summary_parts.append("\n")

        # Most Common Categories (for categorical columns)
        summary_parts.append("#### Most Common Categories:")
        cat_df = df.select_dtypes(include=['object', 'category'])
        if not cat_df.empty:
            for col in cat_df.columns:
                top_value = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
                top_count = df[col].value_counts().max() if not df[col].value_counts().empty else 0
                top_percentage = (top_count / len(df)) * 100 if len(df) > 0 else 0
                
                summary_parts.append(f"- **{col}**: Most common: '{top_value}' ({top_count} occurrences, {top_percentage:.1f}%)")
        else:
            summary_parts.append("- No categorical columns found for common categories.")
        summary_parts.append("\n")

        return "\n".join(summary_parts)


# --- Application Entry Point ---
if __name__ == "__main__":
    root = ctk.CTk()
    app = DataAnalyzerApp(root)
    root.mainloop()