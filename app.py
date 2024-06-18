import os
import logging
from logging.handlers import TimedRotatingFileHandler
from models import init_db, create_superuser, User, BlogPost, Comment
from sanic import Sanic
from sanic.response import html, redirect, json
from sanic.exceptions import NotFound
from sanic_ext import Extend
from sanic_session import Session, InMemorySessionInterface
from jinja2 import Environment, FileSystemLoader, select_autoescape
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from base64 import urlsafe_b64encode
from dotenv import load_dotenv
import aiofiles
from datetime import datetime
# Завантаження змінних оточення
load_dotenv()

# Налаштування логування
logger = logging.getLogger('sanic_app')
logger.setLevel(logging.DEBUG)

# Створюємо обробник для логування в файл з ротацією
file_handler = TimedRotatingFileHandler('app.log', when='midnight', interval=1, backupCount=1)
file_handler.setLevel(logging.DEBUG)

# Створюємо обробник для логування в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Налаштування формату логів
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Додаємо обробники до логгера
logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = Sanic("BlogApp")
Extend(app)

session = Session(app, interface=InMemorySessionInterface())

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

def static_url(filename):
    return f"/static/{filename}"

# Кастомний фільтр для форматування дати
def format_datetime(value, format='%d/%m/%Y'):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime(format)

env.filters['format_datetime'] = format_datetime
env.filters['static_url'] = static_url

# Додаємо маршрут для обробки запитів на статичні файли
app.static('/static', './static')

async def save_file(file, upload_dir='static/uploads'):
    # Переконайтеся, що файл має ім'я
    if not file.name:
        raise ValueError("The uploaded file does not have a name")
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, file.name)
    
    # Переконайтеся, що file_path не є директорією
    if os.path.isdir(file_path):
        raise IsADirectoryError(f"Path {file_path} is a directory")
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file.body)
    
    return f'/static/uploads/{file.name}'

def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_message(sender, to, subject, message_text):
    message = EmailMessage()
    message.set_content(message_text)
    message["To"] = to
    message["From"] = sender
    message["Subject"] = subject
    raw_message = urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        logger.info(f"Message Id: {message['id']}")
        return message
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return None


@app.before_server_start
async def setup_db(app, loop):
    await init_db()
    await create_superuser()


@app.route("/", methods=["GET", "POST"])
async def index(request):
    if request.method == "POST":
        form = request.form
        name = form.get('name')
        email = form.get('email')
        subject = form.get('subject')
        message = form.get('message')

        # Валідація електронної пошти
        try:
            v = validate_email(email)
            email = v["email"]
        except EmailNotValidError as e:
            return json({"error": str(e)}, status=400)

        # Отримання OAuth2 токену
        credentials = get_credentials()

        # Створення сервісу Gmail API
        service = build('gmail', 'v1', credentials=credentials)

        # Створення повідомлення
        email_message = create_message(os.getenv('EMAIL_USER'), os.getenv('RECIPIENT_EMAIL'), subject, f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")

        # Відправка повідомлення
        send_message(service, 'me', email_message)

        logger.info(f"Email sent from {email} with subject '{subject}'")

        return redirect("/")
    latest_posts = await BlogPost.get_latest_posts(2)
    template = env.get_template('index.html')
    return html(template.render(latest_posts=latest_posts))

@app.route("/login", methods=["GET", "POST"])
async def login(request):
    if request.method == "POST":
        form = request.form
        username = form.get('username')
        password = form.get('password')
        if await User.authenticate(username, password):
            response = redirect("/dashboard")
            request.ctx.session['user'] = username
            logger.info(f"User {username} logged in")
            return response
        else:
            logger.warning("Invalid login attempt")
            return json({"error": "Invalid credentials"}, status=401)
    template = env.get_template('login.html')
    return html(template.render())

@app.route("/create_post", methods=["GET", "POST"])
async def create_post(request):
    if 'user' not in request.ctx.session:
        return redirect("/login")
    
    if request.method == "POST":
        form = request.form
        title = form.get('title')
        text = form.get('text')
        tags = form.get('tags')

        # Обробка завантаження зображення
        if 'main_image' in request.files and request.files.get('main_image').name:
            main_image_file = request.files.get('main_image')
            main_image_url = await save_file(main_image_file)
        else:
            main_image_url = None

        # Створення нового блог-посту
        await BlogPost.create(title, main_image_url, text, tags)

        return redirect("/dashboard")

    template = env.get_template('create_post.html')
    return html(template.render())

@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
async def edit_post(request, post_id):
    if 'user' not in request.ctx.session:
        return redirect("/login")
    
    post = await BlogPost.get_by_id(post_id)
    if post is None:
        return redirect("/dashboard")
    
    if request.method == "POST":
        form = request.form
        title = form.get('title')
        text = form.get('text')
        tags = form.get('tags')

        # Обробка завантаження зображення
        if 'main_image' in request.files and request.files.get('main_image').name:
            main_image_file = request.files.get('main_image')
            main_image_url = await save_file(main_image_file)
        else:
            logger.info(post[2])
            main_image_url = post[2]  # Якщо зображення не завантажене, залишити старе

        # Оновлення блог-посту
        await BlogPost.update(post_id, title, main_image_url, text, tags)

        return redirect("/dashboard")

    template = env.get_template('edit_post.html')
    return html(template.render(post=post))

@app.route("/delete_post/<post_id>", methods=["POST"])
async def delete_post(request, post_id):
    if 'user' not in request.ctx.session:
        return redirect("/login")
    
    await BlogPost.delete(post_id)
    return redirect("/dashboard")


@app.route("/dashboard")
async def dashboard(request):
    if 'user' not in request.ctx.session:
        return redirect("/login")
    
    posts = await BlogPost.get_all()
    template = env.get_template('dashboard.html')
    return html(template.render(posts=posts))


@app.route("/posts")
async def posts(request):
    tag = request.args.get('tag')
    page = int(request.args.get('page', 1))
    posts_per_page = 2

    if tag:
        posts = await BlogPost.get_by_tag(tag)
    else:
        posts = await BlogPost.get_all()

    total_posts = len(posts)
    total_pages = (total_posts + posts_per_page - 1) // posts_per_page

    start = (page - 1) * posts_per_page
    end = start + posts_per_page
    paginated_posts = posts[start:end]

    # Отримуємо кількість коментарів для кожного поста
    posts_with_comments = []
    for post in paginated_posts:
        post_id = post[0]
        post_with_comments = list(post)  # Перетворюємо кортеж на список
        post_with_comments.append(await Comment.get_comment_count_by_post_id(post_id))
        posts_with_comments.append(post_with_comments)

    needpagination = total_posts > posts_per_page
    template = env.get_template('posts.html')
    return html(
        template.render(
            posts=posts_with_comments,
            selected_tag=tag,
            total_pages=total_pages,
            current_page=page,
            pagination=needpagination
        )
    )



@app.route("/post/<post_id>", methods=["GET", "POST"])
async def post_detail(request, post_id):
    post = await BlogPost.get_by_id(post_id)
    if not post:
        return redirect("/posts")
    if request.method == "POST":
        form = request.form
        name = form.get('name')
        message = form.get('message')
        parent_id = form.get('parent_id')
        await Comment.create(post_id, name, message, parent_id)
        return redirect(f"/post/{post_id}")

    comments = await Comment.get_by_post_id(post_id)
    prev_post, next_post = await BlogPost.get_navigation_posts(post_id)

    template = env.get_template('post_detail.html')
    return html(template.render(post=post, comments=comments, prev_post=prev_post, next_post=next_post))


@app.route("/admin/comments")
async def admin_comments(request):
    if 'user' not in request.ctx.session:
        return redirect("/login")
    
    comments = await Comment.get_all()
    template = env.get_template('admin_comments.html')
    return html(template.render(comments=comments))

@app.route("/admin/comments/delete/<comment_id>", methods=["POST"])
async def delete_comment(request, comment_id):
    if 'user' not in request.ctx.session:
        return redirect("/login")
    
    await Comment.delete(comment_id)
    return redirect("/admin/comments")


# Обробник помилок 404
@app.exception(NotFound)
async def handle_404(request, exception):
    logger.error(f"404 Not Found: {request.url}")
    template = env.get_template('404.html')
    return html(template.render(), status=404)

# Загальний обробник помилок
# @app.exception(Exception)
# async def handle_exceptions(request, exception):
#     logger.error(f"Exception: {exception}")
#     template = env.get_template('error.html')
#     return html(template.render(), status=500)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)


