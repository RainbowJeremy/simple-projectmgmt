#!/usr/bin/env python3
from app import app, get_db_connection
import os
import json

def generate_static_files():
    """Generate static HTML files from Flask templates"""
    
    # Initialize the database first
    from app import init_db
    init_db()
    
    # Export database data as JSON files
    export_data_as_json()
    
    # Create static HTML files from Flask templates
    with app.app_context():
        with app.test_client() as client:
            # Generate static versions of your pages
            routes = [
                ('/', 'index.html'),
                ('/sprint', 'sprint.html'),
                ('/kpi', 'kpi.html'),
                ('/backlog', 'backlog.html'),
                ('/qr', 'qr.html')
            ]
            
            for route, filename in routes:
                try:
                    print(f'Generating {filename} from {route}...')
                    response = client.get(route)
                    if response.status_code == 200:
                        # Get the HTML content
                        html_content = response.get_data(as_text=True)
                        
                        # Replace API_BASE_URL with relative path for static data
                        html_content = html_content.replace(
                            "const API_BASE_URL = 'http://localhost:8000/api';",
                            "const API_BASE_URL = './data';"
                        )
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        print(f'✓ Generated {filename}')
                    else:
                        print(f'✗ Error: {route} returned status {response.status_code}')
                except Exception as e:
                    print(f'✗ Error generating {route}: {e}')

def export_data_as_json():
    """Export database data as JSON files for static site"""
    
    # Create data directory
    if not os.path.exists('data'):
        os.makedirs('data')
    
    conn = get_db_connection()
    
    try:
        # Export tasks
        tasks = conn.execute('SELECT * FROM tasks ORDER BY created_date DESC').fetchall()
        tasks_data = [dict(task) for task in tasks]
        with open('data/tasks', 'w') as f:
            json.dump(tasks_data, f, indent=2, default=str)
        print('✓ Exported tasks data')
        
        # Export KPIs
        kpis = conn.execute('SELECT * FROM kpis ORDER BY date DESC').fetchall()
        kpis_data = [dict(kpi) for kpi in kpis]
        with open('data/kpis', 'w') as f:
            json.dump(kpis_data, f, indent=2, default=str)
        print('✓ Exported KPIs data')
        
        # Export backlog
        backlog = conn.execute('SELECT * FROM backlog_items ORDER BY priority DESC, created_date DESC').fetchall()
        backlog_data = [dict(item) for item in backlog]
        with open('data/backlog', 'w') as f:
            json.dump(backlog_data, f, indent=2, default=str)
        print('✓ Exported backlog data')
        
    except Exception as e:
        print(f'✗ Error exporting data: {e}')
    finally:
        conn.close()

if __name__ == '__main__':
    generate_static_files() 