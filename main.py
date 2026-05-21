import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ---------- File ----------
DATA_FILE = "workouts.json"

# ---------- Data functions ----------
def load_workouts():
    """Load workouts from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_workouts(workouts):
    """Save workouts to JSON file"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(workouts, f, indent=4, ensure_ascii=False)

# ---------- Validation ----------
def validate_date(date_str):
    """Check if date is in YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_duration(duration_str):
    """Check if duration is a positive number"""
    try:
        duration = float(duration_str)
        return duration > 0
    except ValueError:
        return False

# ---------- GUI Application ----------
class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")
        self.root.resizable(True, True)

        # Data
        self.workouts = load_workouts()
        self.filtered_workouts = self.workouts.copy()

        # Create UI
        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # ---------- Input Form ----------
        form_frame = ttk.LabelFrame(main_frame, text="Добавить тренировку", padding=10)
        form_frame.pack(fill="x", pady=5)

        # Date
        ttk.Label(form_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(form_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Workout type
        ttk.Label(form_frame, text="Тип тренировки:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.type_combo = ttk.Combobox(form_frame, values=["Бег", "Силовая", "Йога", "Плавание", "Велосипед", "Футбол"], width=15)
        self.type_combo.set("Бег")
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)

        # Duration
        ttk.Label(form_frame, text="Длительность (мин):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.duration_entry = ttk.Entry(form_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)

        # Add button
        self.add_btn = ttk.Button(form_frame, text="➕ Добавить тренировку", command=self.add_workout)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        # ---------- Filter Frame ----------
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Тип тренировки:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_type_combo = ttk.Combobox(filter_frame, values=["Все"] + ["Бег", "Силовая", "Йога", "Плавание", "Велосипед", "Футбол"], width=15)
        self.filter_type_combo.set("Все")
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combo.bind("<<ComboboxSelected>>", self.apply_filter)

        ttk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5, pady=5)

        self.filter_btn = ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=4, padx=10, pady=5)

        self.clear_filter_btn = ttk.Button(filter_frame, text="🗑 Сбросить фильтр", command=self.clear_filter)
        self.clear_filter_btn.grid(row=0, column=5, padx=5, pady=5)

        # ---------- Table ----------
        table_frame = ttk.LabelFrame(main_frame, text="Список тренировок", padding=10)
        table_frame.pack(fill="both", expand=True, pady=5)

        columns = ("ID", "Дата", "Тип тренировки", "Длительность (мин)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        self.tree.heading("ID", text="№")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип тренировки", text="Тип тренировки")
        self.tree.heading("Длительность (мин)", text="Длительность (мин)")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Дата", width=100, anchor="center")
        self.tree.column("Тип тренировки", width=150)
        self.tree.column("Длительность (мин)", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- Delete Button ----------
        delete_frame = ttk.Frame(main_frame)
        delete_frame.pack(fill="x", pady=5)

        self.delete_btn = ttk.Button(delete_frame, text="🗑 Удалить выбранную тренировку", command=self.delete_workout)
        self.delete_btn.pack(side="left", padx=5)

        self.clear_all_btn = ttk.Button(delete_frame, text="⚠️ Очистить всё", command=self.clear_all)
        self.clear_all_btn.pack(side="left", padx=5)

        # Stats label
        self.stats_label = ttk.Label(main_frame, text="")
        self.stats_label.pack(pady=5)

    def add_workout(self):
        """Add a new workout"""
        date = self.date_entry.get().strip()
        workout_type = self.type_combo.get()
        duration = self.duration_entry.get().strip()

        # Validation
        if not validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте ГГГГ-ММ-ДД (например, 2026-05-22)")
            return

        if not workout_type:
            messagebox.showerror("Ошибка", "Выберите тип тренировки!")
            return

        if not validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return

        # Create workout record
        workout = {
            "date": date,
            "type": workout_type,
            "duration": float(duration)
        }
        self.workouts.append(workout)
        save_workouts(self.workouts)

        # Clear input fields
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_combo.set("Бег")
        self.duration_entry.delete(0, tk.END)

        # Update table
        self.apply_filter()
        messagebox.showinfo("Успех", "Тренировка добавлена!")

    def apply_filter(self, event=None):
        """Apply filters to the table"""
        filter_type = self.filter_type_combo.get()
        filter_date = self.filter_date_entry.get().strip()

        self.filtered_workouts = self.workouts.copy()

        # Filter by type
        if filter_type != "Все" and filter_type:
            self.filtered_workouts = [w for w in self.filtered_workouts if w["type"] == filter_type]

        # Filter by date
        if filter_date:
            if validate_date(filter_date):
                self.filtered_workouts = [w for w in self.filtered_workouts if w["date"] == filter_date]
            else:
                messagebox.showwarning("Предупреждение", "Неверный формат даты для фильтра!\nИспользуйте ГГГГ-ММ-ДД")

        self.update_table()

    def clear_filter(self):
        """Clear all filters"""
        self.filter_type_combo.set("Все")
        self.filter_date_entry.delete(0, tk.END)
        self.apply_filter()

    def update_table(self):
        """Update the table with filtered workouts"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add workouts
        for i, workout in enumerate(self.filtered_workouts, 1):
            self.tree.insert("", "end", values=(
                i,
                workout["date"],
                workout["type"],
                f"{workout['duration']} мин"
            ))

        # Update stats
        total_duration = sum(w["duration"] for w in self.filtered_workouts)
        self.stats_label.config(text=f"Всего тренировок: {len(self.filtered_workouts)} | Общая длительность: {total_duration} мин")

    def delete_workout(self):
        """Delete selected workout"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления!")
            return

        # Get the index from the table
        item = self.tree.item(selected[0])
        values = item['values']
        if not values:
            return

        # Find and remove from original list
        date_to_delete = values[1]
        type_to_delete = values[2]
        duration_str = values[3].replace(" мин", "")

        for i, workout in enumerate(self.workouts):
            if (workout["date"] == date_to_delete and
                workout["type"] == type_to_delete and
                str(workout["duration"]) == duration_str):
                del self.workouts[i]
                break

        save_workouts(self.workouts)
        self.apply_filter()
        messagebox.showinfo("Успех", "Тренировка удалена!")

    def clear_all(self):
        """Delete all workouts"""
        if messagebox.askyesno("Подтверждение", "Удалить ВСЕ тренировки? Это действие нельзя отменить!"):
            self.workouts = []
            save_workouts(self.workouts)
            self.apply_filter()
            messagebox.showinfo("Успех", "Все тренировки удалены!")


# ---------- Main ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlannerApp(root)
    root.mainloop()
