import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'blog.db')
SECRET_KEY = 'your-secret-key'
REQUEST_MAX_SIZE = int(os.getenv('REQUEST_MAX_SIZE', 50 * 1024 * 1024))