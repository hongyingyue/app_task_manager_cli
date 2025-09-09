# Task Management CLI Application

A powerful command-line task management system built with Python that helps you organize, track, and manage your daily tasks with persistent data storage and automatic session timeout.

## 🚀 Features

### Core Task Management
- ✅ **Add Tasks** - Create new tasks with titles and optional descriptions
- 📋 **View Tasks** - Display all tasks with completion status and timestamps
- ✔️ **Complete Tasks** - Mark tasks as completed with automatic timestamp
- 🗑️ **Delete Tasks** - Remove unwanted tasks from your list
- 📊 **Statistics** - View completion rates and task counts

### Data Management
- 💾 **Persistent Storage** - Tasks are automatically saved to JSON file
- 📤 **Export Tasks** - Save tasks to custom or auto-generated files
- 📥 **Import Tasks** - Load tasks from external JSON files
- 🗂️ **Task History** - View detailed task information with creation/completion times
- 🧹 **Clear All Tasks** - Bulk delete all tasks with confirmation

### Advanced Features
- ⏰ **Session Timeout** - Automatic exit after 3 minutes of inactivity
- 🔄 **Duplicate Detection** - Remove tasks with duplicate titles
- 🧪 **Comprehensive Testing** - Full test suite with 64+ test cases
- 🏗️ **Modular Design** - Clean separation of concerns with separate model and app files

## 📋 Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## 🛠️ Installation

1. **Clone or download** the application files:
   ```bash
   # Ensure you have these files in your directory:
   # - app.py (main application)
   # - models.py (data models)
   # - test_unittest.py (test suite)
   ```

2. **Navigate** to the application directory:
   ```bash
   cd cli_app
   ```

3. **Run the application**:
   ```bash
   python3 app.py
   ```

## 🎯 Usage Guide

### Starting the Application

```bash
python3 app.py
```

You'll see the welcome message and timeout notification:
```
Welcome to the Task Management System!
⏰ Session timeout: 3 minutes of inactivity will auto-exit the app
```

### Main Menu Options

```
========================================
          Task Management System
========================================
1. Add Task
2. View Task List
3. Complete Task
4. Delete Task
5. Statistics
6. Task History
7. Export Tasks
8. Import Tasks
9. Clear All Tasks
0. Exit Program
----------------------------------------
```

### 1. Add Task
- Enter a task title (required)
- Optionally add a description
- Task is automatically saved with creation timestamp

**Example:**
```
Please enter task title: Buy groceries
Please enter task description (optional): Milk, bread, eggs
Task 'Buy groceries' has been added!
```

### 2. View Task List
Displays all tasks with:
- Task number
- Completion status (✓ for completed, ○ for pending)
- Title and description
- Creation timestamp

**Example:**
```
=== Task List ===
1. [○] Buy groceries - Milk, bread, eggs (Created: 2025-09-09 14:35:52)
2. [✓] Finish project - Complete the task management app (Created: 2025-09-09 14:35:53)
```

### 3. Complete Task
- View the task list
- Enter the task number to mark as completed
- Completion timestamp is automatically recorded

### 4. Delete Task
- View the task list
- Enter the task number to delete
- Task is permanently removed

### 5. Statistics
View comprehensive task statistics:
```
=== Statistics ===
Total tasks: 5
Completed: 2
Pending: 3
Completion rate: 40.0%
```

### 6. Task History
View detailed information about all tasks including:
- Creation and completion timestamps
- Full task details
- Chronological order

### 7. Export Tasks
Save your tasks to a file:
- Enter custom filename, or
- Press Enter for auto-generated filename with timestamp

**Example:**
```
Enter filename for export (or press Enter for auto-generated name): my_tasks.json
Tasks exported to: my_tasks.json
```

### 8. Import Tasks
Load tasks from an external JSON file:
```
Enter filename to import from: backup_tasks.json
Tasks imported from: backup_tasks.json
```

### 9. Clear All Tasks
Remove all tasks with confirmation:
```
Are you sure you want to clear all tasks? (yes/no): yes
All tasks have been cleared!
```

### 0. Exit Program
Safely exit the application with a goodbye message.

## ⏰ Session Timeout

The application includes a **3-minute session timeout** for security:
- ⚠️ **Automatic exit** after 3 minutes of inactivity
- 🔄 **Activity reset** on any user input (menu selection, task entry, etc.)
- 📢 **Clear warning** when timeout occurs
- 🛡️ **Secure operation** - prevents unauthorized access

## 💾 Data Storage

### Automatic Persistence
- Tasks are automatically saved to `tasks.json`
- Data persists between application sessions
- No manual save required

### File Format
Tasks are stored in JSON format with full metadata:
```json
[
  {
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "completed": false,
    "created_at": "2025-09-09T14:35:52.863632",
    "completed_at": null
  }
]
```

### Backup and Recovery
- Export functionality creates backup files
- Import functionality restores from backups
- Manual file editing supported (use valid JSON format)

## 🧪 Testing

The application includes a comprehensive test suite:

### Run All Tests
```bash
python3 -m unittest test_unittest -v
```

### Test Categories
- **Task Class Tests** - Core task functionality
- **TaskManager Tests** - Data management and persistence
- **TaskManagerApp Tests** - User interface and interaction
- **Integration Tests** - End-to-end workflows
- **TimeoutManager Tests** - Session timeout functionality

### Test Coverage
- ✅ 64+ test cases
- ✅ All major functionality covered
- ✅ Edge cases and error handling
- ✅ Data persistence testing
- ✅ User input simulation

## 🏗️ Architecture

### File Structure
```
cli_app/
├── app.py              # Main application and user interface
├── models.py           # Task and TaskManager classes
├── test_unittest.py    # Comprehensive test suite
├── tasks.json          # Persistent data storage (auto-generated)
└── README.md           # This documentation
```

### Class Design
- **Task** - Individual task representation with timestamps
- **TaskManager** - Data management and persistence
- **TaskManagerApp** - User interface and application flow
- **TimeoutManager** - Session timeout and security

### Key Design Principles
- **Separation of Concerns** - Models separate from UI
- **Data Persistence** - Automatic JSON-based storage
- **Error Handling** - Graceful handling of invalid input
- **User Experience** - Clear prompts and feedback
- **Security** - Session timeout protection

## 🔧 Customization

### Changing Timeout Duration
Edit the timeout in `app.py`:
```python
# In TaskManagerApp.__init__()
self.timeout_manager = TimeoutManager(timeout_seconds=300)  # 5 minutes
```

### Modifying Data File Location
Edit the data file in `models.py`:
```python
# In TaskManager.__init__()
self.data_file = "custom_tasks.json"
```

## 🐛 Troubleshooting

### Common Issues

**"Error loading tasks: Expecting value: line 1 column 1 (char 0)"**
- This is normal for new installations
- The error disappears after adding your first task

**Tasks not persisting between sessions**
- Ensure the application has write permissions in the directory
- Check that `tasks.json` is not corrupted

**Timeout not working**
- Verify Python threading support
- Check system time synchronization

### Getting Help
- Check the test suite for usage examples
- Review the source code comments
- Ensure Python 3.6+ compatibility

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- All tests pass (`python3 -m unittest test_unittest -v`)
- Code follows existing style and patterns
- New features include appropriate tests
- Documentation is updated

## 🎉 Features in Action

### Quick Start Example
```bash
$ python3 app.py
Welcome to the Task Management System!
⏰ Session timeout: 3 minutes of inactivity will auto-exit the app

========================================
          Task Management System
========================================
1. Add Task
2. View Task List
3. Complete Task
4. Delete Task
5. Statistics
6. Task History
7. Export Tasks
8. Import Tasks
9. Clear All Tasks
0. Exit Program
----------------------------------------
Please select an operation (0-9): 1
Please enter task title: Learn Python
Please enter task description (optional): Complete the CLI app tutorial
Task 'Learn Python' has been added!

Press Enter to continue...
```

---

**Happy Task Managing! 🎯**
