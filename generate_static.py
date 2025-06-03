#!/usr/bin/env python3
from app import app, get_db_connection
import os
import json
import re

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
                        
                        # Disable modification operations for static site
                        html_content = make_read_only(html_content)
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        print(f'✓ Generated {filename}')
                    else:
                        print(f'✗ Error: {route} returned status {response.status_code}')
                except Exception as e:
                    print(f'✗ Error generating {route}: {e}')

def make_read_only(html_content):
    """Disable modification features and add read-only notices"""
    
    # Add read-only notification CSS and JavaScript
    read_only_script = """
    <script>
    // Static Site Read-Only Mode
    function showReadOnlyNotice(action) {
        alert(`This is a read-only static version of the site.\\n\\n` +
              `Cannot ${action} in static mode.\\n\\n` +
              `For full functionality, please run the Flask app locally or deploy to a platform that supports Python backends (like Render.com, Railway.app, or Heroku).`);
    }
    
    // Override modification functions
    window.updateTask = () => showReadOnlyNotice('update tasks');
    window.deleteTask = () => showReadOnlyNotice('delete tasks');
    window.handleDeleteTask = () => showReadOnlyNotice('delete tasks');
    window.addTask = () => showReadOnlyNotice('add tasks');
    window.addBacklogItem = () => showReadOnlyNotice('add backlog items');
    window.updateBacklogItem = () => showReadOnlyNotice('update backlog items');
    window.deleteBacklogItem = () => showReadOnlyNotice('delete backlog items');
    window.addKPI = () => showReadOnlyNotice('add KPIs');
    
    // Disable form submissions
    document.addEventListener('DOMContentLoaded', function() {
        // Add read-only banner
        const banner = document.createElement('div');
        banner.style.cssText = `
            background: #f39c12;
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        `;
        banner.innerHTML = '📖 READ-ONLY MODE: This is a static demo. No data can be modified.';
        document.body.insertBefore(banner, document.body.firstChild);
        
        // Adjust body padding to account for banner
        document.body.style.paddingTop = '50px';
        
        // Disable all forms
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                showReadOnlyNotice('submit forms');
            });
        });
        
        // Disable all buttons that modify data
        const modifyButtons = document.querySelectorAll(
            'button[onclick*="delete"], button[onclick*="add"], button[onclick*="update"], ' +
            'button[onclick*="edit"], .delete-btn, .add-btn, .edit-btn'
        );
        modifyButtons.forEach(button => {
            button.style.opacity = '0.5';
            button.style.cursor = 'not-allowed';
            button.onclick = (e) => {
                e.preventDefault();
                showReadOnlyNotice('modify data');
            };
        });
    });
    </script>
    """
    
    # Insert the script before closing body tag
    html_content = html_content.replace('</body>', read_only_script + '</body>')
    
    # Replace API calls that modify data with read-only notices
    modifications = [
        (r"method:\s*['\"]POST['\"]", "method: 'GET' /* READ-ONLY: POST disabled */"),
        (r"method:\s*['\"]PUT['\"]", "method: 'GET' /* READ-ONLY: PUT disabled */"),
        (r"method:\s*['\"]DELETE['\"]", "method: 'GET' /* READ-ONLY: DELETE disabled */"),
    ]
    
    for pattern, replacement in modifications:
        html_content = re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)
    
    return html_content

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