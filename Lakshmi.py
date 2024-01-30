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
            if isinstance(task, PersonalTask):
                self.conn.execute('''
                    INSERT INTO tasks (task_id, title, description, due_date, priority)
                    VALUES (?, ?, ?, ?, ?)
                ''', (task.task_id, task.title, task.description, task.due_date, task.priority))
            elif isinstance(task, WorkTask):
                self.conn.execute('''
                    INSERT INTO tasks (task_id, title, description, due_date, project)
                    VALUES (?, ?, ?, ?, ?)
                ''', (task.task_id, task.title, task.description, task.due_date, task.project))

    def update_task(self, task_id, new_description):
        with self.conn:
            self.conn.execute('''
                UPDATE tasks SET description = ?
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
                print(row)
                
    def save_to_json(self):
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM tasks')
            tasks = []
            for row in cursor:
                task_data = {
                    'task_id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'due_date': row[3],
                    'priority': row[4] if row[4] else None,
                    'project': row[5] if row[5] else None
                }
                tasks.append(task_data)
                
        with open(self.json_file, 'w') as file:
            json.dump(tasks, file, indent=4)
            
    def load_from_json(self):
        with open(self.json_file, 'r') as file:
            tasks = json.load(file)
            
            with self.conn:
                self.conn.execute('DELETE FROM tasks')
                for task_data in tasks:
                    if 'priority' in task_data:
                        task = PersonalTask(
                            task_data['task_id'],
                            task_data['title'],
                            task_data['description'],
                            task_data['due_date'],
                            task_data['priority']
                        )
                    elif 'project' in task_data:
                        task = WorkTask(
                            task_data['task_id'],
                            task_data['title'],
                            task_data['description'],
                            task_data['due_date'],
                            task_data['project']
                        )
                    self.add_task(task)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

# Example:

with TaskManagementSystem('task_database.db', 'tasks.json') as task_system:
    personal_task = PersonalTask(1, 'Exercise', 'Go for a run', '2024-1-30', 'High')
    work_task = WorkTask(2, 'Project Meeting', 'Discuss project plans', '2022-2-1', 'Project X')
    task_system.add_task(personal_task)
    task_system.add_task(work_task)
    task_system.display_tasks_sorted_by_due_date()
    task_system.save_to_json()
    task_system.load_from_json()