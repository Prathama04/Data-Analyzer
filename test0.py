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
        # Ensure these image files exist in the same directory as your script
        self.icon_data_connection = self.load_icon("data_connection_icon.png", (24, 24)) # Example icon names
        self.icon_summarize_data = self.load_icon("summarize_data_icon.png", (24, 24))
        self.icon_analyze_data = self.load_icon("analyze_data_icon.png", (24, 24))

        self.build_main_layout()

    def load_icon(self, path, size):
        """Helper to load and resize images for icons."""
        try:
            img = Image.open(path).resize(size)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except FileNotFoundError:
            print(f"Warning: {path} not found. Icon will not be displayed.")
            return None # Return None if image not found

    def build_main_layout(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(fg_color="#4B0082") 

        # Create a main container frame that fills the entire root window
        self.main_container_frame = ctk.CTkFrame(self.root, fg_color="#4B0082", corner_radius=0)
        self.main_container_frame.pack(fill="both", expand=True) # Use pack to make it fill the root

        # Now, configure the grid for this container frame.
        # This is where your sidebar and main content will be gridded.
        self.main_container_frame.grid_columnconfigure(0, weight=0) # Sidebar column - fixed width
        self.main_container_frame.grid_columnconfigure(1, weight=1) # Main content column - expands
        self.main_container_frame.grid_rowconfigure(0, weight=1) # The single row of the main container - expands


        self.sidebar_frame = ctk.CTkFrame(self.main_container_frame, # Parent is now main_container_frame
                                          width=280, 
                                          corner_radius=0, 
                                          fg_color="#3A2B5B") 
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")


        self.main_content_frame = ctk.CTkFrame(self.main_container_frame, # Parent is now main_container_frame
                                               corner_radius=0, 
                                               fg_color="#5D40A4") 
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")

        # --- Configure Grid for Sidebar Frame Contents ---
        self.sidebar_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 9), weight=0) 
        self.sidebar_frame.grid_rowconfigure(8, weight=1) 
        
        current_row = 0

        # --- 1. App Title and Subtitle ---
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

        # Subtitle
        ctk.CTkLabel(self.sidebar_frame, text="✨ AI-Powered", 
                     font=("Arial", 18), text_color="#A9A9A9").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(0, 30), sticky="w")
        current_row += 1 

        # --- 2. Tagline ---
        ctk.CTkLabel(self.sidebar_frame, text="Your Personal Assistant in the Digital Realm", 
                     font=("Arial", 20, "bold"), text_color="white", wraplength=240, justify="left").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")
        current_row += 1 
        
        # --- 3. Description ---
        ctk.CTkLabel(self.sidebar_frame, text="Connect, analyze, and discover insights from your data with the power of artificial intelligence.", 
                     font=("Arial", 16), text_color="#D3D3D3", wraplength=240, justify="left").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="w")
        current_row += 1 

        # --- 4. Key Features Section ---
        ctk.CTkLabel(self.sidebar_frame, text="Key Features", 
                     font=("Arial", 25, "bold"), text_color="white").grid(row=current_row, column=0, columnspan=2, padx=20, pady=(40, 10), sticky="w")
        current_row += 1 

        # Helper function for feature items
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

        # Feature Item 1
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

        # --- Flexible Spacer Row ---
        self.sidebar_frame.grid_rowconfigure(current_row, weight=1)
        current_row += 1 

        # --- 5. Bottom Image ---
        try:
            bottom_image_path = "org_logo.png" 
            bottom_img = Image.open(bottom_image_path).resize((300, 80)) 
            self.bottom_img_ctk = ctk.CTkImage(light_image=bottom_img, dark_image=bottom_img, size=(300, 80))
            ctk.CTkLabel(self.sidebar_frame, text="", image=self.bottom_img_ctk).grid(row=current_row, column=0, columnspan=2, pady=(20, 20), sticky="s")
        except FileNotFoundError:
            ctk.CTkLabel(self.sidebar_frame, text="[Your Organization Logo]", font=("Arial", 14), text_color="#D3D3D3").grid(row=current_row, column=0, columnspan=2, pady=(20, 20), sticky="s")
            print(f"Warning: {bottom_image_path} not found. Showing text placeholder.")


        # --- Main Content Area Population ---
        # Configure the grid for the main_content_frame to hold header, separator, and tabview
        self.main_content_frame.grid_columnconfigure(0, weight=1) 
        self.main_content_frame.grid_rowconfigure(0, weight=0) 
        self.main_content_frame.grid_rowconfigure(1, weight=0) 
        self.main_content_frame.grid_rowconfigure(2, weight=1) 

        # Main Content Header
        ctk.CTkLabel(self.main_content_frame, text="🚀 Data Analyzer", 
                     font=("Arial", 30, "bold"), text_color="white", anchor="w").grid(row=0, column=0, padx=40, pady=(30, 10), sticky="ew")

        # Horizontal Separator Line
        ctk.CTkFrame(self.main_content_frame, height=2, fg_color="#7B68EE", corner_radius=0).grid(row=1, column=0, padx=30, pady=(0, 20), sticky="ew")


        # Create the CTkTabview
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

        # Configure the font and border_spacing AFTER the tabview is created
        # Access the internal _segmented_button widget and configure its properties
        if hasattr(self.tabview, '_segmented_button'):
            self.tabview._segmented_button.configure(font=("Arial", 20, "bold"))


        # Add the tabs with icons
        tab_data = [
            ("1. Data Connection", self.icon_data_connection),
            ("2. Summarize Data", self.icon_summarize_data),
            ("3. Analyze Data", self.icon_analyze_data)
        ]

        for text, icon in tab_data:
            tab = self.tabview.add(text)
            # Find the actual CTkButton widget for the tab to set its image
            if hasattr(self.tabview, '_segmented_button'): # Add check for safety
                for child in self.tabview._segmented_button.winfo_children():
                    if isinstance(child, ctk.CTkButton) and child.cget("text") == text:
                        if icon:
                            child.configure(image=icon, compound="left")
                        break


        # Set default active tab
        self.tabview.set("1. Data Connection")


        # Placeholder content for each tab
        ctk.CTkLabel(self.tabview.tab("1. Data Connection"), text="Data Connection Form will go here", text_color="white", font=("Arial", 18)).pack(pady=20)
        ctk.CTkLabel(self.tabview.tab("2. Summarize Data"), text="Data Summary UI will go here", text_color="white", font=("Arial", 18)).pack(pady=20)
        ctk.CTkLabel(self.tabview.tab("3. Analyze Data"), text="Data Analysis UI will go here", text_color="white", font=("Arial", 18)).pack(pady=20)


    def clear_frame_widgets(self, frame):
        """Helper method to destroy all widgets within a given frame."""
        for widget in frame.winfo_children():
            widget.destroy()

    def show_dashboard_view(self):
        pass


# --- Application Entry Point ---
if __name__ == "__main__":
    root = ctk.CTk()
    app = DataAnalyzerApp(root)
    root.mainloop()