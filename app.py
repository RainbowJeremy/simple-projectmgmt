from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import json
import os
import qrcode
import io
import base64
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL')
logger.info(f"DATABASE_URL environment variable: {'SET' if DATABASE_URL else 'NOT SET'}")

if DATABASE_URL:
    logger.info(f"Using PostgreSQL database: {DATABASE_URL[:30]}...")
    # PostgreSQL connection
    def get_db_connection():
        try:
            conn = psycopg2.connect(DATABASE_URL)
            logger.info("✅ PostgreSQL connection successful")
            return conn
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {str(e)}")
            raise
else:
    logger.info("Using SQLite database (local development)")
    # Fallback to SQLite for local development
    DATABASE = 'project_management.db'
    def get_db_connection():
        try:
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
            logger.info("✅ SQLite connection successful")
            return conn
        except Exception as e:
            logger.error(f"❌ SQLite connection failed: {str(e)}")
            raise

def init_db():
    logger.info("🔧 Starting database initialization...")
    
    try:
        conn = get_db_connection()
        logger.info("📊 Database connection established for initialization")
        
        if DATABASE_URL:
            logger.info("🐘 Setting up PostgreSQL tables...")
            # PostgreSQL setup
            cur = conn.cursor()
            
            # KPI Table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS kpis (
                    id SERIAL PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    target_value REAL,
                    date DATE NOT NULL DEFAULT CURRENT_DATE,
                    category TEXT DEFAULT 'general'
                )
            ''')
            logger.info("✅ KPIs table created/verified")
            
            # Tasks Table for Kanban Board
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
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
            logger.info("✅ Tasks table created/verified")
            
            # Product Backlog Table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS backlog_items (
                    id SERIAL PRIMARY KEY,
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
            logger.info("✅ Backlog items table created/verified")
            
            conn.commit()
            cur.close()
            logger.info("🎉 PostgreSQL database initialization completed successfully!")
        else:
            logger.info("📁 Setting up SQLite tables...")
            # SQLite setup
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
            logger.info("🎉 SQLite database initialization completed successfully!")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"💥 Database initialization failed: {str(e)}")
        raise

def convert_priority_to_int(priority):
    """Convert text priority values to integers"""
    if isinstance(priority, int):
        return priority
    
    if isinstance(priority, str):
        priority_lower = priority.lower()
        if priority_lower == 'low':
            return 1
        elif priority_lower == 'medium':
            return 2
        elif priority_lower == 'high':
            return 3
        elif priority_lower == 'critical':
            return 4
        else:
            # Try to convert to int if it's a number string
            try:
                return int(priority)
            except (ValueError, TypeError):
                return 2  # Default to medium priority
    
    return 2  # Default fallback

# Template Routes
@app.route('/home')
@app.route('/')
def home():
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM tasks')
        tasks = cur.fetchall()
        cur.execute('SELECT * FROM backlog_items')
        backlog = cur.fetchall()
        cur.close()
    else:
        # SQLite
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
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM tasks ORDER BY created_date DESC')
        tasks = cur.fetchall()
        cur.close()
    else:
        # SQLite
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
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM kpis ORDER BY date DESC')
        kpis = cur.fetchall()
        cur.close()
    else:
        # SQLite
        kpis = conn.execute('SELECT * FROM kpis ORDER BY date DESC').fetchall()
    
    conn.close()
    
    return render_template('kpi.html', active_page='kpi', kpis=[dict(kpi) for kpi in kpis])

@app.route('/backlog')
def product_backlog():
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM backlog_items ORDER BY priority DESC, created_date DESC')
        items = cur.fetchall()
        cur.close()
    else:
        # SQLite
        items = conn.execute('SELECT * FROM backlog_items ORDER BY priority DESC, created_date DESC').fetchall()
    
    conn.close()
    
    return render_template('productbacklog_backend.html', active_page='backlog', backlog_items=[dict(item) for item in items])

@app.route('/qr')
def qr_code():
    return render_template('qr.html', active_page='qr')

# Database Test Route (for debugging)
@app.route('/api/db-test')
def test_database():
    """Test endpoint to verify database connection and tables"""
    test_results = {
        'database_type': 'PostgreSQL' if DATABASE_URL else 'SQLite',
        'database_url_set': bool(DATABASE_URL),
        'connection_test': None,
        'tables_exist': {},
        'table_counts': {},
        'errors': []
    }
    
    try:
        # Test connection
        conn = get_db_connection()
        test_results['connection_test'] = '✅ SUCCESS'
        logger.info("🔍 Database test: Connection successful")
        
        if DATABASE_URL:
            # PostgreSQL tests
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Check if tables exist
            for table in ['kpis', 'tasks', 'backlog_items']:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table,))
                exists = cur.fetchone()[0]
                test_results['tables_exist'][table] = '✅ EXISTS' if exists else '❌ MISSING'
                
                if exists:
                    cur.execute(f'SELECT COUNT(*) as count FROM {table}')
                    count = cur.fetchone()['count']
                    test_results['table_counts'][table] = count
            
            cur.close()
        else:
            # SQLite tests
            cursor = conn.cursor()
            
            # Check if tables exist
            for table in ['kpis', 'tasks', 'backlog_items']:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?;
                """, (table,))
                exists = cursor.fetchone() is not None
                test_results['tables_exist'][table] = '✅ EXISTS' if exists else '❌ MISSING'
                
                if exists:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    count = cursor.fetchone()[0]
                    test_results['table_counts'][table] = count
        
        conn.close()
        logger.info(f"🔍 Database test completed: {test_results}")
        
    except Exception as e:
        error_msg = f"Database test failed: {str(e)}"
        test_results['errors'].append(error_msg)
        test_results['connection_test'] = '❌ FAILED'
        logger.error(f"🔍 {error_msg}")
    
    return jsonify(test_results)

# Static file serving
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# KPI Routes
@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM kpis ORDER BY date DESC')
        kpis = cur.fetchall()
        cur.close()
    else:
        # SQLite
        kpis = conn.execute('SELECT * FROM kpis ORDER BY date DESC').fetchall()
    
    conn.close()
    
    return jsonify([dict(kpi) for kpi in kpis])

@app.route('/api/kpis', methods=['POST'])
def add_kpi():
    data = request.get_json()
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO kpis (metric_name, value, target_value, category) VALUES (%s, %s, %s, %s)',
            (data['metric_name'], data['value'], data.get('target_value'), data.get('category', 'general'))
        )
        conn.commit()
        cur.close()
    else:
        # SQLite
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
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM tasks ORDER BY created_date DESC')
        tasks = cur.fetchall()
        cur.close()
    else:
        # SQLite
        tasks = conn.execute('SELECT * FROM tasks ORDER BY created_date DESC').fetchall()
    
    conn.close()
    
    return jsonify([dict(task) for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO tasks (title, description, status, priority, assignee, story_points, 
               detailed, estimable, emergent, prioritized) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (data['title'], data.get('description', ''), data.get('status', 'todo'),
             data.get('priority', 'medium'), data.get('assignee', ''), 
             data.get('story_points', 0), data.get('detailed', 'No'),
             data.get('estimable', 'No'), data.get('emergent', 'No'), 
             data.get('prioritized', 'No'))
        )
        conn.commit()
        cur.close()
    else:
        # SQLite
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
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor()
        cur.execute(
            '''UPDATE tasks SET title=%s, description=%s, status=%s, priority=%s, 
               assignee=%s, story_points=%s, detailed=%s, estimable=%s, emergent=%s, 
               prioritized=%s, updated_date=CURRENT_DATE WHERE id=%s''',
            (data['title'], data.get('description', ''), data['status'],
             data.get('priority', 'medium'), data.get('assignee', ''),
             data.get('story_points', 0), data.get('detailed', 'No'),
             data.get('estimable', 'No'), data.get('emergent', 'No'),
             data.get('prioritized', 'No'), task_id)
        )
        conn.commit()
        cur.close()
    else:
        # SQLite
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
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor()
        cur.execute('DELETE FROM tasks WHERE id=%s', (task_id,))
        conn.commit()
        cur.close()
    else:
        # SQLite
        conn.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        conn.commit()
    
    conn.close()
    
    return jsonify({'success': True, 'message': 'Task deleted successfully'})

# Backlog Routes
@app.route('/api/backlog', methods=['GET'])
def get_backlog():
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM backlog_items ORDER BY priority DESC, created_date DESC')
        items = cur.fetchall()
        cur.close()
    else:
        # SQLite
        items = conn.execute('SELECT * FROM backlog_items ORDER BY priority DESC, created_date DESC').fetchall()
    
    conn.close()
    
    return jsonify([dict(item) for item in items])

@app.route('/api/backlog', methods=['POST'])
def add_backlog_item():
    data = request.get_json()
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO backlog_items (title, description, priority, story_points, status, epic) VALUES (%s, %s, %s, %s, %s, %s)',
            (data['title'], data.get('description', ''), convert_priority_to_int(data.get('priority')),
             data.get('story_points', 0), data.get('status', 'new'), data.get('epic', ''))
        )
        conn.commit()
        cur.close()
    else:
        # SQLite
        conn.execute(
            'INSERT INTO backlog_items (title, description, priority, story_points, status, epic) VALUES (?, ?, ?, ?, ?, ?)',
            (data['title'], data.get('description', ''), convert_priority_to_int(data.get('priority')),
             data.get('story_points', 0), data.get('status', 'new'), data.get('epic', ''))
        )
        conn.commit()
    
    conn.close()
    
    return jsonify({'success': True, 'message': 'Backlog item added successfully'})

@app.route('/api/backlog/<int:item_id>', methods=['PUT'])
def update_backlog_item(item_id):
    data = request.get_json()
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor()
        cur.execute(
            '''UPDATE backlog_items SET title=%s, description=%s, priority=%s, 
               story_points=%s, status=%s, epic=%s, updated_date=CURRENT_DATE WHERE id=%s''',
            (data['title'], data.get('description', ''), convert_priority_to_int(data.get('priority')),
             data.get('story_points', 0), data.get('status', 'new'), 
             data.get('epic', ''), item_id)
        )
        conn.commit()
        cur.close()
    else:
        # SQLite
        conn.execute(
            '''UPDATE backlog_items SET title=?, description=?, priority=?, 
               story_points=?, status=?, epic=?, updated_date=CURRENT_DATE WHERE id=?''',
            (data['title'], data.get('description', ''), convert_priority_to_int(data.get('priority')),
             data.get('story_points', 0), data.get('status', 'new'), 
             data.get('epic', ''), item_id)
        )
        conn.commit()
    
    conn.close()
    
    return jsonify({'success': True, 'message': 'Backlog item updated successfully'})

@app.route('/api/backlog/<int:item_id>', methods=['DELETE'])
def delete_backlog_item(item_id):
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cur = conn.cursor()
        cur.execute('DELETE FROM backlog_items WHERE id=%s', (item_id,))
        conn.commit()
        cur.close()
    else:
        # SQLite
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
else:
    # Initialize database when running in production (e.g., with gunicorn)
    init_db() 