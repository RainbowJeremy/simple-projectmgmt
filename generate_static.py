#!/usr/bin/env python3
from app import app
import os

def generate_static_files():
    """Generate static HTML files from Flask templates"""
    
    # Initialize the database first
    from app import init_db
    init_db()
    
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
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.get_data(as_text=True))
                        print(f'✓ Generated {filename}')
                    else:
                        print(f'✗ Error: {route} returned status {response.status_code}')
                except Exception as e:
                    print(f'✗ Error generating {route}: {e}')

if __name__ == '__main__':
    generate_static_files() 