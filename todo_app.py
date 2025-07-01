import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Manager")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Data file for persistence
        self.data_file = "todo_data.json"
        self.tasks = []
        
        # Load existing tasks
        self.load_tasks()
        
        # Create GUI elements
        self.create_widgets()
        
        # Load tasks into the display
        self.refresh_task_list()
    
    def create_widgets(self):
        # Main title
        title_label = tk.Label(
            self.root, 
            text="📝 My To-Do List", 
            font=("Arial", 24, "bold"), 
            bg='#f0f0f0', 
            fg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # Input frame
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(pady=10, padx=20, fill='x')
        
        # Task entry
        tk.Label(input_frame, text="New Task:", font=("Arial", 12), bg='#f0f0f0').pack(anchor='w')
        self.task_entry = tk.Entry(input_frame, font=("Arial", 12), width=50)
        self.task_entry.pack(side='left', padx=(0, 10), pady=5, fill='x', expand=True)
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        # Priority selection
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(
            input_frame, 
            textvariable=self.priority_var, 
            values=["High", "Medium", "Low"],
            state="readonly",
            width=10
        )
        priority_combo.pack(side='left', padx=(0, 10))
        
        # Add button
        add_btn = tk.Button(
            input_frame, 
            text="Add Task", 
            command=self.add_task,
            bg='#3498db', 
            fg='white', 
            font=("Arial", 10, "bold"),
            relief='flat',
            padx=20
        )
        add_btn.pack(side='left')
        
        # Filter frame
        filter_frame = tk.Frame(self.root, bg='#f0f0f0')
        filter_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(filter_frame, text="Filter:", font=("Arial", 10), bg='#f0f0f0').pack(side='left')
        
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.filter_var, 
            values=["All", "Pending", "Completed", "High Priority", "Medium Priority", "Low Priority"],
            state="readonly",
            width=15
        )
        filter_combo.pack(side='left', padx=10)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_task_list())
        
        # Task list frame
        list_frame = tk.Frame(self.root, bg='#f0f0f0')
        list_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Scrollable task list
        self.task_listbox = tk.Listbox(
            list_frame, 
            font=("Arial", 11),
            selectmode=tk.SINGLE,
            bg='white',
            selectbackground='#3498db',
            selectforeground='white',
            relief='flat',
            borderwidth=1
        )
        
        scrollbar = tk.Scrollbar(list_frame, orient='vertical')
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.task_listbox.yview)
        
        self.task_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=20, padx=20, fill='x')
        
        # Complete button
        complete_btn = tk.Button(
            button_frame, 
            text="✓ Complete", 
            command=self.complete_task,
            bg='#27ae60', 
            fg='white', 
            font=("Arial", 10, "bold"),
            relief='flat',
            padx=20
        )
        complete_btn.pack(side='left', padx=(0, 10))
        
        # Edit button
        edit_btn = tk.Button(
            button_frame, 
            text="✏️ Edit", 
            command=self.edit_task,
            bg='#f39c12', 
            fg='white', 
            font=("Arial", 10, "bold"),
            relief='flat',
            padx=20
        )
        edit_btn.pack(side='left', padx=(0, 10))
        
        # Delete button
        delete_btn = tk.Button(
            button_frame, 
            text="🗑️ Delete", 
            command=self.delete_task,
            bg='#e74c3c', 
            fg='white', 
            font=("Arial", 10, "bold"),
            relief='flat',
            padx=20
        )
        delete_btn.pack(side='left', padx=(0, 10))
        
        # Clear completed button
        clear_btn = tk.Button(
            button_frame, 
            text="Clear Completed", 
            command=self.clear_completed,
            bg='#95a5a6', 
            fg='white', 
            font=("Arial", 10, "bold"),
            relief='flat',
            padx=20
        )
        clear_btn.pack(side='right')
        
        # Statistics frame
        stats_frame = tk.Frame(self.root, bg='#ecf0f1', relief='solid', borderwidth=1)
        stats_frame.pack(pady=10, padx=20, fill='x')
        
        self.stats_label = tk.Label(
            stats_frame, 
            text="", 
            font=("Arial", 10), 
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.stats_label.pack(pady=10)
        
        self.update_statistics()
    
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("Empty Task", "Please enter a task description.")
            return
        
        new_task = {
            'id': len(self.tasks) + 1,
            'text': task_text,
            'priority': self.priority_var.get(),
            'completed': False,
            'created_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'completed_date': None
        }
        
        self.tasks.append(new_task)
        self.task_entry.delete(0, tk.END)
        self.save_tasks()
        self.refresh_task_list()
        self.update_statistics()
        
        messagebox.showinfo("Success", "Task added successfully!")
    
    def complete_task(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to complete.")
            return
        
        # Get the actual task index from filtered list
        display_index = selection[0]
        filtered_tasks = self.get_filtered_tasks()
        
        if display_index >= len(filtered_tasks):
            return
        
        task_to_complete = filtered_tasks[display_index]
        
        # Find the task in the main list and update it
        for task in self.tasks:
            if task['id'] == task_to_complete['id']:
                if task['completed']:
                    messagebox.showinfo("Already Completed", "This task is already completed!")
                    return
                
                task['completed'] = True
                task['completed_date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                break
        
        self.save_tasks()
        self.refresh_task_list()
        self.update_statistics()
        messagebox.showinfo("Success", "Task marked as completed!")
    
    def edit_task(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return
        
        display_index = selection[0]
        filtered_tasks = self.get_filtered_tasks()
        
        if display_index >= len(filtered_tasks):
            return
        
        task_to_edit = filtered_tasks[display_index]
        
        # Get new text from user
        new_text = simpledialog.askstring("Edit Task", "Enter new task description:", 
                                        initialvalue=task_to_edit['text'])
        
        if new_text and new_text.strip():
            # Find and update the task in the main list
            for task in self.tasks:
                if task['id'] == task_to_edit['id']:
                    task['text'] = new_text.strip()
                    break
            
            self.save_tasks()
            self.refresh_task_list()
            messagebox.showinfo("Success", "Task updated successfully!")
    
    def delete_task(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            display_index = selection[0]
            filtered_tasks = self.get_filtered_tasks()
            
            if display_index >= len(filtered_tasks):
                return
            
            task_to_delete = filtered_tasks[display_index]
            
            # Remove from main list
            self.tasks = [task for task in self.tasks if task['id'] != task_to_delete['id']]
            
            self.save_tasks()
            self.refresh_task_list()
            self.update_statistics()
            messagebox.showinfo("Success", "Task deleted successfully!")
    
    def clear_completed(self):
        completed_tasks = [task for task in self.tasks if task['completed']]
        if not completed_tasks:
            messagebox.showinfo("No Completed Tasks", "There are no completed tasks to clear.")
            return
        
        if messagebox.askyesno("Confirm Clear", f"Are you sure you want to delete {len(completed_tasks)} completed task(s)?"):
            self.tasks = [task for task in self.tasks if not task['completed']]
            self.save_tasks()
            self.refresh_task_list()
            self.update_statistics()
            messagebox.showinfo("Success", "Completed tasks cleared!")
    
    def get_filtered_tasks(self):
        filter_value = self.filter_var.get()
        
        if filter_value == "All":
            return self.tasks
        elif filter_value == "Pending":
            return [task for task in self.tasks if not task['completed']]
        elif filter_value == "Completed":
            return [task for task in self.tasks if task['completed']]
        elif filter_value == "High Priority":
            return [task for task in self.tasks if task['priority'] == 'High']
        elif filter_value == "Medium Priority":
            return [task for task in self.tasks if task['priority'] == 'Medium']
        elif filter_value == "Low Priority":
            return [task for task in self.tasks if task['priority'] == 'Low']
        else:
            return self.tasks
    
    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        
        filtered_tasks = self.get_filtered_tasks()
        
        for task in filtered_tasks:
            # Format the display text
            status = "✓" if task['completed'] else "○"
            priority_symbol = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[task['priority']]
            
            display_text = f"{status} {priority_symbol} {task['text']}"
            if task['completed']:
                display_text += f" (Completed: {task['completed_date']})"
            
            self.task_listbox.insert(tk.END, display_text)
            
            # Color code based on status and priority
            if task['completed']:
                self.task_listbox.itemconfig(tk.END, {'fg': '#7f8c8d'})
            elif task['priority'] == 'High':
                self.task_listbox.itemconfig(tk.END, {'fg': '#e74c3c'})
            elif task['priority'] == 'Medium':
                self.task_listbox.itemconfig(tk.END, {'fg': '#f39c12'})
            else:
                self.task_listbox.itemconfig(tk.END, {'fg': '#27ae60'})
    
    def update_statistics(self):
        total_tasks = len(self.tasks)
        completed_tasks = len([task for task in self.tasks if task['completed']])
        pending_tasks = total_tasks - completed_tasks
        
        high_priority = len([task for task in self.tasks if task['priority'] == 'High' and not task['completed']])
        
        stats_text = f"Total: {total_tasks} | Completed: {completed_tasks} | Pending: {pending_tasks} | High Priority Pending: {high_priority}"
        self.stats_label.config(text=stats_text)
    
    def save_tasks(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save tasks: {str(e)}")
    
    def load_tasks(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.tasks = json.load(f)
            else:
                self.tasks = []
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load tasks: {str(e)}")
            self.tasks = []

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()