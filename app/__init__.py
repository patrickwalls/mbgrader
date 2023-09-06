from pathlib import Path
from flask import Flask
from flask.cli import with_appcontext
import click
from config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
run = app.run

from app import routes

from app.commands import init_db

app.cli.add_command(init_db)
