import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import pandas as pd
import backend

class DataWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyzer")
        self.root.geometry("710x610")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.data_source = ctk.StringVar()
        self.prompt = ctk.StringVar()
        self.file_path = ctk.StringVar()
        self.df = None
        self.entries = {}

        self.build_main_layout()

    def build_main_layout(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Delay prompt reset to avoid errors
        self.root.after(100, lambda: self.prompt.set(""))

        # Add scrollable frame setup
        canvas_frame = ctk.CTkFrame(self.root)
        canvas_frame.pack(side="left", fill="both", expand=True)

        canvas = ctk.CTkCanvas(canvas_frame, cursor="arrow")
        scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=canvas.yview)
        self.scrollable_area = ctk.CTkFrame(canvas)

        self.scrollable_area.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_area, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sidebar
        sidebar = ctk.CTkFrame(self.scrollable_area, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="Hi, I am Data Analyzer", font=("Arial", 16, "bold"), wraplength=180).pack(pady=(20, 10))
        ctk.CTkLabel(sidebar, text="Your Personal Assistant\nin the Digital Realm", wraplength=180, justify="center").pack(pady=5)

        # Organization logo in bottom-left
        try:
            org_image = Image.open("org_logo.png").resize((200, 80))
            org_logo = ctk.CTkImage(light_image=org_image, dark_image=org_image, size=(200, 80))
            org_label = ctk.CTkLabel(sidebar, image=org_logo, text="")
            org_label.image = org_logo
            org_label.pack(side="bottom", pady=10)
        except:
            pass

        main_area = ctk.CTkFrame(self.scrollable_area)
        main_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_area, text="DATA ANALYZER", font=("Arial", 20, "bold")).pack(pady=10)

        # Data source dropdown
        source_frame = ctk.CTkFrame(main_area)
        source_frame.pack(pady=10)
        ctk.CTkLabel(source_frame, text="Choose Data Source from the drop-down::").pack(pady=5)
        self.source_menu = ctk.CTkOptionMenu(source_frame, variable=self.data_source,
                                             values=["Excel/CSV", "SQL Database", "SharePoint List"])
        self.source_menu.pack(pady=5)

        # Buttons
        button_row = ctk.CTkFrame(source_frame)
        button_row.pack(pady=10)
        ctk.CTkButton(button_row, text="Upload", command=self.load_source_screen).pack(side="left", padx=5)
        ctk.CTkButton(button_row, text="Back", command=self.build_main_layout).pack(side="left", padx=5)

        # Input section placeholder
        self.input_section = ctk.CTkFrame(main_area)
        self.input_section.pack(pady=10)

        # Summarize button
        self.summarize_button = ctk.CTkButton(main_area, text="Summarize Dataset", command=self.summarize_data)
        self.summarize_button.pack(pady=10)

        self.summary_label = ctk.CTkLabel(main_area, text="", wraplength=600, justify="left")
        self.summary_label.pack(pady=10)

        # Prompt & Result
        self.prompt_entry = ctk.CTkEntry(main_area, textvariable=self.prompt,
                                         placeholder_text="Ask your question...", width=500)
        self.prompt_entry.pack(pady=10)
        ctk.CTkButton(main_area, text="Analyze", command=self.run_analysis).pack(pady=10)

        self.result_label = ctk.CTkLabel(main_area, text="", wraplength=600, justify="left")
        self.result_label.pack(pady=20)

    def load_source_screen(self):
        # Clear previous inputs
        for widget in self.input_section.winfo_children():
            widget.destroy()

        for field in list(self.entries):
            try:
                self.entries[field].destroy()
            except:
                pass
        self.entries.clear()

        source = self.data_source.get()
        if source == "Excel/CSV":
            ctk.CTkLabel(self.input_section, text="Upload CSV or Excel File").pack()
            ctk.CTkButton(self.input_section, text="Browse", command=self.browse_file).pack(pady=10)
            ctk.CTkLabel(self.input_section, textvariable=self.file_path).pack()

        elif source == "SQL Database":
            fields = ["Dialect (e.g., mysql/postgresql)", "Username", "Password", "Host", "Port", "Database", "SQL Query"]
            for field in fields:
                ctk.CTkLabel(self.input_section, text=field).pack()
                entry = ctk.CTkEntry(self.input_section, show="*" if "Password" in field or "Secret" in field else None)
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
            try:
                self.df = backend.load_excel_csv(file)
                messagebox.showinfo("Success", "File loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def summarize_data(self):
        if self.df is not None:
            self.summary_label.configure(
                text="This is a hardcoded summary: The dataset contains X rows and Y columns. Major trends include..."
            )
        else:
            messagebox.showerror("Summary Error", "No data loaded to summarize.")

    def run_analysis(self):
        try:
            source = self.data_source.get()
            if source == "Excel/CSV" and self.df is None:
                self.df = backend.load_excel_csv(self.file_path.get())
            elif source == "SQL Database":
                values = [self.entries[f].get() for f in self.entries]
                self.df = backend.load_sql_table(*values)
            elif source == "SharePoint List":
                values = [self.entries[f].get() for f in self.entries]
                self.df = backend.load_sharepoint_list(*values)

            answer = backend.analyse_dataframe(self.df, self.prompt.get())
            self.result_label.configure(text=answer)

        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))


if __name__ == "__main__":
    root = ctk.CTk()
    app = DataWizardApp(root)
    root.mainloop()
