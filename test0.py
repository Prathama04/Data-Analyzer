import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import pandas as pd
import backend1

class DataWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyzer")
        self.root.geometry("710x680")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Initialize state variables
        self.data_source = ctk.StringVar(value="Excel/CSV")
        self.file_path = ctk.StringVar(value="No file selected")
        self.df = None
        self.entries = {}

        self.build_main_layout()

    def build_main_layout(self):
        # Clear previous widgets to rebuild the layout
        for widget in self.root.winfo_children():
            widget.destroy()

        canvas_frame = ctk.CTkFrame(self.root)
        canvas_frame.pack(side="left", fill="both", expand=True)

        canvas = ctk.CTkCanvas(canvas_frame, cursor="arrow")
        scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=canvas.yview)
        self.scrollable_area = ctk.CTkFrame(canvas)

        self.scrollable_area.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_area, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sidebar
        sidebar = ctk.CTkFrame(self.scrollable_area, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(sidebar, text="Hi, I am Data Analyzer", font=("Arial", 16, "bold"), wraplength=180).pack(pady=(20, 10))
        ctk.CTkLabel(sidebar, text="Your Personal Assistant\nin the Digital Realm", wraplength=180, justify="center").pack(pady=5)
        try:
            org_image = Image.open("org_logo.png").resize((200, 80))
            org_logo = ctk.CTkImage(light_image=org_image, dark_image=org_image, size=(200, 80))
            org_label = ctk.CTkLabel(sidebar, image=org_logo, text="")
            org_label.image = org_logo
            org_label.pack(side="bottom", pady=10)
        except:
            pass

        # Main area
        main_area = ctk.CTkFrame(self.scrollable_area)
        main_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_area, text="DATA ANALYZER", font=("Arial", 20, "bold")).pack(pady=10)

        # --- Data Source Selection ---
        source_selection_frame = ctk.CTkFrame(main_area)
        source_selection_frame.pack(pady=10)
        ctk.CTkLabel(source_selection_frame, text="Choose Data Source:").pack(side="left", padx=5)
        self.source_menu = ctk.CTkOptionMenu(source_selection_frame, variable=self.data_source,
                                             values=["Excel/CSV", "SQL Database", "SharePoint List"])
        self.source_menu.pack(side="left", padx=5)
        self.submit_source_button = ctk.CTkButton(source_selection_frame, text="Submit Source", command=self.display_source_inputs)
        self.submit_source_button.pack(side="left", padx=15)

        # --- Dynamic Input Section ---
        self.input_section = ctk.CTkFrame(main_area)
        self.input_section.pack(pady=10, fill="x", padx=20)

        # --- Connect/Load and Back Buttons ---
        action_buttons_frame = ctk.CTkFrame(main_area)
        action_buttons_frame.pack(pady=15)

        self.connect_load_button = ctk.CTkButton(action_buttons_frame, text="Connect/Load Data", command=self.perform_data_load, state="disabled")
        self.connect_load_button.pack(side="left", padx=10)

        # New Back Button
        self.back_button = ctk.CTkButton(action_buttons_frame, text="Reset / Back", command=self.reset_application)
        self.back_button.pack(side="left", padx=10)

        # Loading indicator for data loading
        self.loading_label_data_load = ctk.CTkLabel(main_area, text="Loading data...", font=("Arial", 14, "italic"))
        self.loading_label_data_load.pack_forget()

        # --- Summarize Section ---
        self.summarize_button = ctk.CTkButton(main_area, text="Summarize Dataset", command=self.summarize_data, state="disabled")
        self.summarize_button.pack(pady=20)

        self.summary_label = ctk.CTkLabel(main_area, text="AI summary will appear here.", wraplength=600, justify="left")
        self.summary_label.pack(pady=10)

        # Loading indicator for summary
        self.loading_label_summary = ctk.CTkLabel(main_area, text="Generating summary...", font=("Arial", 14, "italic"))
        self.loading_label_summary.pack_forget()

        # --- Analysis Section ---
        self.prompt_entry = ctk.CTkEntry(main_area, placeholder_text="Ask your question...", width=500)
        self.prompt_entry.pack(pady=10)

        self.analyze_button = ctk.CTkButton(main_area, text="Analyze", command=self.run_analysis, state="disabled")
        self.analyze_button.pack(pady=10)

        # Loading indicator for analysis
        self.loading_label_analysis = ctk.CTkLabel(main_area, text="Analyzing data...", font=("Arial", 14, "italic"))
        self.loading_label_analysis.pack_forget()

        self.result_label = ctk.CTkLabel(main_area, text="AI analysis results will be displayed here.", wraplength=600, justify="left")
        self.result_label.pack(pady=20)

        # Initialize the state (display Excel/CSV inputs by default and disable analysis buttons)
        self.display_source_inputs() # This will also set the initial state of connect_load_button
        self.update_analysis_buttons_state(False) # Ensure analyze/summarize are disabled

    def reset_application(self):
        """Resets the application to its initial state."""
        # Reset state variables
        self.data_source.set("Excel/CSV") # Default choice
        self.file_path.set("No file selected")
        self.df = None
        self.entries.clear()

        # Clear input fields and labels
        for widget in self.input_section.winfo_children():
            widget.destroy()

        self.summary_label.configure(text="AI summary will appear here.")
        self.result_label.configure(text="AI analysis results will be displayed here.")
        self.prompt_entry.delete(0, ctk.END) # Clear prompt entry

        # Hide any loading indicators
        self.loading_label_data_load.pack_forget()
        self.loading_label_summary.pack_forget()
        self.loading_label_analysis.pack_forget()

        # Reset button states
        self.connect_load_button.configure(state="disabled")
        self.update_analysis_buttons_state(False) # Disable summarize/analyze buttons

        # Re-display initial Excel/CSV input fields
        self.display_source_inputs() # This will ensure the "Load File" button is disabled initially
        messagebox.showinfo("Reset", "Application has been reset to its initial state.")


    def display_source_inputs(self):
        """
        Clears existing input fields and displays new ones based on the selected data source.
        This is called when "Submit Source" button is clicked or during reset.
        """
        for widget in self.input_section.winfo_children():
            widget.destroy() # Clear previous widgets
        self.entries.clear() # Clear stored entries
        self.file_path.set("No file selected") # Reset file path display
        self.df = None # Clear any previously loaded dataframe
        self.update_analysis_buttons_state() # Disable analysis buttons

        source = self.data_source.get()

        if source == "Excel/CSV":
            ctk.CTkLabel(self.input_section, text="Select CSV or Excel File:").pack(pady=5)
            file_row = ctk.CTkFrame(self.input_section)
            file_row.pack(pady=5)
            ctk.CTkButton(file_row, text="Browse", command=self.browse_file).pack(side="left", padx=5)
            ctk.CTkLabel(file_row, textvariable=self.file_path).pack(side="left", padx=5)
            self.connect_load_button.configure(text="Load File", state="disabled") # Disabled until file is browsed

        elif source == "SQL Database":
            fields = [("Dialect (e.g., mysql+pymysql)", "dialect"),
                      ("Username", "username"),
                      ("Password", "password"),
                      ("Host", "host"),
                      ("Port", "port"),
                      ("Database", "database"),
                      ("SQL Query", "sql_query")]
            
            for display_name, key_name in fields:
                field_frame = ctk.CTkFrame(self.input_section)
                field_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(field_frame, text=f"{display_name}:", width=150, anchor="w").pack(side="left", padx=5)
                entry = ctk.CTkEntry(field_frame, show="*" if "password" in key_name else None, width=300)
                entry.pack(side="left", fill="x", expand=True, padx=5)
                self.entries[key_name] = entry
            self.connect_load_button.configure(text="Connect to Database", state="normal") # Enable for manual input

        elif source == "SharePoint List":
            fields = [("Site URL", "site_url"),
                      ("List Name", "list_name"),
                      ("Client ID", "client_id"),
                      ("Client Secret", "client_secret")]
            
            for display_name, key_name in fields:
                field_frame = ctk.CTkFrame(self.input_section)
                field_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(field_frame, text=f"{display_name}:", width=150, anchor="w").pack(side="left", padx=5)
                entry = ctk.CTkEntry(field_frame, show="*" if "secret" in key_name else None, width=300)
                entry.pack(side="left", fill="x", expand=True, padx=5)
                self.entries[key_name] = entry
            self.connect_load_button.configure(text="Connect to SharePoint", state="normal") # Enable for manual input

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("CSV/Excel files", "*.csv *.xlsx")])
        if file:
            self.file_path.set(file)
            self.connect_load_button.configure(state="normal") # Enable connect button once file is chosen
        else:
            self.file_path.set("No file selected")
            self.connect_load_button.configure(state="disabled")

    def perform_data_load(self):
        """
        Handles the actual data loading/connection based on the selected source
        and entered details. Called by the "Connect/Load Data" button.
        """
        self.loading_label_data_load.pack(pady=5)
        self.root.update_idletasks() # Force UI update

        source = self.data_source.get()
        try:
            if source == "Excel/CSV":
                if not self.file_path.get() or self.file_path.get() == "No file selected":
                    messagebox.showerror("Error", "Please select an Excel or CSV file first.")
                    self.df = None
                    return
                self.df = backend1.load_excel_csv(self.file_path.get())
                messagebox.showinfo("Success", "File loaded successfully!")
            elif source == "SQL Database":
                params = {k: v.get() for k, v in self.entries.items()}
                if not all(params.values()):
                    messagebox.showerror("Input Error", "Please fill all SQL database connection details.")
                    self.df = None
                    return
                self.df = backend1.load_sql_table(
                    params["dialect"], params["username"], params["password"],
                    params["host"], params["port"], params["database"], params["sql_query"]
                )
                messagebox.showinfo("Success", "SQL data loaded successfully!")
            elif source == "SharePoint List":
                params = {k: v.get() for k, v in self.entries.items()}
                if not all(params.values()):
                    messagebox.showerror("Input Error", "Please fill all SharePoint connection details.")
                    self.df = None
                    return
                self.df = backend1.load_sharepoint_list(
                    params["site_url"], params["list_name"], params["client_id"], params["client_secret"]
                )
                messagebox.showinfo("Success", "SharePoint data loaded successfully!")
            
            # If data load was successful:
            self.update_analysis_buttons_state(True)
            self.summary_label.configure(text="AI summary will appear here.") # Reset summary on new load
            self.result_label.configure(text="AI analysis results will be displayed here.") # Reset results on new load

        except Exception as e:
            messagebox.showerror("Connection/Load Error", str(e))
            self.df = None
            self.update_analysis_buttons_state(False)
        finally:
            self.loading_label_data_load.pack_forget()

    def update_analysis_buttons_state(self, enabled=False):
        """Enables or disables the Summarize and Analyze buttons."""
        state = "normal" if enabled and self.df is not None else "disabled"
        self.summarize_button.configure(state=state)
        self.analyze_button.configure(state=state)

    def summarize_data(self):
        if self.df is not None:
            self.loading_label_summary.pack(pady=5)
            self.summary_label.configure(text="")
            self.root.update_idletasks()

            try:
                summary_text = backend1.summarize_dataframe(self.df)
                self.summary_label.configure(text=summary_text)
            except Exception as e:
                messagebox.showerror("Summary Error", str(e))
                self.summary_label.configure(text="Error generating summary.")
            finally:
                self.loading_label_summary.pack_forget()
        else:
            messagebox.showerror("Summary Error", "No data loaded to summarize. Please connect to a data source first.")
            self.summary_label.configure(text="No data loaded yet.")

    def run_analysis(self):
        if self.df is None:
            messagebox.showerror("Analysis Error", "No data loaded to analyze. Please connect to a data source first.")
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
            answer = backend1.analyse_dataframe(self.df, prompt_text)
            self.result_label.configure(text=answer)
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))
            self.result_label.configure(text="Error during analysis.")
        finally:
            self.loading_label_analysis.pack_forget()

if __name__ == "__main__":
    root = ctk.CTk()
    app = DataWizardApp(root)
    root.mainloop()