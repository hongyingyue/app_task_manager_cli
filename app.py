from models import Task, TaskManager
import threading
import time
import signal
import sys

class TimeoutManager:
    """Manages session timeout functionality"""
    
    def __init__(self, timeout_seconds=180):  # 3 minutes = 180 seconds
        self.timeout_seconds = timeout_seconds
        self.last_activity = time.time()
        self.timeout_thread = None
        self.is_running = False
        self.app_instance = None
    
    def set_app_instance(self, app):
        """Set reference to the main app instance"""
        self.app_instance = app
    
    def reset_activity(self):
        """Reset the last activity time"""
        self.last_activity = time.time()
    
    def start_timeout(self):
        """Start the timeout monitoring thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.reset_activity()
        self.timeout_thread = threading.Thread(target=self._timeout_monitor, daemon=True)
        self.timeout_thread.start()
    
    def stop_timeout(self):
        """Stop the timeout monitoring thread"""
        self.is_running = False
        if self.timeout_thread and self.timeout_thread.is_alive():
            self.timeout_thread.join(timeout=1)
    
    def _timeout_monitor(self):
        """Monitor for timeout in a separate thread"""
        while self.is_running:
            time.sleep(1)  # Check every second
            
            if not self.is_running:
                break
                
            current_time = time.time()
            inactive_time = current_time - self.last_activity
            
            if inactive_time >= self.timeout_seconds:
                print(f"\n\n⚠️  Session timeout! No activity for {self.timeout_seconds // 60} minutes.")
                print("Application will exit automatically...")
                if self.app_instance:
                    self.app_instance.running = False
                break

class TaskManagerApp:
    """Task management application - handles user interaction"""
    def __init__(self):
        self.manager = TaskManager()
        self.running = True
        self.timeout_manager = TimeoutManager()
        self.timeout_manager.set_app_instance(self)
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*40)
        print("          Task Management System")
        print("="*40)
        print("1. Add Task")
        print("2. View Task List")
        print("3. Complete Task")
        print("4. Delete Task")
        print("5. Statistics")
        print("6. Task History")
        print("7. Export Tasks")
        print("8. Import Tasks")
        print("9. Clear All Tasks")
        print("0. Exit Program")
        print("-"*40)
    
    def get_user_choice(self):
        """Get user choice"""
        try:
            choice = int(input("Please select an operation (0-9): "))
            self.timeout_manager.reset_activity()  # Reset timeout on user input
            return choice
        except ValueError:
            self.timeout_manager.reset_activity()  # Reset timeout even on invalid input
            return 0
    
    def handle_add_task(self):
        """Handle adding task"""
        title = input("Please enter task title: ").strip()
        self.timeout_manager.reset_activity()  # Reset timeout on user input
        if not title:
            print("Task title cannot be empty!")
            return
        
        description = input("Please enter task description (optional): ").strip()
        self.timeout_manager.reset_activity()  # Reset timeout on user input
        self.manager.add_task(title, description)
    
    def handle_complete_task(self):
        """Handle completing task"""
        self.manager.list_tasks()
        if not self.manager.tasks:
            return
        
        try:
            task_num = int(input("Please enter the task number to complete: "))
            self.timeout_manager.reset_activity()  # Reset timeout on user input
            self.manager.complete_task(task_num)
        except ValueError:
            self.timeout_manager.reset_activity()  # Reset timeout even on invalid input
            print("Please enter a valid number!")
    
    def handle_delete_task(self):
        """Handle deleting task"""
        self.manager.list_tasks()
        if not self.manager.tasks:
            return
        
        try:
            task_num = int(input("Please enter the task number to delete: "))
            self.timeout_manager.reset_activity()  # Reset timeout on user input
            self.manager.delete_task(task_num)
        except ValueError:
            self.timeout_manager.reset_activity()  # Reset timeout even on invalid input
            print("Please enter a valid number!")
    
    def show_statistics(self):
        """Display statistics"""
        total, completed, pending = self.manager.get_task_count()
        print(f"\n=== Statistics ===")
        print(f"Total tasks: {total}")
        print(f"Completed: {completed}")
        print(f"Pending: {pending}")
        if total > 0:
            completion_rate = (completed / total) * 100
            print(f"Completion rate: {completion_rate:.1f}%")
    
    def handle_task_history(self):
        """Handle showing task history"""
        self.manager.get_task_history()
    
    def handle_export_tasks(self):
        """Handle exporting tasks"""
        filename = input("Enter filename for export (or press Enter for auto-generated name): ").strip()
        self.timeout_manager.reset_activity()  # Reset timeout on user input
        if filename:
            self.manager.export_tasks(filename)
        else:
            self.manager.export_tasks()
    
    def handle_import_tasks(self):
        """Handle importing tasks"""
        filename = input("Enter filename to import from: ").strip()
        self.timeout_manager.reset_activity()  # Reset timeout on user input
        if filename:
            self.manager.import_tasks(filename)
        else:
            print("Please enter a valid filename!")
    
    def handle_clear_all_tasks(self):
        """Handle clearing all tasks"""
        confirm = input("Are you sure you want to clear all tasks? (yes/no): ").strip().lower()
        self.timeout_manager.reset_activity()  # Reset timeout on user input
        if confirm in ['yes', 'y']:
            self.manager.clear_all_tasks()
        else:
            print("Operation cancelled.")
    
    def run(self):
        """Run the main application loop"""
        print("Welcome to the Task Management System!")
        print("⏰ Session timeout: 3 minutes of inactivity will auto-exit the app")
        
        # Start timeout monitoring
        self.timeout_manager.start_timeout()
        
        try:
            while self.running:
                self.show_menu()
                choice = self.get_user_choice()
                
                if choice == 1:
                    self.handle_add_task()
                elif choice == 2:
                    self.manager.list_tasks()
                elif choice == 3:
                    self.handle_complete_task()
                elif choice == 4:
                    self.handle_delete_task()
                elif choice == 5:
                    self.show_statistics()
                elif choice == 6:
                    self.handle_task_history()
                elif choice == 7:
                    self.handle_export_tasks()
                elif choice == 8:
                    self.handle_import_tasks()
                elif choice == 9:
                    self.handle_clear_all_tasks()
                elif choice == 0:
                    print("Thank you for using! Goodbye!")
                    self.running = False
                else:
                    print("Invalid choice, please enter a number between 0-9!")
                
                if self.running:
                    input("\nPress Enter to continue...")
                    self.timeout_manager.reset_activity()  # Reset timeout on continue
        finally:
            # Stop timeout monitoring when exiting
            self.timeout_manager.stop_timeout()


# Program entry point
if __name__ == "__main__":
    app = TaskManagerApp()
    app.run()
