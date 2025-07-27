import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk 

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
        self.summary_label = None
        self.result_label = None
        self.prompt_entry = None
        self.input_section = None
        self.input_section_placeholder_label = None

        # Load icons for tabs at initialization
        self.icon_data_connection = self.load_icon("data_connection_icon.png", (24, 24))
        self.icon_summarize_data = self.load_icon("summarize_data_icon.png", (24, 24))
        self.icon_analyze_data = self.load_icon("analyze_data_icon.png", (24, 24))
        self.icon_file_upload = self.load_icon("upload_icon.png", (20, 20)) 
        self.icon_database = self.load_icon("database_icon.png", (20, 20)) 
        self.icon_sharepoint = self.load_icon("sharepoint_icon.png", (20, 20)) 
        self.icon_reset = self.load_icon("reset_icon.png", (20, 20))

        self.build_main_layout()

    def load_icon(self, path, size):
       
        try:
            img = Image.open(path).resize(size)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except FileNotFoundError:
            print(f"Warning: {path} not found. Icon will not be displayed.")
            return None 

    def build_main_layout(self):
        
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
                        break

        self.tabview.set("1. Data Connection")

        self.build_data_connection_tab()


    def clear_frame_widgets(self, frame):
        
        for widget in frame.winfo_children():
            widget.destroy()

    def build_data_connection_tab(self):
        
        tab = self.tabview.tab("1. Data Connection")
        self.clear_frame_widgets(tab) 

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=0) 
        tab.grid_rowconfigure(8, weight=1)
        
        current_row = 0

      
        try:
           
            data_connection_img = Image.open("database_icon_large.png").resize((200, 200)) 
            self.data_connection_ctk_img = ctk.CTkImage(light_image=data_connection_img, 
                                                       dark_image=data_connection_img, 
                                                       size=(200, 200))
            ctk.CTkLabel(tab, text="", image=self.data_connection_ctk_img).grid(row=current_row, column=0, pady=(30, 10))
        except FileNotFoundError:
            ctk.CTkLabel(tab, text="🗄️", font=("Arial", 100), text_color="#ADFF2F").grid(row=current_row, column=0, pady=(30, 10))
            print("Warning: database_icon_large.png not found. Showing text placeholder.")
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
                                                        dropdown_fg_color="#642392", 
                                                        dropdown_hover_color="#5D40A4", 
                                                        dropdown_text_color="white" 
                                                       )
        self.data_source_optionmenu.grid(row=current_row, column=0, pady=(0, 20), sticky="ew", padx=50)
        current_row += 1

        self.input_section = ctk.CTkFrame(tab, fg_color="transparent")
        self.input_section.grid(row=current_row, column=0, pady=10, sticky="ew", padx=50)
        self.input_section.grid_columnconfigure(0, weight=1) 
        self.input_section_placeholder_label = ctk.CTkLabel(self.input_section, 
                                                            text="Please select a data source to continue.", 
                                                            font=("Arial", 16), text_color="#A9A9A9")
        self.input_section_placeholder_label.pack(pady=50)
        current_row += 1

        self.connect_load_button = ctk.CTkButton(tab, 
                                                 text="Connect & Load Data",
                                                 command=self.load_data,
                                                 font=("Arial", 20, "bold"),
                                                 fg_color="#6A5ACD",
                                                 hover_color="#7B68EE",
                                                 height=50,
                                                 state="disabled") 
        self.connect_load_button.grid(row=current_row, column=0, pady=20, sticky="ew", padx=50)
        current_row += 1

        self.loading_label_data_load = ctk.CTkLabel(tab, text="", font=("Arial", 16), text_color="#ADFF2F")
        self.loading_label_data_load.grid(row=current_row, column=0, pady=(0, 10))
        current_row += 1

        ctk.CTkLabel(tab, text="Loaded Data Preview will appear here...", 
                     font=("Arial", 16), text_color="#A9A9A9").grid(row=current_row, column=0, pady=20)
        current_row += 1
        
        tab.grid_rowconfigure(current_row, weight=1)


    def on_data_source_select(self, choice):
        """Handles the selection of a data source from the OptionMenu."""
        self.clear_frame_widgets(self.input_section) 
        self.connect_load_button.configure(state="normal") 
        self.loading_label_data_load.configure(text="") 
        self.entries = {} 

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
        #Builds input fields for CSV/Excel file selection.
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
        #Builds input fields for SharePoint connection.
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
        #Opens a file dialog for CSV/Excel file selection.
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
        #Initiates data loading based on the selected source
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
        #Resets the application to its initial state.
        response = messagebox.askyesno("Reset Application", "Are you sure you want to reset the application? All loaded data will be cleared.")
        if response:
            self.build_main_layout() 
            messagebox.showinfo("Reset", "Application has been reset.")


# --- Application Entry Point ---
if __name__ == "__main__":
    root = ctk.CTk()
    app = DataAnalyzerApp(root)
    root.mainloop()