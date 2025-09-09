import json
import os
from datetime import datetime


class Task:
    """Task class - represents a single task"""
    def __init__(self, title, description="", created_at=None, completed_at=None):
        self.title = title
        self.description = description
        self.completed = False
        self.created_at = created_at or datetime.now()
        self.completed_at = completed_at
    
    def mark_completed(self):
        """Mark task as completed"""
        self.completed = True
        self.completed_at = datetime.now()
    
    def mark_pending(self):
        """Mark task as pending"""
        self.completed = False
        self.completed_at = None
    
    def to_dict(self):
        """Convert task to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create task from dictionary (for JSON deserialization)"""
        created_at = None
        completed_at = None
        
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        if data.get('completed_at'):
            completed_at = datetime.fromisoformat(data['completed_at'])
        
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            created_at=created_at,
            completed_at=completed_at
        )
        task.completed = data.get('completed', False)
        return task
    
    def __str__(self):
        """Return string representation of the task"""
        status = "✓" if self.completed else "○"
        created_str = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"[{status}] {self.title} - {self.description} (Created: {created_str})"


class TaskManager:
    """Task manager class - manages all tasks with data persistence"""
    def __init__(self, data_file="tasks.json"):
        self.tasks = []
        self.data_file = data_file
        self.load_tasks()
    
    def add_task(self, title, description=""):
        """Add new task"""
        task = Task(title, description)
        self.tasks.append(task)
        print(f"Task '{title}' has been added!")
        self.save_tasks()
    
    def list_tasks(self):
        """Display all tasks"""
        if not self.tasks:
            print("No tasks available")
            return
        
        print("\n=== Task List ===")
        for i, task in enumerate(self.tasks, 1):
            print(f"{i}. {task}")
        print()
    
    def complete_task(self, task_num):
        """Complete specified task"""
        if 1 <= task_num <= len(self.tasks):
            self.tasks[task_num - 1].mark_completed()
            print(f"Task {task_num} has been marked as completed!")
            self.save_tasks()
        else:
            print("Invalid task number!")
    
    def delete_task(self, task_num):
        """Delete specified task"""
        if 1 <= task_num <= len(self.tasks):
            deleted_task = self.tasks.pop(task_num - 1)
            print(f"Task '{deleted_task.title}' has been deleted!")
            self.save_tasks()
        else:
            print("Invalid task number!")
    
    def get_task_count(self):
        """Get task statistics"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.completed)
        pending = total - completed
        return total, completed, pending
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            tasks_data = [task.to_dict() for task in self.tasks]
            with open(self.data_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    tasks_data = json.load(f)
                self.tasks = [Task.from_dict(task_data) for task_data in tasks_data]
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []
    
    def clear_all_tasks(self):
        """Clear all tasks"""
        self.tasks = []
        self.save_tasks()
        print("All tasks have been cleared!")
    
    def export_tasks(self, filename=None):
        """Export tasks to a specific file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tasks_export_{timestamp}.json"
        
        try:
            tasks_data = [task.to_dict() for task in self.tasks]
            with open(filename, 'w') as f:
                json.dump(tasks_data, f, indent=2)
            print(f"Tasks exported to {filename}")
        except Exception as e:
            print(f"Error exporting tasks: {e}")
    
    def import_tasks(self, filename):
        """Import tasks from a file"""
        try:
            if not os.path.exists(filename):
                print(f"File {filename} not found!")
                return
            
            with open(filename, 'r') as f:
                tasks_data = json.load(f)
            
            imported_tasks = [Task.from_dict(task_data) for task_data in tasks_data]
            self.tasks.extend(imported_tasks)
            self.save_tasks()
            print(f"Successfully imported {len(imported_tasks)} tasks from {filename}")
        except Exception as e:
            print(f"Error importing tasks: {e}")
    
    def get_task_history(self):
        """Get task history with completion times"""
        if not self.tasks:
            print("No task history available")
            return
        
        print("\n=== Task History ===")
        for i, task in enumerate(self.tasks, 1):
            status = "✓" if task.completed else "○"
            created_str = task.created_at.strftime("%Y-%m-%d %H:%M")
            completed_str = task.completed_at.strftime("%Y-%m-%d %H:%M") if task.completed_at else "Not completed"
            print(f"{i}. [{status}] {task.title}")
            print(f"   Created: {created_str}")
            print(f"   Completed: {completed_str}")
            print(f"   Description: {task.description}")
            print()
