import csv
import json
import os
from datetime import datetime
from tkinter import colorchooser, messagebox, ttk

import customtkinter as ctk
from dateutil.relativedelta import relativedelta
from tkcalendar import DateEntry

# Constants
APP_NAME = "Time Capsule"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATES_FILE = os.path.join(SCRIPT_DIR, "important_dates.json")
CATEGORIES_FILE = os.path.join(SCRIPT_DIR, "categories.json")
DATE_FORMAT = "%m-%d-%Y"
VERSION = "1.1.0"


def load_dates():
    try:
        with open(DATES_FILE, "r") as file:
            data = json.load(file)
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = {"date": value, "notes": "", "category": ""}
            return data
    except FileNotFoundError:
        return {}


def save_dates(dates):
    with open(DATES_FILE, "w") as file:
        json.dump(dates, file, indent=4)


def load_categories():
    try:
        with open(CATEGORIES_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_categories(categories):
    with open(CATEGORIES_FILE, "w") as file:
        json.dump(categories, file, indent=4)


def calculate_time_since(start_date):
    now = datetime.now()
    start = datetime.strptime(start_date, DATE_FORMAT)
    delta = relativedelta(now, start)
    parts = []
    if delta.years:
        parts.append(f"{delta.years} year{'s' if delta.years > 1 else ''}")
    if delta.months:
        parts.append(f"{delta.months} month{'s' if delta.months > 1 else ''}")
    if delta.days:
        parts.append(f"{delta.days} day{'s' if delta.days > 1 else ''}")
    return ", ".join(parts) or "0 days"


def manage_categories():
    def add_category():
        category_name = category_entry.get()
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if not category_name or not color_code:
            messagebox.showerror("Error", "Category name and color are required.")
            return
        categories[category_name] = color_code
        save_categories(categories)
        refresh_categories_list()
        category_entry.delete(0, "end")

    def delete_category():
        selected_item = categories_listbox.selection()
        if selected_item:
            category_name = categories_listbox.item(selected_item, "values")[0]
            if messagebox.askyesno(
                "Delete Confirmation",
                f"Are you sure you want to delete '{category_name}'?",
            ):
                del categories[category_name]
                save_categories(categories)
                refresh_categories_list()

    def refresh_categories_list():
        categories_listbox.delete(*categories_listbox.get_children())
        for category, color in categories.items():
            categories_listbox.insert(
                "", "end", values=(category, color), tags=(category,)
            )
            categories_listbox.tag_configure(category, background=color)

    manage_categories_window = ctk.CTkToplevel(root)
    manage_categories_window.title("Manage Categories")
    manage_categories_window.geometry("400x400")
    manage_categories_window.minsize(400, 400)
    manage_categories_window.transient(root)
    manage_categories_window.grab_set()

    ctk.CTkLabel(
        manage_categories_window, text="Category Name:", font=("Arial", 12)
    ).pack(pady=10)
    category_entry = ctk.CTkEntry(manage_categories_window, font=("Arial", 12))
    category_entry.pack(pady=5)

    ctk.CTkButton(
        manage_categories_window, text="Add Category", command=add_category
    ).pack(pady=10)
    ctk.CTkButton(
        manage_categories_window,
        text="Delete Selected Category",
        command=delete_category,
    ).pack(pady=10)

    columns = ("Category", "Color")
    categories_listbox = ttk.Treeview(
        manage_categories_window, columns=columns, show="headings"
    )
    for col in columns:
        categories_listbox.heading(col, text=col)
        categories_listbox.column(col, width=150)
    categories_listbox.pack(expand=True, fill="both", padx=10, pady=10)

    refresh_categories_list()


def add_date(event=None, date_str=None, note=None, category=None, mode="Add"):
    def save_event():
        event_name = event_entry.get()
        date_str = date_entry.get_date().strftime(DATE_FORMAT)
        note_text = notes_entry.get("1.0", "end").strip()
        category = category_combobox.get()
        if not event_name or not date_str:
            messagebox.showerror("Error", "Event name and date are required.")
            return
        dates[event_name] = {"date": date_str, "notes": note_text, "category": category}
        save_dates(dates)
        refresh_dates_list()
        add_date_window.destroy()

    add_date_window = ctk.CTkToplevel(root)
    add_date_window.title(f"{mode} Date")
    add_date_window.geometry("400x550")
    add_date_window.minsize(400, 550)
    add_date_window.transient(root)
    add_date_window.grab_set()

    add_date_window.columnconfigure(0, weight=1)
    add_date_window.rowconfigure(1, weight=1)
    add_date_window.rowconfigure(3, weight=2)

    ctk.CTkLabel(
        add_date_window, text="Enter the event name:", font=("Arial", 12)
    ).grid(row=0, column=0, pady=10, padx=10, sticky="w")
    event_entry = ctk.CTkEntry(add_date_window, font=("Arial", 12))
    event_entry.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

    ctk.CTkLabel(add_date_window, text="Enter the date:", font=("Arial", 12)).grid(
        row=2, column=0, pady=10, padx=10, sticky="w"
    )
    date_entry = DateEntry(
        add_date_window, font=("Arial", 12), date_pattern="mm-dd-yyyy"
    )
    date_entry.grid(row=3, column=0, pady=5, padx=10, sticky="ew")

    ctk.CTkLabel(add_date_window, text="Category:", font=("Arial", 12)).grid(
        row=4, column=0, pady=10, padx=10, sticky="w"
    )
    category_combobox = ctk.CTkComboBox(
        add_date_window,
        values=list(categories.keys()) or ["No Categories"],
        font=("Arial", 12),
    )
    category_combobox.grid(row=5, column=0, pady=5, padx=10, sticky="ew")

    ctk.CTkLabel(add_date_window, text="Notes:", font=("Arial", 12)).grid(
        row=6, column=0, pady=10, padx=10, sticky="w"
    )
    notes_entry = ctk.CTkTextbox(add_date_window, height=100, font=("Arial", 12))
    notes_entry.grid(row=7, column=0, pady=5, padx=10, sticky="nsew")

    if event:
        event_entry.insert(0, event)
        if date_str:
            date_entry.set_date(datetime.strptime(date_str, DATE_FORMAT))
        if note:
            notes_entry.insert("1.0", note)
        if category:
            category_combobox.set(category)

    ctk.CTkButton(add_date_window, text="Save", command=save_event).grid(
        row=8, column=0, pady=20
    )


def refresh_dates_list():
    dates_listbox.delete(*dates_listbox.get_children())
    search_text = search_entry.get().lower()
    for event, info in dates.items():
        date_str = info["date"]
        notes = info["notes"]
        category = info.get("category", "")
        if (
            search_text in event.lower()
            or search_text in notes.lower()
            or search_text in category.lower()
        ):
            time_since = calculate_time_since(date_str)
            color = categories.get(category, "#FFFFFF")
            dates_listbox.insert(
                "",
                "end",
                values=(event, date_str, time_since, notes, category),
                tags=(category,),
            )
            dates_listbox.tag_configure(category, background=color)


def show_about():
    about_message = (
        f"{APP_NAME} v{VERSION}\n\n"
        "This application helps you track important dates and milestones.\n\n"
        "Instructions:\n"
        "1. Use the 'Add Date' button to add a new event.\n"
        "2. Double-click an event to edit it.\n"
        "3. Use the search bar to filter events by name, notes, or category.\n"
        "4. Use the 'Export to CSV' and 'Import from CSV' buttons to back up and restore your data.\n"
        "5. Use the 'Manage Categories' button to add, edit, or delete categories.\n\n"
        "Icon Attribution:\n"
        "Dose icons created by Pixel perfect - Flaticon\n"
        "For more information, see the README.md file.\n"
    )
    about_window = ctk.CTkToplevel(root)
    about_window.title("About")
    about_window.geometry("600x500")
    about_window.minsize(600, 500)
    about_window.transient(root)
    about_window.grab_set()
    text_widget = ctk.CTkTextbox(about_window, wrap="word", font=("Arial", 12))
    text_widget.pack(expand=True, fill="both", padx=10, pady=10)
    text_widget.insert("1.0", about_message)
    text_widget.configure(state="disabled")


def on_double_click(event):
    item = dates_listbox.selection()
    if item:
        item = item[0]
        event_name = dates_listbox.item(item, "values")[0]
        date_str = dates_listbox.item(item, "values")[1]
        notes = dates_listbox.item(item, "values")[3]
        category = dates_listbox.item(item, "values")[4]
        add_date(event_name, date_str, notes, category, mode="Edit")


def sort_dates(column, reverse):
    data = [(dates_listbox.set(k, column), k) for k in dates_listbox.get_children("")]
    data.sort(reverse=reverse)
    for index, (val, k) in enumerate(data):
        dates_listbox.move(k, "", index)
    dates_listbox.heading(column, command=lambda: sort_dates(column, not reverse))


def export_to_csv():
    filename = os.path.join(SCRIPT_DIR, "important_dates_export.csv")
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["Event", "Date", "Notes", "Category"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for event, info in dates.items():
            writer.writerow(
                {
                    "Event": event,
                    "Date": info["date"],
                    "Notes": info["notes"],
                    "Category": info.get("category", ""),
                }
            )

    messagebox.showinfo("Export Successful", f"Dates have been exported to {filename}")


def import_from_csv():
    filename = os.path.join(SCRIPT_DIR, "important_dates_import.csv")
    try:
        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                dates[row["Event"]] = {
                    "date": row["Date"],
                    "notes": row["Notes"],
                    "category": row.get("Category", ""),
                }
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
    global root, dates_listbox, search_entry, scrollbar, categories

    # Load existing dates
    global dates
    dates = load_dates()
    categories = load_categories()

    # Create the main window
    root = ctk.CTk()
    root.title(f"{APP_NAME} v{VERSION}")
    root.geometry("1000x600")
    root.minsize(1000, 600)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)

    # Create a custom style for the Treeview and Scrollbar to match the theme
    global style
    style = ttk.Style()
    style.theme_use("clam")

    # Create and pack the Treeview
    columns = ("Event", "Date", "Time Since", "Notes", "Category")
    dates_listbox = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        dates_listbox.heading(
            col, text=col, command=lambda _col=col: sort_dates(_col, False)
        )
        dates_listbox.column(col, width=150)

    dates_listbox.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
    dates_listbox.bind("<Double-1>", on_double_click)

    # Add a scrollbar for the Treeview
    global scrollbar
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=dates_listbox.yview)
    scrollbar.grid(row=1, column=2, rowspan=2, sticky="ns")
    dates_listbox.configure(yscrollcommand=scrollbar.set)

    # Create and pack the buttons in a left-side column
    buttons_frame = ctk.CTkFrame(root)
    buttons_frame.grid(row=1, column=0, rowspan=2, pady=10, sticky="ns")

    ctk.CTkButton(buttons_frame, text="Add Date", command=add_date).pack(
        pady=5, padx=10, fill="x"
    )
    ctk.CTkButton(
        buttons_frame, text="Manage Categories", command=manage_categories
    ).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(buttons_frame, text="Delete Date", command=delete_date).pack(
        pady=5, padx=10, fill="x"
    )
    ctk.CTkButton(buttons_frame, text="Export to CSV", command=export_to_csv).pack(
        pady=5, padx=10, fill="x"
    )
    ctk.CTkButton(buttons_frame, text="Import from CSV", command=import_from_csv).pack(
        pady=5, padx=10, fill="x"
    )
    ctk.CTkButton(buttons_frame, text="About", command=show_about).pack(
        pady=5, padx=10, fill="x"
    )

    # Create search bar above the treeview
    search_frame = ctk.CTkFrame(root)
    search_frame.grid(row=0, column=1, pady=10, padx=10, sticky="ew", columnspan=2)

    ctk.CTkLabel(search_frame, text="Search:", font=("Arial", 12)).pack(side="left")
    search_entry = ctk.CTkEntry(search_frame, font=("Arial", 12))
    search_entry.pack(side="left", fill="x", expand=True)
    search_entry.bind("<KeyRelease>", lambda event: refresh_dates_list())

    # Refresh the Treeview with dates
    refresh_dates_list()

    # Update the styles based on the current theme
    update_styles()

    # Run the application
    root.mainloop()


if __name__ == "__main__":
    main()
