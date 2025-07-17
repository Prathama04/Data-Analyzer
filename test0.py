import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

class DataWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyzer - Tabbed Layout")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.data_source = ctk.StringVar()
        self.file_path = ctk.StringVar()
        self.df = None
        self.entries = {}
        self.build_main_layout()

    def build_main_layout(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Sidebar
        sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(sidebar, text="Data Analyzer", font=("Arial", 16, "bold"), wraplength=180).pack(pady=(20, 10))
        ctk.CTkLabel(sidebar, text="Your Data Assistant", wraplength=180, justify="center").pack(pady=5)
        try:
            org_image = Image.open("org_logo.png").resize((200, 80))
            org_logo = ctk.CTkImage(light_image=org_image, dark_image=org_image, size=(200, 80))
            org_label = ctk.CTkLabel(sidebar, image=org_logo, text="")
            org_label.image = org_logo
            org_label.pack(side="bottom", pady=10)
        except:
            pass

        # Tabview
        tabview = ctk.CTkTabview(self.root)
        tabview.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        tabview.add("Data Source")
        tabview.add("Explore Data")
        tabview.add("Analyze")

        # Data Source Tab
        source_frame = ctk.CTkFrame(tabview.tab("Data Source"))
        source_frame.pack(pady=20, padx=20, fill="both")
        ctk.CTkLabel(source_frame, text="Choose Data Source", font=("Arial", 14)).pack(pady=5)
        self.source_menu = ctk.CTkOptionMenu(source_frame, variable=self.data_source, values=["Excel/CSV", "SQL Database", "SharePoint List"])
        self.source_menu.pack(pady=5)
        self.input_section = ctk.CTkFrame(source_frame)
        self.input_section.pack(pady=10, fill="x")
        ctk.CTkButton(source_frame, text="Load", command=self.load_source_screen).pack(pady=10)

        # Explore Data Tab
        explore_frame = ctk.CTkFrame(tabview.tab("Explore Data"))
        explore_frame.pack(pady=20, padx=20, fill="both")
        self.summary_label = ctk.CTkLabel(explore_frame, text="No data loaded.", wraplength=500, justify="left")
        self.summary_label.pack(pady=10)
        ctk.CTkButton(explore_frame, text="Summarize Dataset", command=self.summarize_data).pack(pady=10)

        # Analyze Tab
        analyze_frame = ctk.CTkFrame(tabview.tab("Analyze"))
        analyze_frame.pack(pady=20, padx=20, fill="both")
        self.prompt_entry = ctk.CTkEntry(analyze_frame, placeholder_text="Ask your question...", width=400)
        self.prompt_entry.pack(pady=10)
        ctk.CTkButton(analyze_frame, text="Analyze", command=self.run_analysis).pack(pady=10)
        self.result_label = ctk.CTkLabel(analyze_frame, text="", wraplength=500, justify="left")
        self.result_label.pack(pady=10)

    def load_source_screen(self):
        for widget in self.input_section.winfo_children():
            widget.destroy()
        source = self.data_source.get()
        if source == "Excel/CSV":
            ctk.CTkLabel(self.input_section, text="Upload CSV or Excel File").pack(pady=5)
            ctk.CTkButton(self.input_section, text="Browse", command=self.browse_file).pack(pady=5)
            ctk.CTkLabel(self.input_section, textvariable=self.file_path).pack(pady=5)
        elif source == "SQL Database":
            fields = ["Dialect", "Username", "Password", "Host", "Port", "Database", "SQL Query"]
            for field in fields:
                ctk.CTkLabel(self.input_section, text=field).pack()
                entry = ctk.CTkEntry(self.input_section, show="*" if "Password" in field else None)
                entry.pack(pady=5)
                self.entries[field] = entry
        elif source == "SharePoint List":
            fields = ["Site URL", "List Name", "Client ID", "Client Secret"]
            for field in fields:
                ctk.CTkLabel(self.input_section, text=field).pack()
                entry = ctk.CTkEntry(self.input_section, show="*" if "Secret" in field else None)
                entry.pack(pady=5)
                self.entries[field] = entry

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("CSV/Excel", "*.csv *.xlsx")])
        self.file_path.set(file)
        if file:
            messagebox.showinfo("Success", "File loaded successfully!")

    def summarize_data(self):
        self.summary_label.configure(text="Dataset Summary: [Placeholder for demo]")

    def run_analysis(self):
        self.result_label.configure(text="Analysis Result: [Placeholder for demo]")

if __name__ == "__main__":
    root = ctk.CTk()
    app = DataWizardApp(root)
    root.mainloop()