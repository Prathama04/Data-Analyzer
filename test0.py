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


        self.build_main_layout()

    def build_main_layout(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.grid_columnconfigure(0, weight=0) 
        self.root.grid_columnconfigure(1, weight=1) 
        self.root.grid_rowconfigure(0, weight=1) 

        self.root.configure(fg_color="#4B0082") 

        self.sidebar_frame = ctk.CTkFrame(self.root, 
                                          width=280, 
                                          corner_radius=0, 
                                          fg_color="#3A2B5B") 
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")


        self.main_content_frame = ctk.CTkFrame(self.root, 
                                               corner_radius=0, 
                                               fg_color="#5D40A4") 
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")

        self.sidebar_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 9), weight=0) # All content rows fixed weight
        self.sidebar_frame.grid_rowconfigure(8, weight=1) # This is the flexible spacer row
        
        # New Row Assignments for clarity and correct spacing
        current_row = 0

        # --- 1. App Title and Subtitle ---
        # Load the Data Analyzer icon from your design (assuming a placeholder PNG)
        try:
            
            app_icon_img = Image.open("icon_app_analyzer.png").resize((50, 50)) 
            self.app_icon_ctk = ctk.CTkImage(light_image=app_icon_img, dark_image=app_icon_img, size=(50, 50))
            ctk.CTkLabel(self.sidebar_frame, text="", image=self.app_icon_ctk).grid(row=current_row, column=0, padx=20, pady=(30, 5), sticky="nw")
        except FileNotFoundError:
            ctk.CTkLabel(self.sidebar_frame, text="📊", font=("Arial", 24), text_color="white").grid(row=current_row, column=0, padx=20, pady=(30, 5), sticky="nw")
            print("Warning: icon_app_analyzer.png not found. Showing text placeholder.")

        ctk.CTkLabel(self.sidebar_frame, text="Data Analyzer", 
                     font=("Arial", 30, "bold"), text_color="white").grid(row=current_row, column=1, padx=(0, 20), pady=(30, 5), sticky="nw")
        current_row += 1 # Move to next row

        # Grid column for title/icon
        self.sidebar_frame.grid_columnconfigure(0, weight=0) # Icon column
        self.sidebar_frame.grid_columnconfigure(1, weight=1) # Title column (expands)

        # Subtitle
        ctk.CTkLabel(self.sidebar_frame, text="✨ AI-Powered", 
                     font=("Arial", 18), text_color="#A9A9A9").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(0, 30), sticky="w")
        current_row += 1 # Move to next row

        # --- 2. Tagline ---
        ctk.CTkLabel(self.sidebar_frame, text="Your Personal Assistant in the Digital Realm", 
                     font=("Arial", 20, "bold"), text_color="white", wraplength=240, justify="left").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")
        current_row += 1 # Move to next row
        
        # --- 3. Description ---
        
        # Add a small pady to separate from tagline if desired.
        ctk.CTkLabel(self.sidebar_frame, text="Connect, analyze, and discover insights from your data with the power of artificial intelligence.", 
                     font=("Arial", 16), text_color="#D3D3D3", wraplength=240, justify="left").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="w")
        current_row += 1 # Move to next row

        # --- 4. Key Features Section ---
        # Add some top padding to separate from the description above.
        ctk.CTkLabel(self.sidebar_frame, text="Key Features", 
                     font=("Arial", 25, "bold"), text_color="white").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(40, 10), sticky="w")
        current_row += 1 # Move to next row

        # Helper function for feature items
        def create_feature_item(parent, icon_path, title, description, row_num): # Use row_num to avoid conflict with outer 'row'
            item_frame = ctk.CTkFrame(parent, fg_color="transparent")
            # pady=8 instead of 5 for more spacing with larger fonts
            item_frame.grid(row=row_num, column=0, columnspan=2, sticky="ew", padx=20, pady=8) 
            item_frame.grid_columnconfigure(0, weight=0) # Icon column
            item_frame.grid_columnconfigure(1, weight=1) # Text column

            try:
                # Icon size matching your requested (30,30)
                icon_img = Image.open(icon_path).resize((30, 30)) 
                icon_ctk = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(30, 30))
                ctk.CTkLabel(item_frame, text="", image=icon_ctk).grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="nw") # sticky changed to nw
            except FileNotFoundError:
                ctk.CTkLabel(item_frame, text="•", font=("Arial", 25), text_color="#87CEEB").grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="nw") # Increased font for placeholder
                print(f"Warning: {icon_path} not found. Showing text placeholder.")

            # Font sizes adjusted based on your request
            ctk.CTkLabel(item_frame, text=title, font=("Arial", 20, "bold"), text_color="white", anchor="w").grid(row=0, column=1, sticky="ew")
            ctk.CTkLabel(item_frame, text=description, font=("Arial", 14), text_color="#A9A9A9", wraplength=180, justify="left", anchor="w").grid(row=1, column=1, sticky="ew")

            return item_frame

        # Feature Item 1: This is now placed in current_row
        create_feature_item(self.sidebar_frame, "icon_multi_source.png", 
                            "Multi-Source Connection", "Excel, SQL, SharePoint", current_row)
        current_row += 1

        # Feature Item 2
        create_feature_item(self.sidebar_frame, "icon_summarization.png", 
                            "Smart Summarization", "Instant data insights", current_row)
        current_row += 1

        # Feature Item 3
        create_feature_item(self.sidebar_frame, "icon_ai_analysis.png", 
                            "AI Analysis", "Natural language queries", current_row)
        current_row += 1

        self.sidebar_frame.grid_rowconfigure(current_row, weight=1)
        current_row += 1 # Move past the flexible spacer row

        # --- 5. Bottom Image ---
        try:
            bottom_image_path = "org_logo.png" 
            bottom_img = Image.open(bottom_image_path).resize((300, 80)) 
            self.bottom_img_ctk = ctk.CTkImage(light_image=bottom_img, dark_image=bottom_img, size=(300, 80))
            # Place in the row AFTER the flexible spacer
            ctk.CTkLabel(self.sidebar_frame, text="", image=self.bottom_img_ctk).grid(row=current_row, column=0, columnspan=2, pady=(20, 20), sticky="s")
        except FileNotFoundError:
            # Uncommented and adjusted font size for placeholder
            ctk.CTkLabel(self.sidebar_frame, text="[Your Organization Logo]", font=("Arial", 14), text_color="#D3D3D3").grid(row=current_row, column=0, columnspan=2, pady=(20, 20), sticky="s")
            print(f"Warning: {bottom_image_path} not found. Showing text placeholder.")


        # Continue with the placeholder for main content
        self.show_dashboard_view() 


    def clear_frame_widgets(self, frame):
        """Helper method to destroy all widgets within a given frame."""
        for widget in frame.winfo_children():
            widget.destroy()

    def show_dashboard_view(self):
        """Placeholder for the method that will display the dashboard content."""
        self.clear_frame_widgets(self.main_content_frame)
        ctk.CTkLabel(self.main_content_frame, text="Main Content Area (Tabs) Will Go Here",
                     font=("Arial", 24, "bold"), text_color="white").pack(pady=100)


# --- Application Entry Point ---
if __name__ == "__main__":
    root = ctk.CTk()
    app = DataAnalyzerApp(root)
    root.mainloop()