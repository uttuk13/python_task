import sqlite3
import json
 
class Task:
    def __init__(self, task_id, title, description, due_date):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.due_date = due_date
 
class PersonalTask(Task):
    def __init__(self, task_id, title, description, due_date, priority, project):
        super().__init__(task_id, title, description, due_date)
        self.priority = priority
        self.project = project
 
class WorkTask(Task):
    def __init__(self, task_id, title, description, due_date,priority, project):
        super().__init__(task_id, title, description, due_date)
        self.priority = priority
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
        #add task to database
        with self.conn:
            self.conn.execute('''
                INSERT INTO tasks (task_id, title, description, due_date, priority, project)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (task.task_id, task.title, task.description, task.due_date, task.priority, task.project))
 
 
    def update_task(self, task_id, new_description):
        # update task description in the database
        with self.conn:
            self.conn.execute('''
                UPDATE tasks
                SET description = ?
                WHERE task_id = ?
            ''', (new_description, task_id))
 
 
    def delete_task(self, task_id):
        # delete a task from the database using lambda function
        with self.conn:
            self.conn.execute('''
                DELETE FROM tasks
                WHERE task_id = ?
            ''', (task_id,))
 
    def display_tasks_sorted_by_due_date(self):
        # display tasks sorted by due date
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM tasks ORDER BY due_date')
            tasks = cursor.fetchall()
            for task in tasks:
                print(task)
 
    def save_to_json(self):
        # save tasks to a JSON file
        with open(self.json_file, 'w') as file:
            tasks = []
            for row in self.conn.execute('SELECT * FROM tasks'):
                tasks.append({
                    'task_id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'due_date': row[3],
                    'priority': row[4],
                    'project': row[5]
                })
            json.dump(tasks, file)
 
    def load_from_json(self):
        # load tasks from a JSON file using try catch
        try:
            with open(self.json_file, 'r') as file:
                tasks = json.load(file)
                return tasks
        except FileNotFoundError:
            print("File not found.")
        except json.JSONDecodeError:
            print("Invalid JSON format.")
        except Exception as e:
            print("An error occurred:", str(e))
               
    def __enter__(self):
        return self
 
    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()
 
 
# Example usage:
with TaskManagementSystem('task_database.db', 'tasks.json') as task_system:
    personal_task = PersonalTask(1, 'Exercise', 'Go for a run', '2022-12-15', 'High', 'Workout')
    work_task = WorkTask(2, 'Project Meeting', 'Discuss project plans', '2022-12-10', 'Project X', 'Work')
 
    task_system.add_task(personal_task)
    task_system.add_task(work_task)
    task_system.display_tasks_sorted_by_due_date()
   
    task_system.update_task(1, 'Go for a walk')
    task_system.display_tasks_sorted_by_due_date()
 
    task_system.save_to_json()
    print(task_system.load_from_json())
 