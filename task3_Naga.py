'''
The task manager
*** Naga Likhith Arlagadda ***
'''
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
                    description TEXT,-
                    due_date TEXT,
                    priority TEXT,
                    project TEXT
                )
            ''')
 
    def task_exists(self, task_id):
        cursor = self.conn.execute('SELECT task_id FROM tasks WHERE task_id = ?', (task_id,))
        return cursor.fetchone() is not None
 
    def add_task(self, task):
        if self.task_exists(task.task_id):
            self.update_task_description(task.task_id, task.description)
        else:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO tasks (task_id, title, description, due_date, priority, project)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    task.task_id,
                    task.title,
                    task.description,
                    task.due_date,
                    getattr(task, 'priority', None),
                    getattr(task, 'project', None)
                ))
 
    def add_tasks(self, tasks):
        for task in tasks:
            self.add_task(task)
 
    def update_task_description(self, task_id, new_description):
        with self.conn:
            self.conn.execute('''
                UPDATE tasks
                SET description=?
                WHERE task_id=?
            ''', (new_description, task_id))
 
    def delete_task(self, task_id):
        with self.conn:
            self.conn.execute('DELETE FROM tasks WHERE task_id=?', (task_id,))
 
    def display_tasks_sorted_by_due_date(self):
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM tasks ORDER BY due_date')
            for row in cursor.fetchall():
                print(f'Task ID: {row[0]}, Title: {row[1]}, Due Date: {row[3]}')
 
    def save_to_json(self):
        with open(self.json_file, 'w') as file:
            tasks = self.getalltasks()
            tasks_to_save = [task.__dict__ for task in tasks]
            json.dump(tasks_to_save, file, indent=4)
 
    def load_from_json(self):
        try:
            with open(self.json_file, 'r') as file:
                data = json.load(file)
                tasks = []
                for task_data in data:
                    if 'priority' in task_data:
                        task = PersonalTask(**task_data)
                    elif 'project' in task_data:
                        task = WorkTask(**task_data)
                    else:
                        task = Task(**task_data)
                    tasks.append(task)
                self.add_tasks(tasks)
        except FileNotFoundError:
            pass
 
    def getalltasks(self):
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM tasks ORDER BY due_date')
            tasks = []
            for row in cursor.fetchall():
                task_id, title, description, due_date, priority, project = row
                if priority:
                    tasks.append(PersonalTask(task_id, title, description, due_date, priority))
                elif project:
                    tasks.append(WorkTask(task_id, title, description, due_date, project))
                else:
                    tasks.append(Task(task_id, title, description, due_date))
            return tasks
 
    def __enter__(self):
        return self
 
    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()
 
# Example usage:
with TaskManagementSystem('tasks.db', 'tasks.json') as task_system:
    personal_task = PersonalTask(1, 'Meditate', 'Breakfast', '2023-11-16', 'High')
    work_task = WorkTask(2, 'Cloud class', 'Assignment submission', '2023-12-5', 'Low')
 
    tasks_to_add = [personal_task, work_task]
    task_system.add_tasks(tasks_to_add)
 
    task_system.display_tasks_sorted_by_due_date()
 
    task_system.save_to_json()
    task_system.load_from_json()