from flask import Flask
from labtracker.config import Config
from labtracker.models import db, init_db
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
with app.app_context():
    db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///','')
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db(app)
    print('✅ database initialized')

