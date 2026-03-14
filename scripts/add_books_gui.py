import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


class BookTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Books List Editor")
        self.geometry("760x520")
        self.resizable(True, True)

        self.root_path = Path(__file__).resolve().parents[1]
        self.list_path = self.root_path / "books" / "list.json"

        self.existing_entries = self._load_existing()
        self.existing_ids = {e.get("id") for e in self.existing_entries}
        self.pending = []

        self._build_ui()
        self._bind_global_clipboard_keys()

    def _load_existing(self):
        if not self.list_path.exists():
            messagebox.showerror("Missing file", f"Could not find {self.list_path}")
            return []
        try:
            return json.loads(self.list_path.read_text(encoding="utf-8"))
        except Exception as exc:
            messagebox.showerror("Invalid JSON", f"Failed to read list.json:\n{exc}")
            return []

    def _build_ui(self):
        form = tk.Frame(self)
        form.pack(fill="x", padx=12, pady=10)

        self.id_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.parts_var = tk.StringVar(value="1")
        self.categories_var = tk.StringVar()

        self._row(form, "ID", self.id_var, 0)
        self._row(form, "Title", self.title_var, 1)
        self._row(form, "Author", self.author_var, 2)
        self._row(form, "Parts", self.parts_var, 3)
        self._row(form, "Categories (comma separated)", self.categories_var, 4)

        btns = tk.Frame(self)
        btns.pack(fill="x", padx=12, pady=6)
        tk.Button(btns, text="Add To Queue", command=self.add_to_queue).pack(side="left")
        tk.Button(btns, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=8)
        tk.Button(btns, text="Clear Queue", command=self.clear_queue).pack(side="left")

        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.listbox = tk.Listbox(list_frame)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        footer = tk.Frame(self)
        footer.pack(fill="x", padx=12, pady=10)
        self.status_var = tk.StringVar(value="Queue: 0")
        tk.Label(footer, textvariable=self.status_var).pack(side="left")
        tk.Button(footer, text="Save To list.json", command=self.save).pack(side="right")

    def _row(self, parent, label, var, row):
        tk.Label(parent, text=label, width=28, anchor="w").grid(row=row, column=0, sticky="w", pady=4)
        entry = tk.Entry(parent, textvariable=var)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        self._enable_paste(entry)
        parent.grid_columnconfigure(1, weight=1)

    def _enable_paste(self, widget):
        # Explicit paste bindings + context menu for environments that don't enable it by default.
        def do_paste(_event=None):
            try:
                text = widget.clipboard_get()
            except Exception:
                return "break"
            try:
                widget.insert(tk.INSERT, text)
            except Exception:
                return "break"
            return "break"

        widget.bind("<Control-v>", do_paste)
        widget.bind("<Control-V>", do_paste)
        widget.bind("<Shift-Insert>", do_paste)
        widget.bind("<Control-Insert>", do_paste)

        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Paste", command=do_paste)

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)
        widget.bind("<ButtonRelease-3>", lambda e: menu.grab_release())

    def _bind_global_clipboard_keys(self):
        # Ensure keyboard paste works even if focus or platform bindings differ.
        def focused_paste(event):
            widget = self.focus_get()
            if widget is None:
                return "break"
            try:
                text = self.clipboard_get()
            except Exception:
                return "break"
            try:
                widget.insert(tk.INSERT, text)
            except Exception:
                return "break"
            return "break"

        self.bind_all("<Control-v>", focused_paste)
        self.bind_all("<Control-V>", focused_paste)
        self.bind_all("<Shift-Insert>", focused_paste)
        self.bind_all("<Control-Insert>", focused_paste)

    def add_to_queue(self):
        book_id = self.id_var.get().strip()
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        parts_raw = self.parts_var.get().strip()
        categories_raw = self.categories_var.get().strip()

        if not book_id or not title or not author:
            messagebox.showwarning("Missing fields", "ID, Title, and Author are required.")
            return

        try:
            parts = int(parts_raw)
            if parts < 1:
                raise ValueError("Parts must be >= 1")
        except Exception:
            messagebox.showwarning("Invalid parts", "Parts must be a positive integer.")
            return

        categories = [c.strip() for c in categories_raw.split(",") if c.strip()]
        if not categories:
            messagebox.showwarning("Missing categories", "At least one category is required.")
            return

        if book_id in self.existing_ids:
            messagebox.showwarning("Duplicate ID", "This ID already exists in list.json.")
            return
        if any(b["id"] == book_id for b in self.pending):
            messagebox.showwarning("Duplicate ID", "This ID already exists in the queue.")
            return

        entry = {
            "id": book_id,
            "title": title,
            "parts": parts,
            "categories": categories,
            "author": author,
        }
        self.pending.append(entry)
        self._refresh_list()
        self._clear_form()

    def remove_selected(self):
        selection = list(self.listbox.curselection())
        if not selection:
            return
        for idx in reversed(selection):
            del self.pending[idx]
        self._refresh_list()

    def clear_queue(self):
        self.pending = []
        self._refresh_list()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for entry in self.pending:
            line = f"{entry['id']} | {entry['title']} | {entry['author']} | {entry['parts']} | {', '.join(entry['categories'])}"
            self.listbox.insert(tk.END, line)
        self.status_var.set(f"Queue: {len(self.pending)}")

    def _clear_form(self):
        self.id_var.set("")
        self.title_var.set("")
        self.author_var.set("")
        self.parts_var.set("1")
        self.categories_var.set("")

    def save(self):
        if not self.pending:
            messagebox.showinfo("Nothing to save", "Queue is empty.")
            return

        latest = self._load_existing()
        latest_ids = {e.get("id") for e in latest}
        collisions = [b["id"] for b in self.pending if b["id"] in latest_ids]
        if collisions:
            messagebox.showerror(
                "Duplicate IDs",
                "These IDs already exist in list.json:\n" + "\n".join(collisions),
            )
            return

        latest.extend(self.pending)
        try:
            self.list_path.write_text(
                json.dumps(latest, ensure_ascii=False, indent=4),
                encoding="utf-8",
            )
        except Exception as exc:
            messagebox.showerror("Write failed", f"Failed to write list.json:\n{exc}")
            return

        self.existing_entries = latest
        self.existing_ids = {e.get("id") for e in self.existing_entries}
        self.pending = []
        self._refresh_list()
        messagebox.showinfo("Saved", "New books were added to list.json.")


if __name__ == "__main__":
    app = BookTool()
    app.mainloop()
