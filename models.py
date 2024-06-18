import aiosqlite
from passlib.context import CryptContext
from config import DB_PATH
from datetime import datetime

# Ініціалізація контексту хешування
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS blogposts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                main_image TEXT,
                publication_date TEXT DEFAULT CURRENT_TIMESTAMP,
                text TEXT NOT NULL,
                tags TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                parent_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES blogposts (id),
                FOREIGN KEY (parent_id) REFERENCES comments (id)
            )
        ''')
        await db.commit()


async def create_superuser():
    username = '$pbkdf2-sha256$29000$xLj3Xgth7P1fa80ZI4Rwzg$fJDuGZOV/o.1BbzotIkfJUTQr.ioz/YUmr.XUjFn2SM'
    password = '$pbkdf2-sha256$29000$6V1Laa0Vwvjf.5/z/v./Nw$MEB2iDetbwoFuhrZn4OgZXI73WH9yJW14ivGdfgfKkM'
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
                         (username, password))
        await db.commit()


class User:
    @staticmethod
    async def authenticate(username, password):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT username, password FROM users") as cursor:
                async for row in cursor:
                    if pwd_context.verify(username, row[0]) and pwd_context.verify(password, row[1]):
                        return True
        return False


class BlogPost:
    def __init__(self, title, main_image, text, tags):
        self.title = title
        self.main_image = main_image
        self.publication_date = datetime.now().isoformat()
        self.text = text
        self.tags = tags

    @staticmethod
    async def create(title, main_image, text, tags):
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('''
                INSERT INTO blogposts (title, main_image, publication_date, text, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, main_image, datetime.now().isoformat(), text, tags))
            await db.commit()
            return cursor.lastrowid

    @staticmethod
    async def update(post_id, title, main_image, text, tags):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                UPDATE blogposts
                SET title = ?, main_image = ?, text = ?, tags = ?
                WHERE id = ?
            ''', (title, main_image, text, tags, post_id))
            await db.commit()

    @staticmethod
    async def delete(post_id):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('DELETE FROM blogposts WHERE id = ?', (post_id,))
            await db.commit()

    @staticmethod
    async def get_all():
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('SELECT * FROM blogposts ORDER BY publication_date DESC')
            posts = await cursor.fetchall()
            return posts

    @staticmethod
    async def get_by_id(post_id):
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('SELECT * FROM blogposts WHERE id = ?', (post_id,))
            post = await cursor.fetchone()
            return post

    @staticmethod
    async def get_by_tag(tag):
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('SELECT * FROM blogposts WHERE tags LIKE ?', ('%' + tag + '%',))
            posts = await cursor.fetchall()
            return posts

    @staticmethod
    async def get_navigation_posts(post_id):
        posts = await BlogPost.get_all()
        post_ids = [p[0] for p in posts]

        try:
            current_index = post_ids.index(int(post_id))
        except ValueError:
            return None, None

        next_post = posts[current_index - 1] if current_index > 0 else None
        prev_post = posts[current_index + 1] if current_index < len(posts) - 1 else None

        return prev_post, next_post
    
    @staticmethod
    async def get_latest_posts(limit=2):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT * FROM blogposts ORDER BY publication_date DESC LIMIT ?", (limit,)) as cursor:
                return await cursor.fetchall()


class Comment:
    @staticmethod
    async def create(post_id, name, message, parent_id=None):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT INTO comments (post_id, name, message, parent_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (post_id, name, message, parent_id, datetime.now().isoformat()))
            await db.commit()

    @staticmethod
    async def get_by_post_id(post_id):
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC', (post_id,))
            comments = await cursor.fetchall()
            return comments

    @staticmethod
    async def get_comment_count_by_post_id(post_id):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM comments WHERE post_id = ?", (post_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    @staticmethod
    async def delete(comment_id):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
            await db.commit()

    @staticmethod
    async def get_all():
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT * FROM comments ORDER BY created_at DESC") as cursor:
                return await cursor.fetchall()