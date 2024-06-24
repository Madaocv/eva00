# Eva00 Tech

## Project Description
Eva00 Tech is a landing page for a charitable organization foundation. This website serves as a digital business card for the organization, showcasing its mission, activities, and ways to contribute.

### Features
- **Multilingual Support**
The website supports two languages, and the language is determined through middleware. The process works as follows:

When a user visits the website, the middleware checks for a language preference cookie.
If the cookie is present, the website will display the content in the preferred language.
If the cookie is not present, the middleware will check the browser's language settings.
Based on the browser's language setting, the website will display the content in the corresponding language.
Users can also manually switch the language, which will update the language preference cookie for future visits.
- **Email Notification**
The website allows users to send messages to a specific email address. When a user fills out the contact form, the message is sent directly to the organization's email address. This ensures that all inquiries and communications are promptly received and addressed.

- **CRUD Operations**
The website includes CRUD (Create, Read, Update, Delete) operations for admin users. Admins can manage the content of the website, including blog posts and other entries. For regular users, the website provides detailed views of the content, allowing them to read and engage with the material.


## Build and Run Commands

### Manual Setup using Virtualenv

1. **Clone the repository**:
```sh
git clone https://github.com/Madaocv/eva00.git
cd eva00
```

2. **Create and activate a virtual environment**:
```sh
virtualenv -p python3 venv
source venv/bin/activate
```

3. **Install the required packages**:
```sh
pip install -r requirements.txt
```

4. **Set up environment variables and configuration files as needed.**

5. **Run the application**:
```sh
python app.py
```

### Setup using Docker

1. **Clone the repository**:
```sh
git clone https://github.com/Madaocv/eva00.git
cd eva00
```

2. Build and run the Docker containers:
```sh
docker-compose up --build
```
The application should now be running and accessible at http://localhost:8000.

## Screenshot Examples

### Home Page

![Home Page](static/img/homepage.png)
*Home Page*

### Detail View

![Detail View](static/img/detailview.png)
*Detail View*

This README provides a comprehensive overview of the Eva00 Tech website, its features, and setup instructions. The screenshots at the end visually demonstrate the user interface and functionality of the website.






