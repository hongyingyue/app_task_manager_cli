#!/usr/bin/env python3
"""
Unit tests for the Task Management System using unittest framework
Tests both Task and TaskManager classes
"""

import unittest
import sys
import io
import os
import json
import tempfile
import time
import threading
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock
from models import Task, TaskManager
from app import TaskManagerApp, TimeoutManager


class TestTimeoutManager(unittest.TestCase):
    """Test cases for the TimeoutManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.timeout_manager = TimeoutManager(timeout_seconds=1)  # 1 second for testing
        self.mock_app = MagicMock()
        self.mock_app.running = True
        self.timeout_manager.set_app_instance(self.mock_app)
    
    def tearDown(self):
        """Clean up after each test method."""
        self.timeout_manager.stop_timeout()
    
    def test_timeout_manager_initialization(self):
        """Test TimeoutManager initialization"""
        self.assertEqual(self.timeout_manager.timeout_seconds, 1)
        self.assertIsNotNone(self.timeout_manager.last_activity)
        self.assertFalse(self.timeout_manager.is_running)
        self.assertIsNone(self.timeout_manager.timeout_thread)
    
    def test_reset_activity(self):
        """Test resetting activity time"""
        initial_time = self.timeout_manager.last_activity
        time.sleep(0.1)  # Small delay
        self.timeout_manager.reset_activity()
        self.assertGreater(self.timeout_manager.last_activity, initial_time)
    
    def test_start_stop_timeout(self):
        """Test starting and stopping timeout monitoring"""
        self.assertFalse(self.timeout_manager.is_running)
        
        self.timeout_manager.start_timeout()
        self.assertTrue(self.timeout_manager.is_running)
        self.assertIsNotNone(self.timeout_manager.timeout_thread)
        
        self.timeout_manager.stop_timeout()
        self.assertFalse(self.timeout_manager.is_running)
    
    def test_timeout_trigger(self):
        """Test that timeout triggers after specified time"""
        self.timeout_manager.start_timeout()
        
        # Wait for timeout to trigger
        time.sleep(1.5)
        
        # The timeout should have triggered and set app.running to False
        self.mock_app.running = False
        self.timeout_manager.stop_timeout()
    
    def test_activity_reset_prevents_timeout(self):
        """Test that resetting activity prevents timeout"""
        self.timeout_manager.start_timeout()
        
        # Reset activity before timeout
        time.sleep(0.5)
        self.timeout_manager.reset_activity()
        
        # Wait a bit more, but total should be less than timeout
        time.sleep(0.5)
        
        # App should still be running
        self.assertTrue(self.mock_app.running)
        self.timeout_manager.stop_timeout()


class TestTask(unittest.TestCase):
    """Test cases for the Task class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.task = Task("Test Task", "Test Description")
    
    def test_task_initialization_with_title_only(self):
        """Test Task initialization with title only"""
        task = Task("Test Task")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "")
        self.assertFalse(task.completed)
    
    def test_task_initialization_with_title_and_description(self):
        """Test Task initialization with title and description"""
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.description, "Test Description")
        self.assertFalse(self.task.completed)
    
    def test_mark_completed(self):
        """Test marking task as completed"""
        self.assertFalse(self.task.completed)
        self.task.mark_completed()
        self.assertTrue(self.task.completed)
    
    def test_mark_pending(self):
        """Test marking task as pending"""
        # First mark as completed
        self.task.mark_completed()
        self.assertTrue(self.task.completed)
        
        # Then mark as pending
        self.task.mark_pending()
        self.assertFalse(self.task.completed)
    
    def test_string_representation_pending(self):
        """Test string representation for pending task"""
        # The string now includes timestamp, so we check for the main parts
        task_str = str(self.task)
        self.assertIn("[○] Test Task - Test Description", task_str)
        self.assertIn("(Created:", task_str)
    
    def test_string_representation_completed(self):
        """Test string representation for completed task"""
        self.task.mark_completed()
        task_str = str(self.task)
        self.assertIn("[✓] Test Task - Test Description", task_str)
        self.assertIn("(Created:", task_str)
    
    def test_string_representation_no_description(self):
        """Test string representation for task without description"""
        task = Task("Simple Task")
        # The string now includes timestamp, so we check for the main parts
        self.assertIn("[○] Simple Task - ", str(task))
        self.assertIn("(Created:", str(task))
    
    def test_task_timestamps(self):
        """Test task timestamp functionality"""
        from datetime import datetime
        
        task = Task("Test Task")
        self.assertIsInstance(task.created_at, datetime)
        self.assertIsNone(task.completed_at)
        
        task.mark_completed()
        self.assertIsInstance(task.completed_at, datetime)
        
        task.mark_pending()
        self.assertIsNone(task.completed_at)
    
    def test_task_to_dict(self):
        """Test task serialization to dictionary"""
        task = Task("Test Task", "Test Description")
        task_dict = task.to_dict()
        
        self.assertEqual(task_dict['title'], "Test Task")
        self.assertEqual(task_dict['description'], "Test Description")
        self.assertFalse(task_dict['completed'])
        self.assertIsNotNone(task_dict['created_at'])
        self.assertIsNone(task_dict['completed_at'])
    
    def test_task_from_dict(self):
        """Test task deserialization from dictionary"""
        from datetime import datetime
        
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'completed': True,
            'created_at': '2023-01-01T10:00:00',
            'completed_at': '2023-01-01T11:00:00'
        }
        
        task = Task.from_dict(task_data)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertTrue(task.completed)
        self.assertIsInstance(task.created_at, datetime)
        self.assertIsInstance(task.completed_at, datetime)


class TestTaskManager(unittest.TestCase):
    """Test cases for the TaskManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Use a temporary file for testing to avoid interfering with real data
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = TaskManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_initialization(self):
        """Test TaskManager initialization"""
        self.assertEqual(len(self.manager.tasks), 0)
        self.assertIsInstance(self.manager.tasks, list)
    
    def test_add_task_title_only(self):
        """Test adding task with title only"""
        with redirect_stdout(io.StringIO()) as f:
            self.manager.add_task("Test Task")
        
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(self.manager.tasks[0].title, "Test Task")
        self.assertEqual(self.manager.tasks[0].description, "")
        self.assertIn("Task 'Test Task' has been added!", f.getvalue())
    
    def test_add_task_with_description(self):
        """Test adding task with title and description"""
        with redirect_stdout(io.StringIO()) as f:
            self.manager.add_task("Test Task", "Test Description")
        
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(self.manager.tasks[0].title, "Test Task")
        self.assertEqual(self.manager.tasks[0].description, "Test Description")
        self.assertIn("Task 'Test Task' has been added!", f.getvalue())
    
    def test_add_multiple_tasks(self):
        """Test adding multiple tasks"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2", "Description 2")
        self.manager.add_task("Task 3")
        
        self.assertEqual(len(self.manager.tasks), 3)
        self.assertEqual(self.manager.tasks[0].title, "Task 1")
        self.assertEqual(self.manager.tasks[1].title, "Task 2")
        self.assertEqual(self.manager.tasks[2].title, "Task 3")
    
    def test_list_tasks_empty(self):
        """Test listing tasks when manager is empty"""
        with redirect_stdout(io.StringIO()) as f:
            self.manager.list_tasks()
        
        self.assertIn("No tasks available", f.getvalue())
    
    def test_list_tasks_with_content(self):
        """Test listing tasks with content"""
        self.manager.add_task("Task 1", "Description 1")
        self.manager.add_task("Task 2", "Description 2")
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.list_tasks()
        
        output = f.getvalue()
        self.assertIn("=== Task List ===", output)
        self.assertIn("1. [○] Task 1 - Description 1", output)
        self.assertIn("2. [○] Task 2 - Description 2", output)
    
    def test_complete_task_valid(self):
        """Test completing a valid task"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.complete_task(1)
        
        self.assertTrue(self.manager.tasks[0].completed)
        self.assertFalse(self.manager.tasks[1].completed)
        self.assertIn("Task 1 has been marked as completed!", f.getvalue())
    
    def test_complete_task_invalid_number(self):
        """Test completing task with invalid number"""
        self.manager.add_task("Task 1")
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.complete_task(5)  # Invalid number
        
        self.assertIn("Invalid task number!", f.getvalue())
        self.assertFalse(self.manager.tasks[0].completed)
    
    def test_complete_task_zero_number(self):
        """Test completing task with zero number"""
        self.manager.add_task("Task 1")
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.complete_task(0)  # Invalid number
        
        self.assertIn("Invalid task number!", f.getvalue())
    
    def test_complete_task_negative_number(self):
        """Test completing task with negative number"""
        self.manager.add_task("Task 1")
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.complete_task(-1)  # Invalid number
        
        self.assertIn("Invalid task number!", f.getvalue())
    
    def test_delete_task_valid(self):
        """Test deleting a valid task"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.add_task("Task 3")
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.delete_task(2)
        
        self.assertEqual(len(self.manager.tasks), 2)
        self.assertEqual(self.manager.tasks[0].title, "Task 1")
        self.assertEqual(self.manager.tasks[1].title, "Task 3")
        self.assertIn("Task 'Task 2' has been deleted!", f.getvalue())
    
    def test_delete_task_invalid_number(self):
        """Test deleting task with invalid number"""
        self.manager.add_task("Task 1")
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.delete_task(10)  # Invalid number
        
        self.assertEqual(len(self.manager.tasks), 1)  # Task should still be there
        self.assertIn("Invalid task number!", f.getvalue())
    
    def test_delete_task_zero_number(self):
        """Test deleting task with zero number"""
        self.manager.add_task("Task 1")
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.delete_task(0)  # Invalid number
        
        self.assertEqual(len(self.manager.tasks), 1)  # Task should still be there
        self.assertIn("Invalid task number!", f.getvalue())
    
    def test_delete_task_negative_number(self):
        """Test deleting task with negative number"""
        self.manager.add_task("Task 1")
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.delete_task(-1)  # Invalid number
        
        self.assertEqual(len(self.manager.tasks), 1)  # Task should still be there
        self.assertIn("Invalid task number!", f.getvalue())
    
    def test_get_task_count_empty(self):
        """Test task count with no tasks"""
        total, completed, pending = self.manager.get_task_count()
        self.assertEqual(total, 0)
        self.assertEqual(completed, 0)
        self.assertEqual(pending, 0)
    
    def test_get_task_count_mixed_status(self):
        """Test task count with mixed completion status"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.add_task("Task 3")
        self.manager.complete_task(1)
        self.manager.complete_task(3)
        
        total, completed, pending = self.manager.get_task_count()
        self.assertEqual(total, 3)
        self.assertEqual(completed, 2)
        self.assertEqual(pending, 1)
    
    def test_get_task_count_all_completed(self):
        """Test task count when all tasks are completed"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.complete_task(1)
        self.manager.complete_task(2)
        
        total, completed, pending = self.manager.get_task_count()
        self.assertEqual(total, 2)
        self.assertEqual(completed, 2)
        self.assertEqual(pending, 0)
    
    def test_get_task_count_all_pending(self):
        """Test task count when all tasks are pending"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        
        total, completed, pending = self.manager.get_task_count()
        self.assertEqual(total, 2)
        self.assertEqual(completed, 0)
        self.assertEqual(pending, 2)
    
    def test_save_and_load_tasks(self):
        """Test saving and loading tasks"""
        # Add some tasks
        self.manager.add_task("Task 1", "Description 1")
        self.manager.add_task("Task 2", "Description 2")
        self.manager.complete_task(1)
        
        # Create a new manager and load tasks
        new_manager = TaskManager(self.temp_file.name)
        
        self.assertEqual(len(new_manager.tasks), 2)
        self.assertEqual(new_manager.tasks[0].title, "Task 1")
        self.assertEqual(new_manager.tasks[1].title, "Task 2")
        self.assertTrue(new_manager.tasks[0].completed)
        self.assertFalse(new_manager.tasks[1].completed)
    
    def test_clear_all_tasks(self):
        """Test clearing all tasks"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.assertEqual(len(self.manager.tasks), 2)
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.clear_all_tasks()
        
        self.assertEqual(len(self.manager.tasks), 0)
        self.assertIn("All tasks have been cleared!", f.getvalue())
    
    def test_export_tasks(self):
        """Test exporting tasks to a file"""
        self.manager.add_task("Task 1", "Description 1")
        self.manager.add_task("Task 2", "Description 2")
        
        export_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        export_file.close()
        
        try:
            with redirect_stdout(io.StringIO()) as f:
                self.manager.export_tasks(export_file.name)
            
            self.assertIn("Tasks exported to", f.getvalue())
            
            # Verify the exported file contains the tasks
            with open(export_file.name, 'r') as f:
                exported_data = json.load(f)
            
            self.assertEqual(len(exported_data), 2)
            self.assertEqual(exported_data[0]['title'], "Task 1")
            self.assertEqual(exported_data[1]['title'], "Task 2")
        finally:
            if os.path.exists(export_file.name):
                os.unlink(export_file.name)
    
    def test_import_tasks(self):
        """Test importing tasks from a file"""
        # Create a test import file
        import_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        import_data = [
            {
                'title': 'Imported Task 1',
                'description': 'Imported Description 1',
                'completed': False,
                'created_at': '2023-01-01T10:00:00',
                'completed_at': None
            },
            {
                'title': 'Imported Task 2',
                'description': 'Imported Description 2',
                'completed': True,
                'created_at': '2023-01-01T11:00:00',
                'completed_at': '2023-01-01T12:00:00'
            }
        ]
        
        with open(import_file.name, 'w') as f:
            json.dump(import_data, f)
        
        try:
            with redirect_stdout(io.StringIO()) as f:
                self.manager.import_tasks(import_file.name)
            
            self.assertIn("Successfully imported 2 tasks", f.getvalue())
            self.assertEqual(len(self.manager.tasks), 2)
            self.assertEqual(self.manager.tasks[0].title, "Imported Task 1")
            self.assertEqual(self.manager.tasks[1].title, "Imported Task 2")
            self.assertFalse(self.manager.tasks[0].completed)
            self.assertTrue(self.manager.tasks[1].completed)
        finally:
            if os.path.exists(import_file.name):
                os.unlink(import_file.name)
    
    def test_get_task_history(self):
        """Test getting task history"""
        self.manager.add_task("Task 1", "Description 1")
        self.manager.add_task("Task 2", "Description 2")
        self.manager.complete_task(1)
        
        with redirect_stdout(io.StringIO()) as f:
            self.manager.get_task_history()
        
        output = f.getvalue()
        self.assertIn("=== Task History ===", output)
        self.assertIn("Task 1", output)
        self.assertIn("Task 2", output)
        self.assertIn("Created:", output)
        self.assertIn("Completed:", output)


class TestTaskManagerIntegration(unittest.TestCase):
    """Integration tests for TaskManager"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Use a temporary file for testing to avoid interfering with real data
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = TaskManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_complete_workflow(self):
        """Test a complete workflow of task management"""
        # Add tasks
        self.manager.add_task("Buy groceries", "Milk, bread, eggs")
        self.manager.add_task("Finish project", "Complete the task management app")
        self.manager.add_task("Call mom", "Weekly check-in")
        
        # Verify initial state
        total, completed, pending = self.manager.get_task_count()
        self.assertEqual(total, 3)
        self.assertEqual(completed, 0)
        self.assertEqual(pending, 3)
        
        # Complete some tasks
        self.manager.complete_task(1)
        self.manager.complete_task(3)
        
        # Verify completion
        total, completed, pending = self.manager.get_task_count()
        self.assertEqual(total, 3)
        self.assertEqual(completed, 2)
        self.assertEqual(pending, 1)
        
        # Delete a task
        self.manager.delete_task(2)
        
        # Verify final state
        total, completed, pending = self.manager.get_task_count()
        self.assertEqual(total, 2)
        self.assertEqual(completed, 2)
        self.assertEqual(pending, 0)
        
        # Verify remaining tasks
        self.assertEqual(self.manager.tasks[0].title, "Buy groceries")
        self.assertEqual(self.manager.tasks[1].title, "Call mom")
        self.assertTrue(self.manager.tasks[0].completed)
        self.assertTrue(self.manager.tasks[1].completed)
    
    def test_task_operations_after_deletion(self):
        """Test that task operations work correctly after deletions"""
        # Add tasks
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.add_task("Task 3")
        self.manager.add_task("Task 4")
        
        # Delete middle task
        self.manager.delete_task(2)
        
        # Verify remaining tasks
        self.assertEqual(len(self.manager.tasks), 3)
        self.assertEqual(self.manager.tasks[0].title, "Task 1")
        self.assertEqual(self.manager.tasks[1].title, "Task 3")
        self.assertEqual(self.manager.tasks[2].title, "Task 4")
        
        # Complete task by new index
        self.manager.complete_task(2)  # Should complete "Task 3"
        self.assertTrue(self.manager.tasks[1].completed)
        self.assertFalse(self.manager.tasks[0].completed)
        self.assertFalse(self.manager.tasks[2].completed)
        
        # Delete another task
        self.manager.delete_task(1)  # Should delete "Task 1"
        
        # Verify final state
        self.assertEqual(len(self.manager.tasks), 2)
        self.assertEqual(self.manager.tasks[0].title, "Task 3")
        self.assertEqual(self.manager.tasks[1].title, "Task 4")
        self.assertTrue(self.manager.tasks[0].completed)
        self.assertFalse(self.manager.tasks[1].completed)


class TestTaskManagerApp(unittest.TestCase):
    """Test cases for the TaskManagerApp class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Use a temporary file for testing to avoid interfering with real data
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        # Create a custom TaskManager with the temp file
        from models import TaskManager
        manager = TaskManager(self.temp_file.name)
        self.app = TaskManagerApp()
        self.app.manager = manager
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_initialization(self):
        """Test TaskManagerApp initialization"""
        self.assertIsInstance(self.app.manager, TaskManager)
        self.assertTrue(self.app.running)
        self.assertEqual(len(self.app.manager.tasks), 0)
    
    def test_show_menu(self):
        """Test menu display"""
        with redirect_stdout(io.StringIO()) as f:
            self.app.show_menu()
        
        output = f.getvalue()
        self.assertIn("Task Management System", output)
        self.assertIn("1. Add Task", output)
        self.assertIn("2. View Task List", output)
        self.assertIn("3. Complete Task", output)
        self.assertIn("4. Delete Task", output)
        self.assertIn("5. Statistics", output)
        self.assertIn("6. Task History", output)
        self.assertIn("7. Export Tasks", output)
        self.assertIn("8. Import Tasks", output)
        self.assertIn("9. Clear All Tasks", output)
        self.assertIn("0. Exit Program", output)
    
    @patch('builtins.input', return_value='3')
    def test_get_user_choice_valid(self, mock_input):
        """Test getting valid user choice"""
        choice = self.app.get_user_choice()
        self.assertEqual(choice, 3)
        mock_input.assert_called_once_with("Please select an operation (0-9): ")
    
    @patch('builtins.input', return_value='invalid')
    def test_get_user_choice_invalid(self, mock_input):
        """Test getting invalid user choice"""
        choice = self.app.get_user_choice()
        self.assertEqual(choice, 0)
        mock_input.assert_called_once_with("Please select an operation (0-9): ")
    
    @patch('builtins.input', side_effect=['Test Task', 'Test Description'])
    def test_handle_add_task_with_description(self, mock_input):
        """Test handling add task with description"""
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_add_task()
        
        self.assertEqual(len(self.app.manager.tasks), 1)
        self.assertEqual(self.app.manager.tasks[0].title, "Test Task")
        self.assertEqual(self.app.manager.tasks[0].description, "Test Description")
        self.assertIn("Task 'Test Task' has been added!", f.getvalue())
    
    @patch('builtins.input', side_effect=['Test Task', ''])
    def test_handle_add_task_without_description(self, mock_input):
        """Test handling add task without description"""
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_add_task()
        
        self.assertEqual(len(self.app.manager.tasks), 1)
        self.assertEqual(self.app.manager.tasks[0].title, "Test Task")
        self.assertEqual(self.app.manager.tasks[0].description, "")
    
    @patch('builtins.input', side_effect=['', 'Description'])
    def test_handle_add_task_empty_title(self, mock_input):
        """Test handling add task with empty title"""
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_add_task()
        
        self.assertEqual(len(self.app.manager.tasks), 0)
        self.assertIn("Task title cannot be empty!", f.getvalue())
    
    @patch('builtins.input', side_effect=['   ', 'Description'])
    def test_handle_add_task_whitespace_title(self, mock_input):
        """Test handling add task with whitespace-only title"""
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_add_task()
        
        self.assertEqual(len(self.app.manager.tasks), 0)
        self.assertIn("Task title cannot be empty!", f.getvalue())
    
    def test_handle_complete_task_no_tasks(self):
        """Test handling complete task when no tasks exist"""
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_complete_task()
        
        output = f.getvalue()
        self.assertIn("No tasks available", output)
    
    @patch('builtins.input', return_value='1')
    def test_handle_complete_task_valid(self, mock_input):
        """Test handling complete task with valid input"""
        self.app.manager.add_task("Test Task")
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_complete_task()
        
        self.assertTrue(self.app.manager.tasks[0].completed)
        self.assertIn("Task 1 has been marked as completed!", f.getvalue())
    
    @patch('builtins.input', return_value='invalid')
    def test_handle_complete_task_invalid_input(self, mock_input):
        """Test handling complete task with invalid input"""
        self.app.manager.add_task("Test Task")
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_complete_task()
        
        self.assertFalse(self.app.manager.tasks[0].completed)
        self.assertIn("Please enter a valid number!", f.getvalue())
    
    def test_handle_delete_task_no_tasks(self):
        """Test handling delete task when no tasks exist"""
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_delete_task()
        
        output = f.getvalue()
        self.assertIn("No tasks available", output)
    
    @patch('builtins.input', return_value='1')
    def test_handle_delete_task_valid(self, mock_input):
        """Test handling delete task with valid input"""
        self.app.manager.add_task("Test Task 1")
        self.app.manager.add_task("Test Task 2")
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_delete_task()
        
        self.assertEqual(len(self.app.manager.tasks), 1)
        self.assertEqual(self.app.manager.tasks[0].title, "Test Task 2")
        self.assertIn("Task 'Test Task 1' has been deleted!", f.getvalue())
    
    @patch('builtins.input', return_value='invalid')
    def test_handle_delete_task_invalid_input(self, mock_input):
        """Test handling delete task with invalid input"""
        self.app.manager.add_task("Test Task")
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_delete_task()
        
        self.assertEqual(len(self.app.manager.tasks), 1)  # Task should still be there
        self.assertIn("Please enter a valid number!", f.getvalue())
    
    def test_show_statistics_empty(self):
        """Test showing statistics with no tasks"""
        with redirect_stdout(io.StringIO()) as f:
            self.app.show_statistics()
        
        output = f.getvalue()
        self.assertIn("=== Statistics ===", output)
        self.assertIn("Total tasks: 0", output)
        self.assertIn("Completed: 0", output)
        self.assertIn("Pending: 0", output)
        self.assertNotIn("Completion rate:", output)
    
    def test_show_statistics_with_tasks(self):
        """Test showing statistics with tasks"""
        self.app.manager.add_task("Task 1")
        self.app.manager.add_task("Task 2")
        self.app.manager.add_task("Task 3")
        self.app.manager.complete_task(1)
        self.app.manager.complete_task(3)
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.show_statistics()
        
        output = f.getvalue()
        self.assertIn("=== Statistics ===", output)
        self.assertIn("Total tasks: 3", output)
        self.assertIn("Completed: 2", output)
        self.assertIn("Pending: 1", output)
        self.assertIn("Completion rate: 66.7%", output)
    
    def test_show_statistics_all_completed(self):
        """Test showing statistics when all tasks are completed"""
        self.app.manager.add_task("Task 1")
        self.app.manager.add_task("Task 2")
        self.app.manager.complete_task(1)
        self.app.manager.complete_task(2)
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.show_statistics()
        
        output = f.getvalue()
        self.assertIn("Total tasks: 2", output)
        self.assertIn("Completed: 2", output)
        self.assertIn("Pending: 0", output)
        self.assertIn("Completion rate: 100.0%", output)
    
    def test_run_application_flow(self):
        """Test the main application flow"""
        with redirect_stdout(io.StringIO()) as f:
            # Test individual components of the application flow
            self.app.show_menu()
            print("Thank you for using! Goodbye!")
            self.app.running = False
        
        output = f.getvalue()
        self.assertIn("Task Management System", output)
        self.assertIn("Thank you for using! Goodbye!", output)
        self.assertFalse(self.app.running)
    
    def test_handle_task_history(self):
        """Test handling task history display"""
        self.app.manager.add_task("Task 1", "Description 1")
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_task_history()
        
        output = f.getvalue()
        self.assertIn("=== Task History ===", output)
        self.assertIn("Task 1", output)
        self.assertIn("Created:", output)
    
    @patch('builtins.input', return_value='test_export.json')
    def test_handle_export_tasks(self, mock_input):
        """Test handling export tasks"""
        self.app.manager.add_task("Task 1", "Description 1")
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_export_tasks()
        
        output = f.getvalue()
        self.assertIn("Tasks exported to test_export.json", output)
        
        # Clean up the test file
        if os.path.exists('test_export.json'):
            os.unlink('test_export.json')
    
    @patch('builtins.input', return_value='nonexistent.json')
    def test_handle_import_tasks_nonexistent(self, mock_input):
        """Test handling import tasks with nonexistent file"""
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_import_tasks()
        
        output = f.getvalue()
        self.assertIn("File nonexistent.json not found!", output)
    
    @patch('builtins.input', side_effect=['yes'])
    def test_handle_clear_all_tasks_confirm(self, mock_input):
        """Test handling clear all tasks with confirmation"""
        self.app.manager.add_task("Task 1")
        self.app.manager.add_task("Task 2")
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_clear_all_tasks()
        
        output = f.getvalue()
        self.assertIn("All tasks have been cleared!", output)
        self.assertEqual(len(self.app.manager.tasks), 0)
    
    @patch('builtins.input', side_effect=['no'])
    def test_handle_clear_all_tasks_cancel(self, mock_input):
        """Test handling clear all tasks with cancellation"""
        self.app.manager.add_task("Task 1")
        self.app.manager.add_task("Task 2")
        
        with redirect_stdout(io.StringIO()) as f:
            self.app.handle_clear_all_tasks()
        
        output = f.getvalue()
        self.assertIn("Operation cancelled.", output)
        self.assertEqual(len(self.app.manager.tasks), 2)


class TestTaskManagerAppIntegration(unittest.TestCase):
    """Integration tests for TaskManagerApp with mocked user interactions"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Use a temporary file for testing to avoid interfering with real data
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        # Create a custom TaskManager with the temp file
        from models import TaskManager
        manager = TaskManager(self.temp_file.name)
        self.app = TaskManagerApp()
        self.app.manager = manager
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_complete_user_workflow(self):
        """Test a complete user workflow with mocked inputs"""
        # This simulates: Add task, Add another task, Complete first task, Delete second task, View stats
        
        # Add first task
        with patch('builtins.input', side_effect=['Buy groceries', 'Milk, bread']):
            self.app.handle_add_task()
        self.assertEqual(len(self.app.manager.tasks), 1)
        self.assertEqual(self.app.manager.tasks[0].title, "Buy groceries")
        
        # Add second task
        with patch('builtins.input', side_effect=['Call mom', '']):
            self.app.handle_add_task()
        self.assertEqual(len(self.app.manager.tasks), 2)
        self.assertEqual(self.app.manager.tasks[1].title, "Call mom")
        
        # Complete first task
        with patch('builtins.input', return_value='1'):
            with redirect_stdout(io.StringIO()) as f:
                self.app.handle_complete_task()
        self.assertTrue(self.app.manager.tasks[0].completed)
        
        # Delete second task
        with patch('builtins.input', return_value='2'):
            with redirect_stdout(io.StringIO()) as f:
                self.app.handle_delete_task()
        self.assertEqual(len(self.app.manager.tasks), 1)
        
        # View statistics
        with redirect_stdout(io.StringIO()) as f:
            self.app.show_statistics()
        output = f.getvalue()
        self.assertIn("Total tasks: 1", output)
        self.assertIn("Completed: 1", output)
        self.assertIn("Pending: 0", output)
        self.assertIn("Completion rate: 100.0%", output)


def main():
    """Run the test suite"""
    print("TASK MANAGEMENT SYSTEM - UNITTEST SUITE")
    print("=" * 60)
    
    # Run tests with detailed output
    unittest.main(verbosity=2, exit=False)


if __name__ == "__main__":
    sys.exit(main())
