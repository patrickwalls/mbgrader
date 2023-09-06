from config import Config
from flask import Flask

import app
from .commands import init_db

def run_server():
    """Helper function to automatically create a database and start a development server."""

    db_path = Config.BASE_DIR / "app.db"
    if db_path.exists():
        print("Database found - reset by calling init-mbgrader-db")
    else:
        print("Database not found - creating...")
        init_db(standalone_mode=False)

    app.run()
