#!/usr/bin/env python3
"""
Startup script for the Project Management Dashboard backend.
This script initializes the database and starts the Flask server.
"""

import os
import sys
from app import app, init_db

def main():
    print("🚀 Starting Project Management Dashboard Backend")
    print("=" * 50)
    
    # Initialize database
    print("📊 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Check if database file exists
    if os.path.exists('project_management.db'):
        print(f"📁 Database file: project_management.db")
    
    print("\n🌐 Starting Flask server...")
    print("📍 Frontend: http://localhost:8000")
    print("🔌 API Base: http://localhost:8000/api")
    print("\n📋 Available endpoints:")
    print("   • GET  /api/kpis")
    print("   • POST /api/kpis")
    print("   • GET  /api/tasks")
    print("   • POST /api/tasks")
    print("   • PUT  /api/tasks/<id>")
    print("   • DELETE /api/tasks/<id>")
    print("   • GET  /api/backlog")
    print("   • POST /api/backlog")
    print("   • PUT  /api/backlog/<id>")
    print("   • DELETE /api/backlog/<id>")
    print("   • POST /api/qr")
    
    print("\n💡 Tips:")
    print("   • Press Ctrl+C to stop the server")
    print("   • Run 'python test_api.py' in another terminal to test the API")
    print("   • Check README_BACKEND.md for detailed documentation")
    
    print("\n" + "=" * 50)
    
    # Start the Flask app
    try:
        app.run(debug=True, host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 