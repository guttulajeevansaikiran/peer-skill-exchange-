# ⚔️ Skill Exchange – Shadow System

A Python Full Stack Web Application that connects people who want to share their knowledge, teach skills, and learn new skills through mutual skill exchange.

## 📌 About the Project

Skill Exchange is a web-based platform designed to help users discover people with complementary skills and connect with them for collaborative learning.

Users can create accounts, build their profiles, add skills they can teach, select skills they want to learn, discover other members, send connection requests, identify mutual skill matches, and communicate with connected users through chat.

The application features a cinematic dark interface inspired by anime-style gaming systems, with a focus on user experience and responsive design.

## ✨ Features

- 🔐 User Registration and Login
- 👤 User Profiles and Profile Settings
- 🛠️ Add, Manage, and Remove Skills
- 🔍 Search Members by Skills
- 🤝 Send, Accept, Reject, and Withdraw Connection Requests
- 🔄 Smart Mutual Skill Matching
- 💬 Chat with Connected Members
- 🔔 Notifications
- ⭐ User Reviews and Ratings
- 🎯 Skill Recommendations
- 📱 Responsive User Interface
- 🌑 Dark Shadow-System Theme

## 🧰 Technologies Used

**Frontend**
- HTML5
- CSS3
- JavaScript
- Responsive Web Design

**Backend**
- Python
- Flask

**Database**
- MySQL
- MySQL Connector for Python

**Development Tools**
- Visual Studio Code
- XAMPP
- phpMyAdmin
- Git and GitHub

## 🏗️ Project Structure

```text
skill_exchange/
│
├── app.py
├── database.py
├── requirements.txt
│
├── database/
│   └── skill_exchange.sql
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── entry-bg.png
│
└── templates/
    ├── index.html
    ├── register.html
    ├── login.html
    ├── dashboard.html
    ├── profile.html
    ├── profile_settings.html
    ├── skills.html
    ├── users.html
    ├── connections.html
    ├── requests.html
    ├── chats.html
    ├── chat.html
    ├── matches.html
    ├── notifications.html
    ├── recommendations.html
    ├── member_profile.html
    ├── forgot_password.html
    └── reset_password.html
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/guttulajeevansaikiran/skill-exchange.git
```

### 2. Navigate to the Project Folder

```bash
cd skill-exchange
```

### 3. Install Dependencies

Make sure Python and pip are installed.

```bash
py -m pip install -r requirements.txt
```

### 4. Set Up MySQL

1. Install and open XAMPP.
2. Start Apache and MySQL.
3. Open phpMyAdmin at `http://localhost/phpmyadmin`.
4. Create the `skill_exchange` database if it does not exist.
5. Import `database/skill_exchange.sql`.

### 5. Configure the Database

Check `database.py` and configure the MySQL connection settings for your local environment.

Do not publish database passwords, secret keys, or other sensitive credentials on GitHub.

### 6. Run the Application

```bash
py app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## 🔄 How It Works

1. Register an account and log in.
2. Complete your profile.
3. Add the skills you can teach.
4. Select the skills you want to learn.
5. Search for members with relevant skills.
6. Send connection requests to potential learning partners.
7. Accept connection requests and identify mutual skill matches.
8. Chat with connected members and exchange knowledge.

## 🎯 Project Objective

The main objective of Skill Exchange is to create a collaborative learning environment where users can share their expertise, discover learning partners, and develop new skills through peer-to-peer knowledge exchange.

## 🚀 Future Enhancements

- AI-powered skill recommendations
- Real-time messaging
- Video-based learning sessions
- Skill verification and achievement badges
- Advanced user matching
- Deployment to a cloud hosting platform

## 👨‍💻 Developer

**Jeevan Sai Kiran**

- GitHub: [@guttulajeevansaikiran](https://github.com/guttulajeevansaikiran)
- Email: jeevanguttula45@gmail.com

## 📄 License

This project is developed for educational and portfolio purposes.
