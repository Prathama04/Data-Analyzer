import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import pandas as pd
import backend1

class DataWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyzer")
        # Adjust initial geometry for a more balanced start
        self.root.geometry("850x700") # Increased width slightly
        # Set minimum size to prevent window from becoming too small
        self.root.minsize(width=750, height=650) # Added minsize

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Initialize state variables
        self.data_source = ctk.StringVar(value="--- Select Source ---")
        self.file_path = ctk.StringVar(value="No file selected")
        self.df = None
        self.entries = {}

        self.build_main_layout()

    def build_main_layout(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Using grid for the main window layout for better responsiveness
        self.root.grid_columnconfigure(0, weight=0) # Sidebar column (fixed width)
        self.root.grid_columnconfigure(1, weight=1) # Main content column (expands)
        self.root.grid_rowconfigure(0, weight=1) # Main row (expands)

        # Sidebar
        sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew") # Placed in grid
        ctk.CTkLabel(sidebar, text="Hi, I am Data Analyzer", font=("Arial", 16, "bold"), wraplength=180).pack(pady=(20, 10))
        ctk.CTkLabel(sidebar, text="Your Personal Assistant\nin the Digital Realm", wraplength=180, justify="center").pack(pady=5)
        try:
            org_image = Image.open("org_logo.png").resize((200, 80))
            org_logo = ctk.CTkImage(light_image=org_image, dark_image=org_image, size=(200, 80))
            org_label = ctk.CTkLabel(sidebar, image=org_logo, text="")
            org_label.image = org_logo
            org_label.pack(side="bottom", pady=10)
        except FileNotFoundError:
            print("Warning: org_logo.png not found. Skipping image.")
        except Exception as e:
            print(f"Error loading image: {e}")

        # Main area within a scrollable frame for overflow content
        # This frame now takes up the second column in the root grid
        self.main_scrollable_frame = ctk.CTkScrollableFrame(self.root)
        self.main_scrollable_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Content of the main area is packed into self.main_scrollable_frame
        ctk.CTkLabel(self.main_scrollable_frame, text="DATA ANALYZER", font=("Arial", 20, "bold")).pack(pady=10)

        # --- Data Source Selection ---
        source_selection_frame = ctk.CTkFrame(self.main_scrollable_frame)
        source_selection_frame.pack(pady=10)
        ctk.CTkLabel(source_selection_frame, text="Choose Data Source:").pack(side="left", padx=5)
        self.source_menu = ctk.CTkOptionMenu(source_selection_frame, variable=self.data_source,
                                             values=["--- Select Source ---", "Excel/CSV", "SQL Database", "SharePoint List"],
                                             command=self.on_source_menu_change)
        self.source_menu.pack(side="left", padx=5)
        self.submit_source_button = ctk.CTkButton(source_selection_frame, text="Submit Source",
                                                  command=self.display_source_inputs, state="disabled")
        self.submit_source_button.pack(side="left", padx=15)

        # --- Dynamic Input Section ---
        self.input_section = ctk.CTkFrame(self.main_scrollable_frame)
        self.input_section.pack(pady=10, fill="x", padx=20)
        self.input_section_placeholder_label = ctk.CTkLabel(self.input_section, text="Please select a data source and click 'Submit Source'.", wraplength=400, justify="center")
        self.input_section_placeholder_label.pack(pady=40)

        # --- Connect/Load and Back Buttons ---
        action_buttons_frame = ctk.CTkFrame(self.main_scrollable_frame)
        action_buttons_frame.pack(pady=15)

        self.connect_load_button = ctk.CTkButton(action_buttons_frame, text="Connect/Load Data", command=self.perform_data_load, state="disabled")
        self.connect_load_button.pack(side="left", padx=10)

        self.back_button = ctk.CTkButton(action_buttons_frame, text="Reset / Back", command=self.reset_application)
        self.back_button.pack(side="left", padx=10)

        # Loading indicator for data loading
        self.loading_label_data_load = ctk.CTkLabel(self.main_scrollable_frame, text="Loading data...", font=("Arial", 14, "italic"))
        self.loading_label_data_load.pack_forget()

        # --- Summarize Section ---
        self.summarize_button = ctk.CTkButton(self.main_scrollable_frame, text="Summarize Dataset", command=self.summarize_data, state="disabled")
        self.summarize_button.pack(pady=20)

        self.summary_label = ctk.CTkLabel(self.main_scrollable_frame, text="AI summary will appear here.", wraplength=600, justify="left")
        self.summary_label.pack(pady=10)

        # Loading indicator for summary
        self.loading_label_summary = ctk.CTkLabel(self.main_scrollable_frame, text="Generating summary...", font=("Arial", 14, "italic"))
        self.loading_label_summary.pack_forget()

        # --- Analysis Section ---
        self.prompt_entry = ctk.CTkEntry(self.main_scrollable_frame, placeholder_text="Ask your question...", width=500)
        self.prompt_entry.pack(pady=10)

        self.analyze_button = ctk.CTkButton(self.main_scrollable_frame, text="Analyze", command=self.run_analysis, state="disabled")
        self.analyze_button.pack(pady=10)

        # Loading indicator for analysis
        self.loading_label_analysis = ctk.CTkLabel(self.main_scrollable_frame, text="Analyzing data...", font=("Arial", 14, "italic"))
        self.loading_label_analysis.pack_forget()

        self.result_label = ctk.CTkLabel(self.main_scrollable_frame, text="AI analysis results will be displayed here.", wraplength=600, justify="left")
        self.result_label.pack(pady=20)

        # Ensure analysis and connect/load buttons are disabled initially
        self.update_analysis_buttons_state(False)
        self.connect_load_button.configure(state="disabled")

    def on_source_menu_change(self, choice):
        if choice == "--- Select Source ---":
            self.submit_source_button.configure(state="disabled")
        else:
            self.submit_source_button.configure(state="normal")
        self.reset_input_section_state()

    def reset_input_section_state(self):
        for widget in self.input_section.winfo_children():
            widget.destroy()
        self.input_section_placeholder_label = ctk.CTkLabel(self.input_section, text="Please select a data source and click 'Submit Source'.", wraplength=400, justify="center")
        self.input_section_placeholder_label.pack(pady=40)

        self.entries.clear()
        self.file_path.set("No file selected")
        self.df = None
        self.connect_load_button.configure(state="disabled")
        self.update_analysis_buttons_state(False)
        self.summary_label.configure(text="AI summary will appear here.")
        self.result_label.configure(text="AI analysis results will be displayed here.")
        self.prompt_entry.delete(0, ctk.END)


    def reset_application(self):
        self.data_source.set("--- Select Source ---")
        self.file_path.set("No file selected")
        self.df = None
        self.entries.clear()

        self.reset_input_section_state()

        self.loading_label_data_load.pack_forget()
        self.loading_label_summary.pack_forget()
        self.loading_label_analysis.pack_forget()

        self.connect_load_button.configure(state="disabled")
        self.update_analysis_buttons_state(False)
        self.submit_source_button.configure(state="disabled")

        messagebox.showinfo("Reset", "Application has been reset to its initial state.")


    def display_source_inputs(self):
        # Remove the placeholder label
        self.input_section_placeholder_label.pack_forget()
        for widget in self.input_section.winfo_children():
            widget.destroy()

        self.entries.clear()
        self.file_path.set("No file selected")
        self.df = None
        self.update_analysis_buttons_state()

        source = self.data_source.get()

        if source == "Excel/CSV":
            ctk.CTkLabel(self.input_section, text="Select CSV or Excel File:").pack(pady=5)
            file_row = ctk.CTkFrame(self.input_section)
            file_row.pack(pady=5)
            ctk.CTkButton(file_row, text="Browse", command=self.browse_file).pack(side="left", padx=5)
            ctk.CTkLabel(file_row, textvariable=self.file_path).pack(side="left", padx=5)
            self.connect_load_button.configure(text="Load File", state="disabled")

        elif source == "SQL Database":
            fields = [("Dialect (e.g., mysql+pymysql)", "dialect"),
                      ("Username", "username"),
                      ("Password", "password"),
                      ("Host", "host"),
                      ("Port", "port"),
                      ("Database", "database")]
                      
            
            for display_name, key_name in fields:
                field_frame = ctk.CTkFrame(self.input_section)
                field_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(field_frame, text=f"{display_name}:", width=150, anchor="w").pack(side="left", padx=5)
                entry = ctk.CTkEntry(field_frame, show="*" if "password" in key_name else None, width=300)
                entry.pack(side="left", fill="x", expand=True, padx=5)
                self.entries[key_name] = entry
            self.connect_load_button.configure(text="Connect to Database", state="normal")

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
                self.df = backend1.load_excel_csv(self.file_path.get())
                messagebox.showinfo("Success", "File loaded successfully!")
            elif source == "SQL Database":
                params = {k: v.get() for k, v in self.entries.items()}
                params_for_backend = {
                    "dialect": params.get("dialect", ""),
                    "username": params.get("username", ""),
                    "password": params.get("password", ""),
                    "host": params.get("host", ""),
                    "port": params.get("port", ""),
                    "database": params.get("database", "")
                    #"sql_query": params.get("sql_query", "")
                }
                if not all(params_for_backend[key] for key in ["dialect", "username", "password", "host", "port", "database", "sql_query"]):
                     messagebox.showerror("Input Error", "Please fill all SQL database connection details.")
                     self.df = None
                     return

                self.df = backend.load_sql_table(
                    params_for_backend["dialect"], params_for_backend["username"], params_for_backend["password"],
                    params_for_backend["host"], params_for_backend["port"], params_for_backend["database"], params_for_backend["sql_query"]
                )
                messagebox.showinfo("Success", "SQL data loaded successfully!")
            elif source == "SharePoint List":
                params = {k: v.get() for k, v in self.entries.items()}
                params_for_backend = {
                    "site_url": params.get("site_url", ""),
                    "list_name": params.get("list_name", ""),
                    "client_id": params.get("client_id", ""),
                    "client_secret": params.get("client_secret", "")
                }
                if not all(params_for_backend[key] for key in ["site_url", "list_name", "client_id", "client_secret"]):
                     messagebox.showerror("Input Error", "Please fill all SharePoint connection details.")
                     self.df = None
                     return
                self.df = backend1.load_sharepoint_list(
                    params_for_backend["site_url"], params_for_backend["list_name"], params_for_backend["client_id"], params_for_backend["client_secret"]
                )
                messagebox.showinfo("Success", "SharePoint data loaded successfully!")
            
            self.update_analysis_buttons_state(True)
            self.summary_label.configure(text="AI summary will appear here.")
            self.result_label.configure(text="AI analysis results will be displayed here.")

        except Exception as e:
            messagebox.showerror("Connection/Load Error", str(e))
            self.df = None
            self.update_analysis_buttons_state(False)
        finally:
            self.loading_label_data_load.pack_forget()

    def update_analysis_buttons_state(self, enabled=False):
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