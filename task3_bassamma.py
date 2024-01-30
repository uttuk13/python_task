import sqlite3
import json

class Task:
    def __init__(self, task_id, title, description, due_date):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.due_date = due_date

class PersonalTask(Task):
    def __init__(self, task_id, title, description, due_date, priority):
        super().__init__(task_id, title, description, due_date)
        self.priority = priority

class WorkTask(Task):
    def __init__(self, task_id, title, description, due_date, project):
        super().__init__(task_id, title, description, due_date)
        self.project = project

class TaskManagementSystem:
    def __init__(self, db_file, json_file):
        self.conn = sqlite3.connect(db_file)
        self.create_task_table()
        self.json_file = json_file

    def create_task_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT,
                    project TEXT
                )
            ''')

    def add_task(self, task):
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM tasks WHERE task_id = ?', (task.task_id,))
            existing_task = cursor.fetchone()
            
            if existing_task:
                print("Task with the same ID already exists.")
            else:
                if isinstance(task, PersonalTask):
                    self.conn.execute('''INSERT INTO tasks (task_id, title, description, due_date, priority)
                    VALUES (?, ?, ?, ?, ?)''',(task.task_id, task.title, task.description, task.due_date, task.priority))
                elif isinstance(task, WorkTask):
                    self.conn.execute('''
                        INSERT INTO tasks (task_id, title, description, due_date, project)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (task.task_id, task.title, task.description, task.due_date, task.project))
            print("Task added successfully.")

    def update_task(self, task_id, new_description):
        with self.conn:
            self.conn.execute('''
                UPDATE tasks
                SET description = ?
                WHERE task_id = ?
            ''', (new_description, task_id))

    def delete_task(self, task_id):
        with self.conn:
            self.conn.execute('''
                DELETE FROM tasks
                WHERE task_id = ?
            ''', (task_id,))

    def display_tasks_sorted_by_due_date(self):
        with self.conn:
            cursor = self.conn.execute('''
                SELECT * FROM tasks
                ORDER BY due_date
            ''')

        for row in cursor:
            task_id, title, description, due_date, priority, project = row
            print("Task ID:", task_id)
            print("Title:", title)
            print("Description:", description)
            print("Due Date:", due_date)
            print("Priority:", priority)
            print("Project:", project)
            print("----")

    def save_to_json(self):
        tasks = []

        with self.conn:
            cursor = self.conn.execute('''
                SELECT * FROM tasks
            ''')

        for row in cursor:
            task_id, title, description, due_date, priority, project = row
            task = {
                'task_id': task_id,
                'title': title,
                'description': description,
                'due_date': due_date,
                'priority': priority,
                'project': project
            }
            tasks.append(task)

        with open(self.json_file, 'w') as file:
            json.dump(tasks, file, indent=4)

        print("Tasks saved to JSON file.")

    def load_from_json(self):
        with open(self.json_file, 'r') as file:
            tasks = json.load(file)

        for task in tasks:
            if 'priority' in task:
                new_task = PersonalTask(
                    task['task_id'],
                    task['title'],
                    task['description'],
                    task['due_date'],
                    task['priority']
                )
            elif 'project' in task:
                new_task = WorkTask(
                    task['task_id'],
                    task['title'],
                    task['description'],
                    task['due_date'],
                    task['project']
                )

            self.add_task(new_task)

        print("Tasks loaded from JSON file.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

# Example usage:
with TaskManagementSystem('task_database.db', 'tasks.json') as task_system:
    personal_task = PersonalTask(1, 'Exercise', 'Go for a run', '2024-01-15', 'High')
    work_task = WorkTask(2, 'Project Meeting', 'Discuss project plans', '2024-01-20', 'Project X')
    work_task = WorkTask(3, 'Meeting', 'project plans', '2024-01-25', 'Project y')

    task_system.add_task(personal_task)
    task_system.add_task(work_task)

    task_system.display_tasks_sorted_by_due_date()

    task_system.save_to_json()
    task_system.load_from_json()