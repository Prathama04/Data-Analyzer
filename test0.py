import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk # Import ImageTk for handling image scaling
import pandas as pd
import backend 

class DataWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyzer")
        self.root.geometry("1200x800") # Increased default size for dashboard layout
        self.root.minsize(width=1000, height=700) # Increased min size

        ctk.set_appearance_mode("dark") # The design uses a darker theme overall
        ctk.set_default_color_theme("blue") # Blue accents for buttons etc.

        # Initialize state variables
        self.data_source = ctk.StringVar(value="--- Select Source ---")
        self.file_path = ctk.StringVar(value="No file selected")
        self.df = None
        self.entries = {} # Stores references to entry widgets for dynamic forms

        # Main content frames to be managed for dynamic display
        self.dashboard_frame = None
        self.data_connection_form_frame = None
        self.summary_results_frame = None
        self.analysis_query_frame = None


        self.build_main_layout()

    def build_main_layout(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # --- Configure Grid for Main Window ---
        # 3 columns: Left Nav (fixed width), Main Content (expands), Right margin (small fixed)
        self.root.grid_columnconfigure(0, weight=0) # Left Nav - fixed width
        self.root.grid_columnconfigure(1, weight=1) # Main Content - expands
        self.root.grid_columnconfigure(2, weight=0) # Small right margin/shadow effect

        # 2 rows: Top Bar (fixed height), Main Content Area (expands)
        self.root.grid_rowconfigure(0, weight=0) # Top Bar - fixed height
        self.root.grid_rowconfigure(1, weight=1) # Main Content Area - expands

        # --- Top Bar ---
        self.top_bar = ctk.CTkFrame(self.root, height=60, corner_radius=0, fg_color="#3A3B5B") # Darker purple shade
        self.top_bar.grid(row=0, column=0, columnspan=3, sticky="nsew") # Spans all columns

        # Layout for top bar contents
        self.top_bar.grid_columnconfigure(0, weight=0) # Logo/Title
        self.top_bar.grid_columnconfigure(1, weight=1) # Search Bar (expands)
        self.top_bar.grid_columnconfigure(2, weight=0) # Icons

        # --- Top Bar: App Title ---
        ctk.CTkLabel(self.top_bar, text="DATA ANALYZER", font=("Arial", 20, "bold"), text_color="white").grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # --- Top Bar: Search Bar ---
        self.search_entry = ctk.CTkEntry(self.top_bar, placeholder_text="Search for data, reports, or insights...",
                                         width=400, fg_color="#4F507F", border_color="#5D5E8C", text_color="white") # Deeper input color
        self.search_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        # --- Top Bar: User/Settings Icons ---
        # Placeholder for icons (you'd load actual image icons here)
        icon_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        icon_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")
        # Assuming you'll have actual icon images later. For now, text placeholders.
        ctk.CTkLabel(icon_frame, text="🔔", font=("Arial", 20), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(icon_frame, text="⚙️", font=("Arial", 20), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(icon_frame, text="👤", font=("Arial", 20), text_color="white").pack(side="left", padx=5)


        # --- Left Navigation Panel (Sidebar) ---
        self.left_nav_panel = ctk.CTkFrame(self.root, width=220, corner_radius=0, fg_color="#2D2E4A") # Darker purple for nav
        self.left_nav_panel.grid(row=1, column=0, sticky="nsew")
        self.left_nav_panel.grid_rowconfigure((0,1,2,3,4,5,6), weight=0) # Fixed size for buttons
        self.left_nav_panel.grid_rowconfigure(7, weight=1) # Expands below buttons
        self.left_nav_panel.grid_rowconfigure(8, weight=0) # Logo at bottom

        # --- Left Nav: App Branding/Logo (Moved from top of sidebar) ---
        try:
            # Using a smaller, square logo to fit the top of the nav
            app_logo_img = Image.open("app_logo_placeholder.png").resize((80, 80)) # Placeholder image, replace with your custom one
            self.app_logo_ctk = ctk.CTkImage(light_image=app_logo_img, dark_image=app_logo_img, size=(80, 80))
            ctk.CTkLabel(self.left_nav_panel, text="", image=self.app_logo_ctk).grid(row=0, column=0, pady=(20, 10), padx=20)
        except FileNotFoundError:
            ctk.CTkLabel(self.left_nav_panel, text="[App Logo]", text_color="white", font=("Arial", 14)).grid(row=0, column=0, pady=(20, 10), padx=20)
            print("Warning: app_logo_placeholder.png not found. Showing text placeholder.")

        # --- Left Nav: Navigation Buttons ---
        self.nav_buttons_frame = ctk.CTkFrame(self.left_nav_panel, fg_color="transparent")
        self.nav_buttons_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.nav_buttons_frame.grid_columnconfigure(0, weight=1)

       
        # Dashboard Button
        self.btn_dashboard = self.create_nav_button(self.nav_buttons_frame, "📊 Dashboard", lambda: self.show_view("dashboard"))
        self.btn_dashboard.grid(row=0, column=0, pady=5, sticky="ew", padx=5) # <--- Add padx here

        # Data Connection Button
        self.btn_data_connection = self.create_nav_button(self.nav_buttons_frame, "📁 Data Connection", lambda: self.show_view("data_connection_form"))
        self.btn_data_connection.grid(row=1, column=0, pady=5, sticky="ew", padx=5) # <--- Add padx here

        # Data Summary Button
        self.btn_data_summary = self.create_nav_button(self.nav_buttons_frame, "⬇️ Data Summary", lambda: self.show_view("summary_results"))
        self.btn_data_summary.grid(row=2, column=0, pady=5, sticky="ew", padx=5) # <--- Add padx here

        # Data Analysis Button
        self.btn_data_analysis = self.create_nav_button(self.nav_buttons_frame, "🧠 Data Analysis", lambda: self.show_view("analysis_query"))
        self.btn_data_analysis.grid(row=3, column=0, pady=5, sticky="ew", padx=5) # <--- Add padx here
        # "Your Questions" Section in Left Nav (Bottom)
        ctk.CTkLabel(self.left_nav_panel, text="Your Questions", font=("Arial", 14, "bold"), text_color="white").grid(row=5, column=0, pady=(30, 5), padx=20, sticky="w")
        self.left_nav_prompt_entry = ctk.CTkEntry(self.left_nav_panel, placeholder_text="Ask a quick question...", width=180, fg_color="#4F507F", border_color="#5D5E8C", text_color="white")
        self.left_nav_prompt_entry.grid(row=6, column=0, pady=5, padx=20, sticky="ew")
        self.left_nav_ask_button = ctk.CTkButton(self.left_nav_panel, text="Ask AI", command=self.run_analysis_from_nav, fg_color="#6A5ACD", hover_color="#7B68EE") # Purple button
        self.left_nav_ask_button.grid(row=7, column=0, pady=10, padx=20, sticky="ew")


        # --- Bottom Right Logo (Org Logo) ---
        try:
            org_image = Image.open("org_logo.png").resize((180, 70)) # Adjust size if needed
            org_logo = ctk.CTkImage(light_image=org_image, dark_image=org_image, size=(180, 70))
            org_label = ctk.CTkLabel(self.left_nav_panel, image=org_logo, text="")
            org_label.image = org_logo # Keep reference
            org_label.grid(row=8, column=0, pady=(20, 10), sticky="s") # Stick to bottom
        except FileNotFoundError:
            ctk.CTkLabel(self.left_nav_panel, text="[Org Logo]", text_color="white", font=("Arial", 12)).grid(row=8, column=0, pady=(20, 10), sticky="s")
            print("Warning: org_logo.png not found. Showing text placeholder.")


        # --- Main Content Area (Scrollable Frame) ---
        # This will hold the dashboard cards or dynamic forms
        self.main_content_area = ctk.CTkScrollableFrame(self.root, fg_color="#EFEFF5") # Light grey background
        self.main_content_area.grid(row=1, column=1, sticky="nsew", padx=20, pady=20) # Padding to match design

        # --- Right Margin/Shadow (Optional, for visual effect) ---
        self.right_margin_frame = ctk.CTkFrame(self.root, width=20, corner_radius=0, fg_color="#EFEFF5") # Matches main content background
        self.right_margin_frame.grid(row=1, column=2, sticky="nsew")


        # Initialize and show the dashboard view first
        self.show_view("dashboard")

    # Helper function to create consistent navigation buttons
    def create_nav_button(self, parent, text, command):
        # REMOVE padx from here
        return ctk.CTkButton(parent, text=text, command=command,
                             height=40, font=("Arial", 14),
                             fg_color="transparent", text_color="white",
                             hover_color="#4F507F", # Slightly lighter purple on hover
                             anchor="w") # Align text to left. padx is for grid/pack

    def show_view(self, view_name):
        # Hide all possible content frames
        if self.dashboard_frame:
            self.dashboard_frame.grid_forget()
        if self.data_connection_form_frame:
            self.data_connection_form_frame.grid_forget()
        if self.summary_results_frame:
            self.summary_results_frame.grid_forget()
        if self.analysis_query_frame:
            self.analysis_query_frame.grid_forget()
        
        # Clear main content area before showing new view to prevent overlap issues
        for widget in self.main_content_area.winfo_children():
            widget.destroy()

        # Show the requested view
        if view_name == "dashboard":
            self.display_dashboard()
        elif view_name == "data_connection_form":
            self.display_data_connection_form()
        elif view_name == "summary_results":
            self.display_summary_results()
        elif view_name == "analysis_query":
            self.display_analysis_query()

        # Update button states (optional, for visual feedback)
    # --- Placeholder Methods for Content Views (to be filled in next steps) ---
    def display_dashboard(self):
        if not self.dashboard_frame:
            self.dashboard_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.dashboard_frame.grid_columnconfigure((0,1,2,3), weight=1) # For cards
        
        ctk.CTkLabel(self.dashboard_frame, text="Solution Categories", font=("Arial", 18, "bold"), text_color="#3A3B5B").grid(row=0, column=0, columnspan=4, pady=(0, 20), sticky="w")
        
      
        # Card 1: Data Processing Overview
        self.create_dashboard_card(self.dashboard_frame, 1, 0, "monitor_icon.png", "Data Processing Overview",
                                   "Gain insights into your data's structure and completeness. Connect, clean, and prepare datasets efficiently.",
                                   "Connect Data", lambda: self.show_view("data_connection_form"),
                                   "Show Details", lambda: messagebox.showinfo("Details", "Detailed information about Data Processing."))
        # Card 2: Strategic Planning Insights
        self.create_dashboard_card(self.dashboard_frame, 1, 1, "people_icon.png", "Strategic Planning Insights",
                                   "Leverage historical data to forecast trends and inform strategic decisions for future growth.",
                                   "Explore Forecasts", lambda: messagebox.showinfo("Action", "Exploring forecasts..."),
                                   "Learn More", lambda: messagebox.showinfo("Details", "Detailed info on Strategic Planning."))
        # Card 3: Performance Analysis
        self.create_dashboard_card(self.dashboard_frame, 1, 2, "laptop_icon.png", "Performance Analysis",
                                   "Monitor key performance indicators (KPIs) and identify areas for improvement.",
                                   "View Performance", lambda: messagebox.showinfo("Action", "Viewing performance..."),
                                   "Dive Deeper", lambda: messagebox.showinfo("Details", "Detailed info on Performance Analysis."))
        # Card 4: Customer Behavior Trends
        self.create_dashboard_card(self.dashboard_frame, 1, 3, "user_icon.png", "Customer Behavior Trends",
                                   "Understand customer preferences, buying patterns, and engagement levels to optimize strategies.",
                                   "Analyze Customers", lambda: messagebox.showinfo("Action", "Analyzing customer behavior..."),
                                   "Get Insights", lambda: messagebox.showinfo("Details", "Detailed info on Customer Behavior."))

        # "Your Questions" section in the main content area (as seen in the dashboard image)
        ctk.CTkLabel(self.dashboard_frame, text="Your Questions", font=("Arial", 18, "bold"), text_color="#3A3B5B").grid(row=2, column=0, columnspan=4, pady=(40, 20), sticky="w")
        self.dashboard_prompt_entry = ctk.CTkEntry(self.dashboard_frame, placeholder_text="Enter your question here...",
                                         width=800, fg_color="white", border_color="#DEDFE3", text_color="#3A3B5B")
        self.dashboard_prompt_entry.grid(row=3, column=0, columnspan=3, padx=(0,10), sticky="ew") # Spans 3 columns
        self.dashboard_ask_button = ctk.CTkButton(self.dashboard_frame, text="Ask AI", command=self.run_analysis_from_dashboard, fg_color="#0066CC", hover_color="#0052A3") # Blue button
        self.dashboard_ask_button.grid(row=3, column=3, sticky="ew") # In the 4th column

        # Initial prompt/results area
        self.dashboard_analysis_results = ctk.CTkLabel(self.dashboard_frame, text="AI insights will appear here after you ask a question.", wraplength=900, justify="left", text_color="#3A3B5B")
        self.dashboard_analysis_results.grid(row=4, column=0, columnspan=4, pady=(10, 0), sticky="nw")


    def create_dashboard_card(self, parent_frame, row, column, icon_path, title, description,
                              button1_text, button1_command, button2_text, button2_command):
        card_frame = ctk.CTkFrame(parent_frame, width=250, height=300, corner_radius=10, fg_color="white", border_color="#E0E0E0", border_width=1)
        card_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        card_frame.grid_propagate(False) # Prevent frame from shrinking to fit content

        card_frame.grid_rowconfigure((0,1,2), weight=0) # For fixed size content
        card_frame.grid_rowconfigure(3, weight=1) # For description (expands)
        card_frame.grid_rowconfigure((4,5), weight=0) # For buttons

        # Card Icon
        try:
            icon_img = Image.open(icon_path).resize((50, 50)) # Adjust icon size
            icon_ctk = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(50, 50))
            ctk.CTkLabel(card_frame, text="", image=icon_ctk).grid(row=0, column=0, pady=(15,5), padx=10, sticky="nw")
        except FileNotFoundError:
            ctk.CTkLabel(card_frame, text="[Icon]", text_color="#3A3B5B", font=("Arial", 12)).grid(row=0, column=0, pady=(15,5), padx=10, sticky="nw")
            print(f"Warning: {icon_path} not found.")

        # Card Title
        ctk.CTkLabel(card_frame, text=title, font=("Arial", 16, "bold"), text_color="#3A3B5B", wraplength=200, justify="left").grid(row=1, column=0, padx=10, pady=(5,0), sticky="nw")

        # Card Description
        ctk.CTkLabel(card_frame, text=description, font=("Arial", 12), text_color="#6F6F6F", wraplength=230, justify="left").grid(row=2, column=0, padx=10, pady=(5,10), sticky="nw")

        # Buttons at the bottom of the card
        button1 = ctk.CTkButton(card_frame, text=button1_text, command=button1_command,
                                fg_color="#0066CC", hover_color="#0052A3", corner_radius=5)
        button1.grid(row=4, column=0, pady=(0, 5), padx=10, sticky="ew")

        button2 = ctk.CTkButton(card_frame, text=button2_text, command=button2_command,
                                fg_color="transparent", border_color="#0066CC", border_width=1,
                                text_color="#0066CC", hover_color="#E0E0E0", corner_radius=5)
        button2.grid(row=5, column=0, pady=(0, 15), padx=10, sticky="ew") # More padding at bottom

        return card_frame

    def display_data_connection_form(self):
        # This will be the form that appears when "Connect Data" is clicked from a card
        if not self.data_connection_form_frame:
            self.data_connection_form_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.data_connection_form_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.data_connection_form_frame.grid_columnconfigure(0, weight=1) # Ensure form expands

        ctk.CTkLabel(self.data_connection_form_frame, text="Connect to Your Data Source", font=("Arial", 18, "bold"), text_color="#3A3B5B").pack(pady=10)

        # Reusing the existing data source selection and input logic
        source_selection_frame = ctk.CTkFrame(self.data_connection_form_frame, fg_color="transparent")
        source_selection_frame.pack(pady=10)
        ctk.CTkLabel(source_selection_frame, text="Choose Data Source:", text_color="#3A3B5B").pack(side="left", padx=5)
        self.source_menu = ctk.CTkOptionMenu(source_selection_frame, variable=self.data_source,
                                             values=["--- Select Source ---", "Excel/CSV", "SQL Database", "SharePoint List"],
                                             command=self.on_source_menu_change, fg_color="white", text_color="#3A3B5B", button_color="#0066CC", button_hover_color="#0052A3")
        self.source_menu.pack(side="left", padx=5)
        self.submit_source_button = ctk.CTkButton(source_selection_frame, text="Submit Source",
                                                  command=self.display_source_inputs, state="disabled", fg_color="#0066CC", hover_color="#0052A3")
        self.submit_source_button.pack(side="left", padx=15)

        # Dynamic Input Section (re-using existing structure)
        self.input_section = ctk.CTkFrame(self.data_connection_form_frame, fg_color="white", corner_radius=10, padx=20, pady=20, border_color="#E0E0E0", border_width=1)
        self.input_section.pack(pady=10, fill="x", padx=20)
        self.input_section_placeholder_label = ctk.CTkLabel(self.input_section, text="Please select a data source and click 'Submit Source'.", wraplength=400, justify="center", text_color="#3A3B5B")
        self.input_section_placeholder_label.pack(pady=40)

        # Connect/Load and Back Buttons
        action_buttons_frame = ctk.CTkFrame(self.data_connection_form_frame, fg_color="transparent")
        action_buttons_frame.pack(pady=15)

        self.connect_load_button = ctk.CTkButton(action_buttons_frame, text="Connect/Load Data", command=self.perform_data_load, state="disabled", fg_color="#0066CC", hover_color="#0052A3")
        self.connect_load_button.pack(side="left", padx=10)

        self.back_to_dashboard_button = ctk.CTkButton(action_buttons_frame, text="Back to Dashboard", command=lambda: self.show_view("dashboard"), fg_color="#6F6F6F", hover_color="#5A5A5A")
        self.back_to_dashboard_button.pack(side="left", padx=10)

        # Loading indicator for data loading
        self.loading_label_data_load = ctk.CTkLabel(self.data_connection_form_frame, text="Loading data...", font=("Arial", 14, "italic"), text_color="#3A3B5B")
        self.loading_label_data_load.pack_forget()

        # Call on_source_menu_change to correctly set initial state of submit button
        self.on_source_menu_change(self.data_source.get())


    def display_summary_results(self):
        if not self.summary_results_frame:
            self.summary_results_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.summary_results_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.summary_results_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.summary_results_frame, text="Dataset Summary", font=("Arial", 18, "bold"), text_color="#3A3B5B").pack(pady=10)

        self.summarize_button = ctk.CTkButton(self.summary_results_frame, text="Generate Summary", command=self.summarize_data, fg_color="#0066CC", hover_color="#0052A3",
                                              state="normal" if self.df is not None else "disabled") # Enable if data is loaded
        self.summarize_button.pack(pady=20)

        self.summary_label = ctk.CTkLabel(self.summary_results_frame, text="Click 'Generate Summary' to see insights.", wraplength=700, justify="left", text_color="#3A3B5B")
        self.summary_label.pack(pady=10, fill="both", expand=True) # Allow label to expand

        self.loading_label_summary = ctk.CTkLabel(self.summary_results_frame, text="Generating summary...", font=("Arial", 14, "italic"), text_color="#3A3B5B")
        self.loading_label_summary.pack_forget()


    def display_analysis_query(self):
        if not self.analysis_query_frame:
            self.analysis_query_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.analysis_query_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.analysis_query_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.analysis_query_frame, text="Ask AI About Your Data", font=("Arial", 18, "bold"), text_color="#3A3B5B").pack(pady=10)

        self.prompt_entry = ctk.CTkEntry(self.analysis_query_frame, placeholder_text="Ask your question (e.g., 'number of rows', 'average price', 'unique categories')...", width=600, fg_color="white", border_color="#DEDFE3", text_color="#3A3B5B")
        self.prompt_entry.pack(pady=10)

        self.analyze_button = ctk.CTkButton(self.analysis_query_frame, text="Analyze Data", command=self.run_analysis, fg_color="#0066CC", hover_color="#0052A3",
                                            state="normal" if self.df is not None else "disabled") # Enable if data is loaded
        self.analyze_button.pack(pady=10)

        self.loading_label_analysis = ctk.CTkLabel(self.analysis_query_frame, text="Analyzing data...", font=("Arial", 14, "italic"), text_color="#3A3B5B")
        self.loading_label_analysis.pack_forget()

        self.result_label = ctk.CTkLabel(self.analysis_query_frame, text="AI analysis results will be displayed here.", wraplength=700, justify="left", text_color="#3A3B5B")
        self.result_label.pack(pady=20, fill="both", expand=True) # Allow label to expand


    # --- Modified existing methods to fit new UI flow ---

    def on_source_menu_change(self, choice):
        # Original logic, but ensure `display_source_inputs` can be called from here
        if choice == "--- Select Source ---":
            self.submit_source_button.configure(state="disabled")
            self.reset_input_section_state() # Clear dynamic inputs if source is reset
        else:
            self.submit_source_button.configure(state="normal")
            # Automatically display inputs if a valid source is selected on menu change
            # This is a small UX improvement for the new design
            # self.display_source_inputs() # Uncomment if you want immediate display without hitting 'Submit Source'


    def reset_input_section_state(self):
        # Existing logic modified for the new frame structure
        for widget in self.input_section.winfo_children():
            widget.destroy()
        self.input_section_placeholder_label = ctk.CTkLabel(self.input_section, text="Please select a data source and click 'Submit Source'.", wraplength=400, justify="center", text_color="#3A3B5B")
        self.input_section_placeholder_label.pack(pady=40)

        self.entries.clear()
        self.file_path.set("No file selected")
        self.df = None
        self.connect_load_button.configure(state="disabled")
        # No need for update_analysis_buttons_state here, as it's done when switching views
        # Also, the dashboard prompt and results are separate
        if self.dashboard_analysis_results:
            self.dashboard_analysis_results.configure(text="AI insights will appear here after you ask a question.")
        if self.summary_label:
            self.summary_label.configure(text="Click 'Generate Summary' to see insights.")
        if self.result_label:
            self.result_label.configure(text="AI analysis results will be displayed here.")


    def reset_application(self):
        # Full reset, similar to before but adapted for the new view management
        self.data_source.set("--- Select Source ---")
        self.file_path.set("No file selected")
        self.df = None
        self.entries.clear()

        # Reset all dynamic input sections and results
        self.reset_input_section_state()

        # Hide all loading indicators
        self.loading_label_data_load.pack_forget()
        if hasattr(self, 'loading_label_summary'): self.loading_label_summary.pack_forget()
        if hasattr(self, 'loading_label_analysis'): self.loading_label_analysis.pack_forget()


        self.connect_load_button.configure(state="disabled")
        self.submit_source_button.configure(state="disabled")
        # Ensure summary/analyze buttons are disabled
        if hasattr(self, 'summarize_button'): self.summarize_button.configure(state="disabled")
        if hasattr(self, 'analyze_button'): self.analyze_button.configure(state="disabled")
        if hasattr(self, 'left_nav_ask_button'): self.left_nav_ask_button.configure(state="normal") # AI in nav is always active

        # Switch back to dashboard view
        self.show_view("dashboard")
        messagebox.showinfo("Reset", "Application has been reset to its initial state.")


    def display_source_inputs(self):
        # Existing logic, ensure text colors and background match new theme
        self.input_section_placeholder_label.pack_forget()
        for widget in self.input_section.winfo_children():
            widget.destroy()

        self.entries.clear()
        self.file_path.set("No file selected")
        self.df = None
       
        source = self.data_source.get()

        label_kwargs = {"text_color": "#3A3B5B", "width": 180, "anchor": "w"}
        entry_kwargs = {"fg_color": "white", "border_color": "#DEDFE3", "text_color": "#3A3B5B", "width": 300}


        if source == "Excel/CSV":
            ctk.CTkLabel(self.input_section, text="Select CSV or Excel File:", **label_kwargs).pack(pady=5)
            file_row = ctk.CTkFrame(self.input_section, fg_color="transparent")
            file_row.pack(pady=5)
            ctk.CTkButton(file_row, text="Browse", command=self.browse_file, fg_color="#0066CC", hover_color="#0052A3").pack(side="left", padx=5)
            ctk.CTkLabel(file_row, textvariable=self.file_path, text_color="#3A3B5B").pack(side="left", padx=5)
            self.connect_load_button.configure(text="Load File", state="disabled")

        elif source == "SQL Database":
            fields = [("Dialect (e.g., mysql+pymysql, sqlite)", "dialect"),
                      ("Username", "username"),
                      ("Password", "password"),
                      ("Host", "host"),
                      ("Port", "port"),
                      ("Database", "database"),
                      ("SQL Query (e.g., SELECT * FROM my_table)", "sql_query")]
            
            for display_name, key_name in fields:
                field_frame = ctk.CTkFrame(self.input_section, fg_color="transparent")
                field_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(field_frame, text=f"{display_name}:", **label_kwargs).pack(side="left", padx=5)
                entry = ctk.CTkEntry(field_frame, show="*" if "password" in key_name else None, **entry_kwargs)
                entry.pack(side="left", fill="x", expand=True, padx=5)
                self.entries[key_name] = entry
            self.connect_load_button.configure(text="Connect to Database", state="normal")

        elif source == "SharePoint List":
            fields = [("Site URL (e.g., https://org.sharepoint.com/sites/team)", "site_url"),
                      ("List Name (e.g., 'Documents')", "list_name"),
                      ("Client ID (Azure AD App Registration)", "client_id"),
                      ("Client Secret (Azure AD App Registration)", "client_secret")]
            
            for display_name, key_name in fields:
                field_frame = ctk.CTkFrame(self.input_section, fg_color="transparent")
                field_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(field_frame, text=f"{display_name}:", **label_kwargs).pack(side="left", padx=5)
                entry = ctk.CTkEntry(field_frame, show="*" if "secret" in key_name else None, **entry_kwargs)
                entry.pack(side="left", fill="x", expand=True, padx=5)
                self.entries[key_name] = entry
            self.connect_load_button.configure(text="Connect to SharePoint", state="normal")
        
        else:
            self.connect_load_button.configure(state="disabled")


    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("CSV/Excel files", "*.csv *.xlsx")])
        if file:
            self.file_path.set(file)
            self.connect_load_button.configure(state="normal")
        else:
            self.file_path.set("No file selected")
            self.connect_load_button.configure(state="disabled")

    def perform_data_load(self):
        self.loading_label_data_load.pack(pady=5)
        self.root.update_idletasks()

        source = self.data_source.get()
        if source == "--- Select Source ---":
            messagebox.showwarning("Selection Error", "Please select a valid data source before connecting/loading.")
            self.loading_label_data_load.pack_forget()
            return

        try:
            if source == "Excel/CSV":
                if not self.file_path.get() or self.file_path.get() == "No file selected":
                    messagebox.showerror("Error", "Please select an Excel or CSV file first.")
                    self.df = None
                    return
                self.df = backend.load_excel_csv(self.file_path.get())
                messagebox.showinfo("Success", "File loaded successfully!")
            elif source == "SQL Database":
                params = {k: v.get() for k, v in self.entries.items()}
                required_sql_fields = ["dialect", "username", "password", "host", "port", "database", "sql_query"]
                if not all(params.get(key) for key in required_sql_fields):
                     messagebox.showerror("Input Error", "Please fill all SQL database connection details and the SQL query.")
                     self.df = None
                     return
                self.df = backend.load_sql_table(
                    params["dialect"], params["username"], params["password"],
                    params["host"], params["port"], params["database"], params["sql_query"]
                )
                messagebox.showinfo("Success", "SQL data loaded successfully!")
            elif source == "SharePoint List":
                params = {k: v.get() for k, v in self.entries.items()}
                required_sp_fields = ["site_url", "list_name", "client_id", "client_secret"]
                if not all(params.get(key) for key in required_sp_fields):
                     messagebox.showerror("Input Error", "Please fill all SharePoint connection details.")
                     self.df = None
                     return
                self.df = backend.load_sharepoint_list(
                    params["site_url"], params["list_name"], params["client_id"], params["client_secret"]
                )
                messagebox.showinfo("Success", "SharePoint data loaded successfully!")
            
            # If data load was successful, ensure relevant buttons are enabled and switch views
            self.update_analysis_buttons_state(True) # This now affects buttons in summary/analysis views
            if self.summary_label: self.summary_label.configure(text="Click 'Generate Summary' to see insights.") # Reset summary text
            if self.result_label: self.result_label.configure(text="AI analysis results will be displayed here.") # Reset analysis text
            if self.dashboard_analysis_results: self.dashboard_analysis_results.configure(text="AI insights will appear here after you ask a question.")

            self.show_view("summary_results") # Automatically switch to summary view after loading


        except Exception as e:
            messagebox.showerror("Connection/Load Error", str(e))
            self.df = None
            self.update_analysis_buttons_state(False) # Disable buttons if loading fails
        finally:
            self.loading_label_data_load.pack_forget()

    def update_analysis_buttons_state(self, enabled=False):
        """Enables or disables the Summarize and Analyze buttons in their respective views."""
        state = "normal" if enabled and self.df is not None else "disabled"
        if hasattr(self, 'summarize_button'): self.summarize_button.configure(state=state)
        if hasattr(self, 'analyze_button'): self.analyze_button.configure(state=state)
        # Note: Left nav ask button remains enabled, it handles its own df check
        # Dashboard ask button also handles its own df check inside run_analysis_from_dashboard

    def summarize_data(self):
        if self.df is not None:
            self.loading_label_summary.pack(pady=5)
            self.summary_label.configure(text="")
            self.root.update_idletasks()

            try:
                summary_text = backend.summarize_dataframe(self.df)
                self.summary_label.configure(text=summary_text)
            except Exception as e:
                messagebox.showerror("Summary Error", str(e))
                self.summary_label.configure(text="Error generating summary.")
            finally:
                self.loading_label_summary.pack_forget()
        else:
            messagebox.showerror("Summary Error", "No data loaded to summarize. Please connect to a data source first using the 'Data Connection' section.")
            self.summary_label.configure(text="No data loaded yet.")

    def run_analysis(self):
        # This is for the dedicated Analysis view
        if self.df is None:
            messagebox.showerror("Analysis Error", "No data loaded to analyze. Please connect to a data source first using the 'Data Connection' section.")
            self.result_label.configure(text="No data loaded yet.")
            return

        prompt_text = self.prompt_entry.get()
        if not prompt_text:
            messagebox.showwarning("Input Warning", "Please enter a question for the AI analysis.")
            return

        self.loading_label_analysis.pack(pady=5)
        self.result_label.configure(text="")
        self.root.update_idletasks()

        try:
            answer = backend.analyse_dataframe(self.df, prompt_text)
            self.result_label.configure(text=answer)
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))
            self.result_label.configure(text="Error during analysis.")
        finally:
            self.loading_label_analysis.pack_forget()

    def run_analysis_from_nav(self):
        # This handles the "Ask AI" button in the left navigation
        prompt_text = self.left_nav_prompt_entry.get()
        if not prompt_text:
            messagebox.showwarning("Input Warning", "Please enter a question in the left nav's 'Ask AI' field.")
            return
        
        if self.df is None:
            messagebox.showwarning("Data Missing", "No data loaded yet for analysis. Please load data first.")
            return

        # Perform analysis and display in analysis view
        self.show_view("analysis_query")
        # Now trigger the analysis in the analysis view's context
        self.prompt_entry.delete(0, ctk.END) # Clear existing prompt in main analysis view
        self.prompt_entry.insert(0, prompt_text) # Insert the nav prompt
        self.run_analysis() # Run analysis from the main analysis function
        self.left_nav_prompt_entry.delete(0, ctk.END) # Clear nav prompt after transfer


    def run_analysis_from_dashboard(self):
        # This handles the "Ask AI" button in the dashboard's "Your Questions" section
        prompt_text = self.dashboard_prompt_entry.get()
        if not prompt_text:
            messagebox.showwarning("Input Warning", "Please enter a question in the dashboard's 'Your Questions' field.")
            return
        
        if self.df is None:
            self.dashboard_analysis_results.configure(text="No data loaded yet for analysis. Please load data first.")
            return

        self.dashboard_analysis_results.configure(text="Analyzing...", text_color="#3A3B5B")
        self.root.update_idletasks()

        try:
            answer = backend.analyse_dataframe(self.df, prompt_text)
            self.dashboard_analysis_results.configure(text=answer, text_color="#3A3B5B")
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))
            self.dashboard_analysis_results.configure(text=f"Error: {e}", text_color="red")
        finally:
            self.dashboard_prompt_entry.delete(0, ctk.END) # Clear prompt after analysis


if __name__ == "__main__":
    root = ctk.CTk()
    app = DataWizardApp(root)
    root.mainloop()