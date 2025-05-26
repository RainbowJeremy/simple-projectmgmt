from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json
import os
import qrcode
import io
import base64

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'project_management.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # KPI Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS kpis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            target_value REAL,
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            category TEXT DEFAULT 'general'
        )
    ''')
    
    # Tasks Table for Kanban Board
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo',
            priority TEXT DEFAULT 'medium',
            assignee TEXT,
            created_date DATE DEFAULT CURRENT_DATE,
            updated_date DATE DEFAULT CURRENT_DATE,
            story_points INTEGER DEFAULT 0,
            detailed TEXT DEFAULT 'No',
            estimable TEXT DEFAULT 'No',
            emergent TEXT DEFAULT 'No',
            prioritized TEXT DEFAULT 'No'
        )
    ''')
    
    # Product Backlog Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS backlog_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER DEFAULT 0,
            story_points INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',
            epic TEXT,
            created_date DATE DEFAULT CURRENT_DATE,
            updated_date DATE DEFAULT CURRENT_DATE
        )
    ''')
    
    # Sample data
    try:
        # Sample KPIs
        conn.execute('INSERT OR IGNORE INTO kpis (metric_name, value, target_value, category) VALUES (?, ?, ?, ?)',
                    ('Revenue', 45000, 50000, 'financial'))
        conn.execute('INSERT OR IGNORE INTO kpis (metric_name, value, target_value, category) VALUES (?, ?, ?, ?)',
                    ('Customer Satisfaction', 4.2, 4.5, 'customer'))
        conn.execute('INSERT OR IGNORE INTO kpis (metric_name, value, target_value, category) VALUES (?, ?, ?, ?)',
                    ('Conversion Rate', 2.8, 3.5, 'marketing'))
        
        # Sample Tasks
        conn.execute('INSERT OR IGNORE INTO tasks (title, description, status, priority) VALUES (?, ?, ?, ?)',
                    ('Setup Authentication', 'Implement user login system', 'todo', 'high'))
        conn.execute('INSERT OR IGNORE INTO tasks (title, description, status, priority) VALUES (?, ?, ?, ?)',
                    ('Database Design', 'Design database schema', 'doing', 'high'))
        conn.execute('INSERT OR IGNORE INTO tasks (title, description, status, priority) VALUES (?, ?, ?, ?)',
                    ('Unit Tests', 'Write unit tests for core functions', 'done', 'medium'))
        
        # Sample Backlog Items
        conn.execute('INSERT OR IGNORE INTO backlog_items (title, description, priority, story_points, epic) VALUES (?, ?, ?, ?, ?)',
                    ('User Registration', 'Allow users to create accounts', 1, 5, 'Authentication'))
        conn.execute('INSERT OR IGNORE INTO backlog_items (title, description, priority, story_points, epic) VALUES (?, ?, ?, ?, ?)',
                    ('Dashboard Analytics', 'Real-time analytics dashboard', 2, 8, 'Analytics'))
        
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    
    conn.close()

# Template Routes
@app.route('/home')
@app.route('/')
def home():
    conn = get_db_connection()
    
    # Get statistics for dashboard
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    backlog = conn.execute('SELECT * FROM backlog_items').fetchall()
    
    total_tasks = len(tasks)
    active_sprint_tasks = len([task for task in tasks if task['status'] in ['todo', 'doing']])
    completed_tasks = len([task for task in tasks if task['status'] == 'done'])
    backlog_items = len(backlog)
    
    conn.close()
    
    return render_template('index.html', 
                         active_page='home',
                         total_tasks=total_tasks,
                         active_sprint_tasks=active_sprint_tasks,
                         completed_tasks=completed_tasks,
                         backlog_items=backlog_items)

@app.route('/sprint')
def sprint_board():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks ORDER BY created_date DESC').fetchall()
    conn.close()
    
    # Group tasks by status
    todo_tasks = [dict(task) for task in tasks if task['status'] == 'todo']
    doing_tasks = [dict(task) for task in tasks if task['status'] == 'doing']
    done_tasks = [dict(task) for task in tasks if task['status'] == 'done']
    
    return render_template('mykanban_backend.html', 
                         active_page='sprint',
                         tasks=[dict(task) for task in tasks],
                         todo_tasks=todo_tasks,
                         doing_tasks=doing_tasks,
                         done_tasks=done_tasks)

@app.route('/sprint/micheal')
def micheal_sprint():
    return render_template('micheal_sprint.html', active_page='sprint')

@app.route('/sprint/fintan')
def fintan_sprint():
    return render_template('fintan_sprint.html', active_page='sprint')

@app.route('/sprint/jack')
def jack_sprint():
    return render_template('jack_sprint.html', active_page='sprint')

@app.route('/kpi')
def kpi_dashboard():
    conn = get_db_connection()
    kpis = conn.execute('SELECT * FROM kpis ORDER BY date DESC').fetchall()
    conn.close()
    
    return render_template('kpi.html', active_page='kpi', kpis=[dict(kpi) for kpi in kpis])

@app.route('/backlog')
def product_backlog():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM backlog_items ORDER BY priority DESC, created_date DESC').fetchall()
    conn.close()
    
    return render_template('productbacklog_backend.html', active_page='backlog', backlog_items=[dict(item) for item in items])

@app.route('/qr')
def qr_code():
    return render_template('qr.html', active_page='qr')

# Static file serving
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# KPI Routes
@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    conn = get_db_connection()
    kpis = conn.execute('SELECT * FROM kpis ORDER BY date DESC').fetchall()
    conn.close()
    
    return jsonify([dict(kpi) for kpi in kpis])

@app.route('/api/kpis', methods=['POST'])
def add_kpi():
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute(
        'INSERT INTO kpis (metric_name, value, target_value, category) VALUES (?, ?, ?, ?)',
        (data['metric_name'], data['value'], data.get('target_value'), data.get('category', 'general'))
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'KPI added successfully'})

# Task Routes (Kanban)
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks ORDER BY created_date DESC').fetchall()
    conn.close()
    
    return jsonify([dict(task) for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute(
        '''INSERT INTO tasks (title, description, status, priority, assignee, story_points, 
           detailed, estimable, emergent, prioritized) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data['title'], data.get('description', ''), data.get('status', 'todo'),
         data.get('priority', 'medium'), data.get('assignee', ''), 
         data.get('story_points', 0), data.get('detailed', 'No'),
         data.get('estimable', 'No'), data.get('emergent', 'No'), 
         data.get('prioritized', 'No'))
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Task added successfully'})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute(
        '''UPDATE tasks SET title=?, description=?, status=?, priority=?, 
           assignee=?, story_points=?, detailed=?, estimable=?, emergent=?, 
           prioritized=?, updated_date=CURRENT_DATE WHERE id=?''',
        (data['title'], data.get('description', ''), data['status'],
         data.get('priority', 'medium'), data.get('assignee', ''),
         data.get('story_points', 0), data.get('detailed', 'No'),
         data.get('estimable', 'No'), data.get('emergent', 'No'),
         data.get('prioritized', 'No'), task_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Task updated successfully'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Task deleted successfully'})

# Backlog Routes
@app.route('/api/backlog', methods=['GET'])
def get_backlog():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM backlog_items ORDER BY priority DESC, created_date DESC').fetchall()
    conn.close()
    
    return jsonify([dict(item) for item in items])

@app.route('/api/backlog', methods=['POST'])
def add_backlog_item():
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute(
        'INSERT INTO backlog_items (title, description, priority, story_points, status, epic) VALUES (?, ?, ?, ?, ?, ?)',
        (data['title'], data.get('description', ''), data.get('priority', 0),
         data.get('story_points', 0), data.get('status', 'new'), data.get('epic', ''))
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Backlog item added successfully'})

@app.route('/api/backlog/<int:item_id>', methods=['PUT'])
def update_backlog_item(item_id):
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute(
        '''UPDATE backlog_items SET title=?, description=?, priority=?, 
           story_points=?, status=?, epic=?, updated_date=CURRENT_DATE WHERE id=?''',
        (data['title'], data.get('description', ''), data.get('priority', 0),
         data.get('story_points', 0), data.get('status', 'new'), 
         data.get('epic', ''), item_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Backlog item updated successfully'})

@app.route('/api/backlog/<int:item_id>', methods=['DELETE'])
def delete_backlog_item(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM backlog_items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Backlog item deleted successfully'})

# QR Code Route
@app.route('/api/qr', methods=['POST'])
def generate_qr():
    data = request.get_json()
    text = data.get('text', 'Hello World')
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({'qr_code': f'data:image/png;base64,{img_str}'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000) 