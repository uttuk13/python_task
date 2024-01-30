import sqlite3
import json
from datetime import datetime

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
        self.db_file = db_file
        self.json_file = json_file
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.create_task_table()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()

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
            self.conn.execute('''
                INSERT INTO tasks (task_id, title, description, due_date, priority, project)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (task.task_id, task.title, task.description, task.due_date, getattr(task, 'priority', None), getattr(task, 'project', None)))

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
            for row in cursor.fetchall():
                print(row)

    def save_to_json(self):
        tasks = []
        with self.conn:
            cursor = self.conn.execute('''
                SELECT * FROM tasks
            ''')
            for row in cursor.fetchall():
                tasks.append({
                    'task_id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'due_date': row[3],
                    'priority': row[4],
                    'project': row[5]
                })

        with open(self.json_file, 'w') as json_file:
            json.dump(tasks, json_file, indent=2)

    def load_from_json(self):
        with open(self.json_file, 'r') as json_file:
            tasks = json.load(json_file)

        with self.conn:
            self.conn.execute('DELETE FROM tasks')
            for task in tasks:
                self.add_task(Task(task['task_id'], task['title'], task['description'], task['due_date'], task.get('priority'), task.get('project')))


task_system = TaskManagementSystem('task_database.db', 'tasks.json')
with task_system:
    personal_task_1 = PersonalTask(1, 'Exercise', 'Go for a run', '2022-12-15', 'High')
    personal_task_2 = PersonalTask(2, 'Read Books', 'Read "Sapiens" by Yuval Noah Harari', '2022-12-20', 'Medium')
    personal_task_3 = PersonalTask(3, 'Grocery Shopping', 'Buy ingredients for dinner', '2022-12-18', 'Low')

    work_task_1 = WorkTask(1, 'Project Meeting', 'Discuss project plans with the team', '2022-12-10', 'Project X')
    work_task_2 = WorkTask(2, 'Review Code', 'Review pull requests on GitHub', '2022-12-08', 'Project Y')
    work_task_3 = WorkTask(3, 'Prepare Presentation', 'Create slides for client presentation', '2022-12-13', 'Project Z')

    task_system.add_task(personal_task_1)
    task_system.add_task(personal_task_2)
    task_system.add_task(personal_task_3)
    task_system.add_task(work_task_1)
    task_system.add_task(work_task_2)
    task_system.add_task(work_task_3)

    task_system.display_tasks_sorted_by_due_date()

    task_system.save_to_json()
    task_system.load_from_json()