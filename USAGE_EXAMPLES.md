# Usage Examples

This document provides practical examples of how to use the Task Management CLI Application.

## Quick Start

### 1. Launch the Application
```bash
python3 app.py
```

### 2. Add Your First Task
```
Please select an operation (0-9): 1
Please enter task title: Learn Python
Please enter task description (optional): Complete the CLI app tutorial
Task 'Learn Python' has been added!
```

### 3. View Your Tasks
```
Please select an operation (0-9): 2

=== Task List ===
1. [○] Learn Python - Complete the CLI app tutorial (Created: 2025-09-09 15:11)
```

## Common Workflows

### Daily Task Management
```
1. Add Task: "Check emails"
2. Add Task: "Team meeting at 2 PM"
3. Add Task: "Review project proposal"
4. View Task List
5. Complete Task: Mark "Check emails" as done
6. View Statistics
```

### Project Planning
```
1. Add Task: "Research requirements"
2. Add Task: "Create wireframes"
3. Add Task: "Develop prototype"
4. Add Task: "User testing"
5. Add Task: "Final implementation"
6. Export Tasks: Save as "project_plan.json"
```

### Weekly Review
```
1. View Task History
2. View Statistics
3. Export Tasks: Create weekly backup
4. Clear completed tasks (manually delete)
```

## Advanced Features

### Data Backup and Recovery
```bash
# Export tasks
Please select an operation (0-9): 7
Enter filename for export: backup_2025_09_09.json

# Import tasks later
Please select an operation (0-9): 8
Enter filename to import from: backup_2025_09_09.json
```

### Bulk Operations
```bash
# Clear all tasks (with confirmation)
Please select an operation (0-9): 9
Are you sure you want to clear all tasks? (yes/no): yes
```

### Session Management
- The app automatically saves your progress
- 3-minute timeout for security
- All user input resets the timeout counter

## Tips and Best Practices

### Task Naming
- Use clear, descriptive titles
- Keep titles concise but informative
- Use consistent naming conventions

### Descriptions
- Add context when helpful
- Include deadlines or priorities
- Use descriptions for additional details

### Regular Maintenance
- Review and complete tasks regularly
- Export backups weekly
- Clear completed tasks periodically
- Use statistics to track productivity

### File Management
- Export important task lists
- Keep backups in different locations
- Use descriptive filenames with dates

## Troubleshooting

### Common Commands
```bash
# Run tests
python3 -m unittest test_unittest -v

# Check file permissions
ls -la tasks.json

# View application files
ls -la
```

### Data Recovery
If your `tasks.json` file is corrupted:
1. Check for backup files
2. Import from exported files
3. Start fresh if necessary

### Performance
- The app handles thousands of tasks efficiently
- Large task lists may take longer to display
- Consider exporting old tasks to separate files
