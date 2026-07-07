import json
import os
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from src.core.controller import AppController


class UmrahApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("INNA ATAINA TRAVELS OPS PRO")
        self.geometry("1100x740")
        self.minsize(1000, 680)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.controller = AppController(self.handle_controller_events)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Rows: logo, title, buttons, spacer, status, credit
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Top logo (safe loading to avoid crash if missing)
        self.logo_image = None
        logo_path_png = os.path.join("assets", "logo.png")
        logo_path_jpg = os.path.join("assets", "logo.jpg")
        logo_path_jpeg = os.path.join("assets", "logo.jpeg")

        logo_path = None
        if os.path.exists(logo_path_png):
            logo_path = logo_path_png
        elif os.path.exists(logo_path_jpg):
            logo_path = logo_path_jpg
        elif os.path.exists(logo_path_jpeg):
            logo_path = logo_path_jpeg

        if logo_path:
            try:
                pil_logo = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(90, 90))
                self.logo_widget = ctk.CTkLabel(self.sidebar, text="", image=self.logo_image)
                self.logo_widget.grid(row=0, column=0, padx=24, pady=(28, 12), sticky="n")
            except Exception:
                self.logo_widget = ctk.CTkLabel(
                    self.sidebar,
                    text="",
                    width=1,
                    height=1,
                )
                self.logo_widget.grid(row=0, column=0, padx=24, pady=(28, 12), sticky="n")
        else:
            self.logo_widget = ctk.CTkLabel(
                self.sidebar,
                text="",
                width=1,
                height=1,
            )
            self.logo_widget.grid(row=0, column=0, padx=24, pady=(28, 12), sticky="n")

        # Branding header
        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="INNA ATAINA TRAVELS\nOPS PRO",
            font=ctk.CTkFont(size=24, weight="bold"),
            justify="center",
        )
        self.logo.grid(row=1, column=0, padx=20, pady=(2, 24))

        # Action buttons (commands preserved exactly)
        self.btn_upload = ctk.CTkButton(
            self.sidebar,
            text="1. Upload Ticket",
            command=self.upload_ticket,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
        )
        self.btn_upload.grid(row=2, column=0, padx=24, pady=(8, 12), sticky="ew")

        self.btn_generate = ctk.CTkButton(
            self.sidebar,
            text="2. Generate Document",
            state="disabled",
            fg_color="green",
            hover_color="darkgreen",
            command=self.generate_doc,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
        )
        self.btn_generate.grid(row=3, column=0, padx=24, pady=12, sticky="ew")

        self.btn_open_folder = ctk.CTkButton(
            self.sidebar,
            text="Open Output Folder",
            command=self.open_output,
            fg_color="transparent",
            border_width=1,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10,
        )
        self.btn_open_folder.grid(row=4, column=0, padx=24, pady=(12, 16), sticky="sew")

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="Status: Idle",
            text_color="gray",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.status_label.grid(row=5, column=0, padx=20, pady=(8, 8))

        # Developer credit
        self.dev_credit = ctk.CTkLabel(
            self.sidebar,
            text="Developed by AIO Scholarworks",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("gray35", "gray75"),
        )
        self.dev_credit.grid(row=6, column=0, padx=20, pady=(4, 18))

    def _build_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=14)
        self.main_frame.grid(row=0, column=1, padx=24, pady=24, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self.main_frame,
            text="AIO Scholarworks Data Extraction Preview",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_lbl.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="w")

        self.data_textbox = ctk.CTkTextbox(
            self.main_frame,
            font=("Consolas", 13),
            corner_radius=10,
            border_width=1,
        )
        self.data_textbox.grid(row=1, column=0, padx=18, pady=(8, 18), sticky="nsew")
        self.data_textbox.insert("0.0", "Upload a document to see extracted JSON data here...")

    def upload_ticket(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Supported Files", "*.pdf *.png *.jpg *.jpeg")]
        )
        if filepath:
            self.data_textbox.delete("0.0", "end")
            self.btn_generate.configure(state="disabled")
            self.controller.process_ticket_async(filepath)

    def generate_doc(self):
        self.btn_generate.configure(state="disabled")
        self.controller.generate_document_async()

    def open_output(self):
        out_dir = self.controller.config.get("output_directory")
        if os.path.exists(out_dir):
            os.startfile(os.path.abspath(out_dir))
        else:
            messagebox.showwarning("Warning", "Output directory does not exist yet.")

    def handle_controller_events(self, event_type, payload):
        # Ensure UI updates happen on the main thread safely
        self.after(0, self._process_event, event_type, payload)

    def _process_event(self, event_type, payload):
        if event_type == "status":
            self.status_label.configure(text=payload)

        elif event_type == "error":
            self.status_label.configure(text="Error occurred.")
            messagebox.showerror("System Error", payload)

        elif event_type == "data_ready":
            self.status_label.configure(text="Data Ready.")
            self.data_textbox.delete("0.0", "end")
            self.data_textbox.insert("end", payload["data"])
            self.btn_generate.configure(state="normal")

            if payload["warnings"]:
                warning_text = "\n".join(payload["warnings"])
                messagebox.showwarning("Validation Warnings", f"Please review:\n\n{warning_text}")

        elif event_type == "success":
            self.status_label.configure(text="Complete.")
            self.btn_generate.configure(state="normal")
            messagebox.showinfo("Success", payload)