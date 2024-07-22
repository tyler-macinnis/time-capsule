import csv
import json
import os
from datetime import datetime
from tkinter import messagebox, ttk

import customtkinter as ctk
from tkcalendar import DateEntry

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATES_FILE = os.path.join(SCRIPT_DIR, "important_dates.json")
DATE_FORMAT = "%m-%d-%Y"  # Updated date format
VERSION = "1.0.0"
APP_NAME = "Time Capsule"  # You can change this to any of the suggested names


def load_dates():
    try:
        with open(DATES_FILE, "r") as file:
            data = json.load(file)
            # Ensure the data is in the correct format
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = {"date": value, "notes": ""}
            return data
    except FileNotFoundError:
        return {}


def save_dates(dates):
    with open(DATES_FILE, "w") as file:
        json.dump(dates, file, indent=4)


def add_date(event=None, date_str=None, note=None, mode="Add"):
    def save_event():
        event_name = event_entry.get()
        date_str = date_entry.get_date().strftime(DATE_FORMAT)
        note_text = notes_entry.get("1.0", "end").strip()
        if not event_name or not date_str:
            messagebox.showerror("Error", "Event name and date are required.")
            return
        dates[event_name] = {"date": date_str, "notes": note_text}
        save_dates(dates)
        refresh_dates_list()
        add_date_window.destroy()

    add_date_window = ctk.CTkToplevel(root)
    add_date_window.title(f"{mode} Date")
    add_date_window.geometry("400x450")
    add_date_window.transient(root)
    add_date_window.grab_set()

    ctk.CTkLabel(
        add_date_window, text="Enter the event name:", font=("Arial", 12)
    ).pack(pady=10)
    event_entry = ctk.CTkEntry(add_date_window, font=("Arial", 12))
    event_entry.pack(pady=5)

    ctk.CTkLabel(add_date_window, text="Enter the date:", font=("Arial", 12)).pack(
        pady=10
    )
    date_entry = DateEntry(
        add_date_window, font=("Arial", 12), date_pattern="mm-dd-yyyy"
    )
    date_entry.pack(pady=5)

    ctk.CTkLabel(add_date_window, text="Notes:", font=("Arial", 12)).pack(pady=10)
    notes_entry = ctk.CTkTextbox(add_date_window, height=100, font=("Arial", 12))
    notes_entry.pack(pady=5)

    if event:
        event_entry.insert(0, event)
        if date_str:
            date_entry.set_date(datetime.strptime(date_str, DATE_FORMAT))
        if note:
            notes_entry.insert("1.0", note)

    ctk.CTkButton(add_date_window, text="Save", command=save_event).pack(pady=20)


def refresh_dates_list():
    dates_listbox.delete(*dates_listbox.get_children())
    search_text = search_entry.get().lower()
    for event, info in dates.items():
        date_str = info["date"]
        notes = info["notes"]
        if search_text in event.lower() or search_text in notes.lower():
            date = datetime.strptime(date_str, DATE_FORMAT)
            days_since = (datetime.now() - date).days
            dates_listbox.insert(
                "", "end", values=(event, date_str, f"{days_since} days ago", notes)
            )


def show_about():
    about_message = (
        f"{APP_NAME} v{VERSION}\n\n"
        "This application helps you track important dates and milestones.\n\n"
        "Instructions:\n"
        "1. Use the 'Add Date' button to add a new event.\n"
        "2. Double-click an event to edit it.\n"
        "3. Use the search bar to filter events by name or notes.\n"
        "4. Use the 'Export to CSV' and 'Import from CSV' buttons to back up and restore your data.\n"
    )
    about_window = ctk.CTkToplevel(root)
    about_window.title("About")
    about_window.geometry("600x500")  # Set the size of the window
    about_window.transient(root)
    about_window.grab_set()
    text_widget = ctk.CTkTextbox(about_window, wrap="word", font=("Arial", 12))
    text_widget.pack(expand=True, fill="both", padx=10, pady=10)
    text_widget.insert("1.0", about_message)
    text_widget.configure(state="disabled")  # Make the text widget read-only


def on_double_click(event):
    item = dates_listbox.selection()
    if item:
        item = item[0]
        event_name = dates_listbox.item(item, "values")[0]
        date_str = dates_listbox.item(item, "values")[1]
        notes = dates_listbox.item(item, "values")[3]
        add_date(event_name, date_str, notes, mode="Edit")


def sort_dates(column, reverse):
    data = [(dates_listbox.set(k, column), k) for k in dates_listbox.get_children("")]
    data.sort(reverse=reverse)
    for index, (val, k) in enumerate(data):
        dates_listbox.move(k, "", index)
    dates_listbox.heading(column, command=lambda: sort_dates(column, not reverse))


def export_to_csv():
    filename = os.path.join(SCRIPT_DIR, "important_dates_export.csv")
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["Event", "Date", "Notes"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for event, info in dates.items():
            writer.writerow(
                {"Event": event, "Date": info["date"], "Notes": info["notes"]}
            )

    messagebox.showinfo("Export Successful", f"Dates have been exported to {filename}")


def import_from_csv():
    filename = os.path.join(SCRIPT_DIR, "important_dates_import.csv")
    try:
        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                dates[row["Event"]] = {"date": row["Date"], "notes": row["Notes"]}
        save_dates(dates)
        refresh_dates_list()
        messagebox.showinfo(
            "Import Successful", "Dates have been imported successfully"
        )
    except FileNotFoundError:
        messagebox.showerror("Import Error", f"{filename} not found")


def delete_date():
    selected_item = dates_listbox.selection()
    if selected_item:
        event_name = dates_listbox.item(selected_item, "values")[0]
        if messagebox.askyesno(
            "Delete Confirmation", f"Are you sure you want to delete '{event_name}'?"
        ):
            del dates[event_name]
            save_dates(dates)
            refresh_dates_list()


def update_styles():
    mode = ctk.get_appearance_mode()
    if mode == "Dark":
        style.configure(
            "Treeview",
            background="#2D2D2D",
            foreground="white",
            fieldbackground="#2D2D2D",
            bordercolor="#343638",
            borderwidth=1,
        )
        style.configure(
            "Treeview.Heading",
            background="#565656",
            foreground="white",
            bordercolor="#565656",
            borderwidth=1,
        )
        style.map("Treeview", background=[("selected", "#565656")])
        scrollbar.configure(style="Vertical.TScrollbar")
    else:
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            bordercolor="lightgrey",
            borderwidth=1,
        )
        style.configure(
            "Treeview.Heading",
            background="lightgrey",
            foreground="black",
            bordercolor="lightgrey",
            borderwidth=1,
        )
        style.map("Treeview", background=[("selected", "lightblue")])
        scrollbar.configure(style="Vertical.TScrollbar")


def main():
    global root, dates_listbox, search_entry, scrollbar

    # Load existing dates
    global dates
    dates = load_dates()

    # Create the main window
    root = ctk.CTk()
    root.title(f"{APP_NAME} v{VERSION}")
    root.geometry("900x600")  # Set initial size
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    # Create search bar
    search_frame = ctk.CTkFrame(root)
    search_frame.grid(row=0, column=0, columnspan=4, pady=10, padx=10, sticky="ew")

    ctk.CTkLabel(search_frame, text="Search:", font=("Arial", 12)).pack(side="left")
    search_entry = ctk.CTkEntry(search_frame, font=("Arial", 12))
    search_entry.pack(side="left", fill="x", expand=True)
    search_entry.bind("<KeyRelease>", lambda event: refresh_dates_list())

    # Create a custom style for the Treeview and Scrollbar to match the theme
    global style
    style = ttk.Style()
    style.theme_use("clam")  # Using 'clam' as it is easily customizable

    # Create and pack the Treeview
    columns = ("Event", "Date", "Days Since", "Notes")
    dates_listbox = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        dates_listbox.heading(
            col, text=col, command=lambda _col=col: sort_dates(_col, False)
        )
        dates_listbox.column(col, width=150)

    dates_listbox.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
    dates_listbox.bind("<Double-1>", on_double_click)

    # Add a scrollbar for the Treeview
    global scrollbar
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=dates_listbox.yview)
    scrollbar.grid(row=1, column=4, sticky="ns")
    dates_listbox.configure(yscrollcommand=scrollbar.set)

    # Create and pack the buttons
    buttons_frame = ctk.CTkFrame(root)
    buttons_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

    ctk.CTkButton(buttons_frame, text="Add Date", command=add_date).grid(
        row=0, column=0, padx=10
    )
    ctk.CTkButton(buttons_frame, text="Delete Date", command=delete_date).grid(
        row=0, column=1, padx=10
    )
    ctk.CTkButton(buttons_frame, text="Export to CSV", command=export_to_csv).grid(
        row=0, column=2, padx=10
    )
    ctk.CTkButton(buttons_frame, text="Import from CSV", command=import_from_csv).grid(
        row=0, column=3, padx=10
    )
    ctk.CTkButton(buttons_frame, text="About", command=show_about).grid(
        row=0, column=4, padx=10
    )

    # Refresh the Treeview with dates
    refresh_dates_list()

    # Update the styles based on the current theme
    update_styles()

    # Run the application
    root.mainloop()


if __name__ == "__main__":
    main()
