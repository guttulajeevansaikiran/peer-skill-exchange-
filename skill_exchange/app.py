from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from functools import wraps
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)

app.secret_key = "skill_exchange_shadow_system_secret_key"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="skill_exchange"
    )


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


# =========================================================
# DATABASE STRUCTURE
# =========================================================

def ensure_database_structure():

    conn = get_db_connection()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # USER SKILLS - skill_type
    # -----------------------------------------------------

    cursor.execute(
        "SHOW COLUMNS FROM user_skills LIKE 'skill_type'"
    )

    if cursor.fetchone() is None:

        cursor.execute("""
            ALTER TABLE user_skills
            ADD COLUMN skill_type
            ENUM('teach','learn')
            DEFAULT 'teach'
        """)

    # -----------------------------------------------------
    # USERS - location
    # -----------------------------------------------------

    cursor.execute(
        "SHOW COLUMNS FROM users LIKE 'location'"
    )

    if cursor.fetchone() is None:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN location VARCHAR(255) NULL
        """)

    # -----------------------------------------------------
    # USERS - education
    # -----------------------------------------------------

    cursor.execute(
        "SHOW COLUMNS FROM users LIKE 'education'"
    )

    if cursor.fetchone() is None:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN education VARCHAR(255) NULL
        """)

    # -----------------------------------------------------
    # USERS - reset token
    # -----------------------------------------------------

    cursor.execute(
        "SHOW COLUMNS FROM users LIKE 'reset_token'"
    )

    if cursor.fetchone() is None:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN reset_token VARCHAR(255) NULL
        """)

    # -----------------------------------------------------
    # USERS - reset token expiry
    # -----------------------------------------------------

    cursor.execute(
        "SHOW COLUMNS FROM users LIKE 'reset_token_expiry'"
    )

    if cursor.fetchone() is None:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN reset_token_expiry DATETIME NULL
        """)

    # -----------------------------------------------------
    # CONNECTIONS - sender_id
    # -----------------------------------------------------

    cursor.execute(
        "SHOW COLUMNS FROM connections LIKE 'sender_id'"
    )

    if cursor.fetchone() is None:

        cursor.execute("""
            ALTER TABLE connections
            ADD COLUMN sender_id INT NULL
        """)

    # -----------------------------------------------------
    # CONNECTIONS - receiver_id
    # -----------------------------------------------------

    cursor.execute(
        "SHOW COLUMNS FROM connections LIKE 'receiver_id'"
    )

    if cursor.fetchone() is None:

        cursor.execute("""
            ALTER TABLE connections
            ADD COLUMN receiver_id INT NULL
        """)

    # -----------------------------------------------------
    # NOTIFICATIONS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications
        (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            message VARCHAR(500) NOT NULL,
            notification_type VARCHAR(100) DEFAULT 'general',
            is_read TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # REVIEWS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews
        (
            id INT AUTO_INCREMENT PRIMARY KEY,
            reviewer_id INT NOT NULL,
            reviewed_user_id INT NOT NULL,
            rating INT NOT NULL,
            review_text VARCHAR(1000),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # BADGES
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS badges
        (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            badge_name VARCHAR(255) NOT NULL,
            badge_description VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # MESSAGES
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages
        (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            message TEXT NOT NULL,
            is_read TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    cursor.close()
    conn.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name", ""
        ).strip()

        username = request.form.get(
            "username", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        if (
            not full_name
            or not username
            or not email
            or not password
        ):

            flash(
                "Please fill all fields.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT id
            FROM users
            WHERE username = %s
            OR email = %s
        """, (username, email))

        existing_user = cursor.fetchone()

        if existing_user:

            cursor.close()
            conn.close()

            flash(
                "Username or email already exists.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        cursor.execute("""
            INSERT INTO users
            (
                full_name,
                username,
                email,
                password
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
        """, (
            full_name,
            username,
            email,
            password
        ))

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login_value = request.form.get(
            "login", ""
        ).strip()

        # Supports old login form
        if not login_value:

            login_value = request.form.get(
                "email", ""
            ).strip()

        password = request.form.get(
            "password", ""
        )

        if not login_value or not password:

            flash(
                "Please enter username/email and password.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT *
            FROM users
            WHERE
            (
                LOWER(email) = LOWER(%s)
                OR
                LOWER(username) = LOWER(%s)
            )
            AND password = %s
            LIMIT 1
        """, (
            login_value,
            login_value,
            password
        ))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:

            session.clear()

            session["user_id"] = user["id"]

            session["username"] = user["username"]

            session["email"] = user["email"]

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid username/email or password.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    # User
    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = %s
    """, (user_id,))

    user = cursor.fetchone()

    # Pending requests
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM connections
        WHERE receiver_id = %s
        AND status = 'pending'
    """, (user_id,))

    pending_requests = cursor.fetchone()["total"]

    # Accepted connections
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM connections
        WHERE
        (
            sender_id = %s
            OR
            receiver_id = %s
        )
        AND status = 'accepted'
    """, (
        user_id,
        user_id
    ))

    connections_count = cursor.fetchone()["total"]

    # Teaching skills
    cursor.execute("""
        SELECT s.skill_name
        FROM user_skills us
        INNER JOIN skills s
        ON us.skill_id = s.id
        WHERE us.user_id = %s
        AND us.skill_type = 'teach'
        ORDER BY s.skill_name
    """, (user_id,))

    teaching_skills = cursor.fetchall()

    # Learning skills
    cursor.execute("""
        SELECT s.skill_name
        FROM user_skills us
        INNER JOIN skills s
        ON us.skill_id = s.id
        WHERE us.user_id = %s
        AND us.skill_type = 'learn'
        ORDER BY s.skill_name
    """, (user_id,))

    learning_skills = cursor.fetchall()

    # Notifications
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_id = %s
        AND is_read = 0
    """, (user_id,))

    unread_notifications = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        pending_requests=pending_requests,
        connections_count=connections_count,
        teaching_skills=teaching_skills,
        learning_skills=learning_skills,
        unread_notifications=unread_notifications
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
@login_required
def profile():

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = %s
    """, (user_id,))

    user = cursor.fetchone()

    cursor.execute("""
        SELECT
            s.skill_name,
            s.category,
            us.skill_type
        FROM user_skills us
        INNER JOIN skills s
        ON us.skill_id = s.id
        WHERE us.user_id = %s
        ORDER BY s.skill_name
    """, (user_id,))

    skills = cursor.fetchall()

    cursor.execute("""
        SELECT
            AVG(rating) AS average_rating,
            COUNT(*) AS total_reviews
        FROM reviews
        WHERE reviewed_user_id = %s
    """, (user_id,))

    review_data = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "profile.html",
        user=user,
        skills=skills,
        review_data=review_data
    )


# =========================================================
# PROFILE SETTINGS
# =========================================================

@app.route(
    "/profile/settings",
    methods=["GET", "POST"]
)
@login_required
def profile_settings():

    user_id = session["user_id"]

    if request.method == "POST":

        full_name = request.form.get(
            "full_name", ""
        ).strip()

        username = request.form.get(
            "username", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip()

        location = request.form.get(
            "location", ""
        ).strip()

        education = request.form.get(
            "education", ""
        ).strip()

        if (
            not full_name
            or not username
            or not email
        ):

            flash(
                "Name, username and email are required.",
                "error"
            )

            return redirect(
                url_for("profile_settings")
            )

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT id
            FROM users
            WHERE
            (
                username = %s
                OR
                email = %s
            )
            AND id != %s
        """, (
            username,
            email,
            user_id
        ))

        existing = cursor.fetchone()

        if existing:

            cursor.close()
            conn.close()

            flash(
                "Username or email already exists.",
                "error"
            )

            return redirect(
                url_for("profile_settings")
            )

        cursor.execute("""
            UPDATE users
            SET
                full_name = %s,
                username = %s,
                email = %s,
                location = %s,
                education = %s
            WHERE id = %s
        """, (
            full_name,
            username,
            email,
            location,
            education,
            user_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        session["username"] = username
        session["email"] = email

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("profile")
        )

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = %s
    """, (user_id,))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "profile_settings.html",
        user=user
    )


# =========================================================
# SKILLS
# =========================================================

@app.route("/skills")
@login_required
def skills():

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM skills
        ORDER BY category, skill_name
    """)

    all_skills = cursor.fetchall()

    cursor.execute("""
        SELECT
            s.id,
            s.skill_name,
            s.category,
            us.skill_type
        FROM user_skills us
        INNER JOIN skills s
        ON us.skill_id = s.id
        WHERE us.user_id = %s
        ORDER BY s.skill_name
    """, (user_id,))

    user_skills = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "skills.html",
        all_skills=all_skills,
        user_skills=user_skills
    )


# =========================================================
# ADD SKILL
# =========================================================

@app.route(
    "/skills/add",
    methods=["POST"]
)
@login_required
def add_skill():

    user_id = session["user_id"]

    skill_id = request.form.get(
        "skill_id"
    )

    skill_type = request.form.get(
        "skill_type",
        "teach"
    )

    if not skill_id:
        return redirect(
            url_for("skills")
        )

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM user_skills
        WHERE user_id = %s
        AND skill_id = %s
        AND skill_type = %s
    """, (
        user_id,
        skill_id,
        skill_type
    ))

    exists = cursor.fetchone()

    if not exists:

        cursor.execute("""
            INSERT INTO user_skills
            (
                user_id,
                skill_id,
                skill_type
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """, (
            user_id,
            skill_id,
            skill_type
        ))

        conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("skills")
    )


# =========================================================
# ADD CUSTOM SKILL
# =========================================================

@app.route(
    "/skills/add-custom",
    methods=["POST"]
)
@login_required
def add_custom_skill():

    user_id = session["user_id"]

    skill_name = request.form.get(
        "skill_name",
        ""
    ).strip()

    category = request.form.get(
        "category",
        "Other"
    ).strip()

    skill_type = request.form.get(
        "skill_type",
        "teach"
    )

    if not skill_name:

        return redirect(
            url_for("skills")
        )

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT id
        FROM skills
        WHERE LOWER(skill_name) = LOWER(%s)
    """, (skill_name,))

    skill = cursor.fetchone()

    if skill:

        skill_id = skill["id"]

    else:

        cursor.execute("""
            INSERT INTO skills
            (
                skill_name,
                category
            )
            VALUES
            (
                %s,
                %s
            )
        """, (
            skill_name,
            category
        ))

        conn.commit()

        skill_id = cursor.lastrowid

    cursor.execute("""
        SELECT id
        FROM user_skills
        WHERE user_id = %s
        AND skill_id = %s
        AND skill_type = %s
    """, (
        user_id,
        skill_id,
        skill_type
    ))

    exists = cursor.fetchone()

    if not exists:

        cursor.execute("""
            INSERT INTO user_skills
            (
                user_id,
                skill_id,
                skill_type
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """, (
            user_id,
            skill_id,
            skill_type
        ))

        conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("skills")
    )


# =========================================================
# REMOVE SKILL
# =========================================================

@app.route(
    "/skills/remove/<int:skill_id>/<skill_type>"
)
@login_required
def remove_skill(
    skill_id,
    skill_type
):

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM user_skills
        WHERE user_id = %s
        AND skill_id = %s
        AND skill_type = %s
    """, (
        user_id,
        skill_id,
        skill_type
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("skills")
    )


# =========================================================
# FIND PLAYERS
# FRIENDS / MEMBERS / SKILLS SEARCH
# =========================================================

@app.route("/users")
@login_required
def users():

    search = request.args.get(
        "search",
        ""
    ).strip()

    search_type = request.args.get(
        "type",
        "all"
    ).strip().lower()

    current_user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    users_data = []

    # =====================================================
    # FRIENDS SEARCH
    # =====================================================

    if search_type == "friends":

        query = """
            SELECT DISTINCT
                u.id,
                u.full_name,
                u.username,
                u.email
            FROM users u

            INNER JOIN connections c
            ON
            (
                (
                    c.sender_id = %s
                    AND c.receiver_id = u.id
                )
                OR
                (
                    c.receiver_id = %s
                    AND c.sender_id = u.id
                )
            )

            WHERE c.status = 'accepted'

            AND u.id != %s
        """

        params = [
            current_user_id,
            current_user_id,
            current_user_id
        ]

        if search:

            query += """
                AND
                (
                    LOWER(u.full_name)
                    LIKE LOWER(%s)

                    OR

                    LOWER(u.username)
                    LIKE LOWER(%s)

                    OR

                    LOWER(u.email)
                    LIKE LOWER(%s)
                )
            """

            keyword = "%" + search + "%"

            params.extend([
                keyword,
                keyword,
                keyword
            ])

        query += """
            ORDER BY u.full_name
        """

        cursor.execute(
            query,
            tuple(params)
        )

        users_data = cursor.fetchall()

    # =====================================================
    # MEMBERS / SKILLS / ALL
    # =====================================================

    else:

        query = """
            SELECT DISTINCT
                u.id,
                u.full_name,
                u.username,
                u.email

            FROM users u

            LEFT JOIN user_skills us
            ON u.id = us.user_id

            LEFT JOIN skills s
            ON us.skill_id = s.id

            WHERE u.id != %s
        """

        params = [
            current_user_id
        ]

        if search:

            keyword = "%" + search + "%"

            # ---------------------------------------------
            # MEMBERS
            # ---------------------------------------------

            if search_type == "members":

                query += """
                    AND
                    (
                        LOWER(u.full_name)
                        LIKE LOWER(%s)

                        OR

                        LOWER(u.username)
                        LIKE LOWER(%s)

                        OR

                        LOWER(u.email)
                        LIKE LOWER(%s)
                    )
                """

                params.extend([
                    keyword,
                    keyword,
                    keyword
                ])

            # ---------------------------------------------
            # SKILLS
            # ---------------------------------------------

            elif search_type == "skills":

                query += """
                    AND
                    LOWER(s.skill_name)
                    LIKE LOWER(%s)
                """

                params.append(
                    keyword
                )

            # ---------------------------------------------
            # ALL
            # ---------------------------------------------

            else:

                query += """
                    AND
                    (
                        LOWER(u.full_name)
                        LIKE LOWER(%s)

                        OR

                        LOWER(u.username)
                        LIKE LOWER(%s)

                        OR

                        LOWER(u.email)
                        LIKE LOWER(%s)

                        OR

                        LOWER(s.skill_name)
                        LIKE LOWER(%s)
                    )
                """

                params.extend([
                    keyword,
                    keyword,
                    keyword,
                    keyword
                ])

        query += """
            ORDER BY u.full_name
        """

        cursor.execute(
            query,
            tuple(params)
        )

        users_data = cursor.fetchall()

    # =====================================================
    # USER SKILLS + CONNECTION STATUS
    # =====================================================

    for user in users_data:

        user["teaching_skills"] = []

        user["learning_skills"] = []

        cursor.execute("""
            SELECT
                s.skill_name,
                us.skill_type

            FROM user_skills us

            INNER JOIN skills s
            ON us.skill_id = s.id

            WHERE us.user_id = %s

            ORDER BY s.skill_name
        """, (user["id"],))

        skill_rows = cursor.fetchall()

        for row in skill_rows:

            if row["skill_type"] == "teach":

                user[
                    "teaching_skills"
                ].append(
                    row["skill_name"]
                )

            elif row["skill_type"] == "learn":

                user[
                    "learning_skills"
                ].append(
                    row["skill_name"]
                )

        # Default
        user["connection_status"] = "none"

        # -------------------------------------------------
        # CONNECTION STATUS
        # -------------------------------------------------

        cursor.execute("""
            SELECT *
            FROM connections

            WHERE
            (
                sender_id = %s
                AND receiver_id = %s
            )

            OR

            (
                sender_id = %s
                AND receiver_id = %s
            )

            ORDER BY id DESC
            LIMIT 1
        """, (
            current_user_id,
            user["id"],
            user["id"],
            current_user_id
        ))

        connection = cursor.fetchone()

        if connection:

            status = connection.get(
                "status"
            )

            sender_id = connection.get(
                "sender_id"
            )

            receiver_id = connection.get(
                "receiver_id"
            )

            if status == "accepted":

                user[
                    "connection_status"
                ] = "connected"

            elif status == "pending":

                if sender_id == current_user_id:

                    user[
                        "connection_status"
                    ] = "sent"

                elif receiver_id == current_user_id:

                    user[
                        "connection_status"
                    ] = "received"

            elif status == "rejected":

                user[
                    "connection_status"
                ] = "none"

    cursor.close()
    conn.close()

    return render_template(
        "users.html",
        users=users_data,
        search=search,
        search_type=search_type
    )


# =========================================================
# MEMBER PROFILE
# =========================================================

@app.route("/member/<int:user_id>")
@login_required
def member_profile(user_id):

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = %s
    """, (user_id,))

    user = cursor.fetchone()

    if not user:

        cursor.close()
        conn.close()

        flash(
            "User not found.",
            "error"
        )

        return redirect(
            url_for("users")
        )

    cursor.execute("""
        SELECT
            s.skill_name,
            s.category,
            us.skill_type

        FROM user_skills us

        INNER JOIN skills s
        ON us.skill_id = s.id

        WHERE us.user_id = %s

        ORDER BY s.skill_name
    """, (user_id,))

    skills = cursor.fetchall()

    cursor.execute("""
        SELECT
            AVG(rating) AS average_rating,
            COUNT(*) AS total_reviews

        FROM reviews

        WHERE reviewed_user_id = %s
    """, (user_id,))

    review_data = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "member_profile.html",
        user=user,
        skills=skills,
        review_data=review_data
    )


# =========================================================
# SEND CONNECTION REQUEST
# =========================================================

@app.route(
    "/send-request/<int:user_id>",
    methods=["POST", "GET"]
)
@login_required
def send_request(user_id):

    current_user_id = session["user_id"]

    if current_user_id == user_id:

        flash(
            "You cannot connect with yourself.",
            "error"
        )

        return redirect(
            request.referrer
            or url_for("users")
        )

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    # -----------------------------------------------------
    # TARGET USER
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            full_name
        FROM users
        WHERE id = %s
    """, (user_id,))

    target_user = cursor.fetchone()

    if not target_user:

        cursor.close()
        conn.close()

        flash(
            "User not found.",
            "error"
        )

        return redirect(
            url_for("users")
        )

    # -----------------------------------------------------
    # EXISTING CONNECTION
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM connections

        WHERE
        (
            sender_id = %s
            AND receiver_id = %s
        )

        OR

        (
            sender_id = %s
            AND receiver_id = %s
        )

        ORDER BY id DESC
        LIMIT 1
    """, (
        current_user_id,
        user_id,
        user_id,
        current_user_id
    ))

    existing = cursor.fetchone()

    # -----------------------------------------------------
    # EXISTING CONNECTION FOUND
    # -----------------------------------------------------

    if existing:

        status = existing["status"]

        # Already connected
        if status == "accepted":

            cursor.close()
            conn.close()

            flash(
                "You are already connected with this user.",
                "error"
            )

            return redirect(
                request.referrer
                or url_for("users")
            )

        # Request already sent
        if status == "pending":

            if existing["sender_id"] == current_user_id:

                cursor.close()
                conn.close()

                flash(
                    "Connection request already sent.",
                    "error"
                )

                return redirect(
                    request.referrer
                    or url_for("users")
                )

            # Request received
            if existing["receiver_id"] == current_user_id:

                cursor.execute("""
                    UPDATE connections
                    SET status = 'accepted'
                    WHERE id = %s
                """, (
                    existing["id"],
                ))

                conn.commit()

                # Notify sender
                cursor.execute("""
                    INSERT INTO notifications
                    (
                        user_id,
                        message,
                        notification_type
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        'connection_accepted'
                    )
                """, (
                    existing["sender_id"],
                    "Your connection request was accepted."
                ))

                conn.commit()

                cursor.close()
                conn.close()

                flash(
                    "Connection accepted.",
                    "success"
                )

                return redirect(
                    request.referrer
                    or url_for("users")
                )

        # -------------------------------------------------
        # REJECTED REQUEST
        # -------------------------------------------------

        if status == "rejected":

            cursor.execute("""
                UPDATE connections

                SET
                    sender_id = %s,
                    receiver_id = %s,
                    user_id = %s,
                    connected_user_id = %s,
                    status = 'pending'

                WHERE id = %s
            """, (
                current_user_id,
                user_id,
                current_user_id,
                user_id,
                existing["id"]
            ))

            conn.commit()

            cursor.execute("""
                INSERT INTO notifications
                (
                    user_id,
                    message,
                    notification_type
                )
                VALUES
                (
                    %s,
                    %s,
                    'connection_request'
                )
            """, (
                user_id,
                "You received a new connection request."
            ))

            conn.commit()

            cursor.close()
            conn.close()

            flash(
                "Connection request sent.",
                "success"
            )

            return redirect(
                request.referrer
                or url_for("users")
            )

    # =====================================================
    # CREATE NEW REQUEST
    # =====================================================

    cursor.execute("""
        INSERT INTO connections
        (
            user_one_id,
            user_two_id,
            user_id,
            connected_user_id,
            sender_id,
            receiver_id,
            status
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            'pending'
        )
    """, (
        current_user_id,
        user_id,
        current_user_id,
        user_id,
        current_user_id,
        user_id
    ))

    conn.commit()

    # Notification
    cursor.execute("""
        INSERT INTO notifications
        (
            user_id,
            message,
            notification_type
        )
        VALUES
        (
            %s,
            %s,
            'connection_request'
        )
    """, (
        user_id,
        "You received a new connection request."
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Connection request sent.",
        "success"
    )

    return redirect(
        request.referrer
        or url_for("users")
    )


# =========================================================
# WITHDRAW CONNECTION REQUEST
# =========================================================

@app.route(
    "/withdraw-request/<int:user_id>",
    methods=["POST", "GET"]
)
@login_required
def withdraw_request(user_id):

    current_user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    # -----------------------------------------------------
    # FIND ONLY CURRENT USER'S REQUEST
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM connections

        WHERE sender_id = %s
        AND receiver_id = %s
        AND status = 'pending'

        ORDER BY id DESC
        LIMIT 1
    """, (
        current_user_id,
        user_id
    ))

    connection = cursor.fetchone()

    if not connection:

        cursor.close()
        conn.close()

        flash(
            "No pending request found.",
            "error"
        )

        return redirect(
            request.referrer
            or url_for("users")
        )

    # -----------------------------------------------------
    # DELETE CONNECTION REQUEST
    # -----------------------------------------------------

    cursor.execute("""
        DELETE FROM connections
        WHERE id = %s
    """, (
        connection["id"],
    ))

    conn.commit()

    # -----------------------------------------------------
    # REMOVE ONLY ONE RELATED NOTIFICATION
    # -----------------------------------------------------

    cursor.execute("""
        SELECT id
        FROM notifications

        WHERE user_id = %s
        AND notification_type = 'connection_request'
        AND message =
        'You received a new connection request.'

        ORDER BY id ASC
        LIMIT 1
    """, (
        user_id,
    ))

    notification = cursor.fetchone()

    if notification:

        cursor.execute("""
            DELETE FROM notifications
            WHERE id = %s
        """, (
            notification["id"],
        ))

        conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Connection request withdrawn.",
        "success"
    )

    return redirect(
        request.referrer
        or url_for("users")
    )


# =========================================================
# REQUESTS
# =========================================================

@app.route("/requests")
@login_required
def requests():

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            c.id AS connection_id,
            c.status,
            u.id AS user_id,
            u.full_name,
            u.username,
            u.email

        FROM connections c

        INNER JOIN users u
        ON c.sender_id = u.id

        WHERE c.receiver_id = %s
        AND c.status = 'pending'

        ORDER BY c.created_at DESC
    """, (user_id,))

    pending_requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "requests.html",
        requests=pending_requests
    )


# =========================================================
# ACCEPT REQUEST
# =========================================================

@app.route(
    "/accept-request/<int:connection_id>",
    methods=["GET", "POST"]
)
@login_required
def accept_request(connection_id):

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM connections

        WHERE id = %s
        AND receiver_id = %s
        AND status = 'pending'
    """, (
        connection_id,
        user_id
    ))

    connection = cursor.fetchone()

    if connection:

        cursor.execute("""
            UPDATE connections
            SET status = 'accepted'
            WHERE id = %s
        """, (
            connection_id,
        ))

        conn.commit()

        # Notify sender
        cursor.execute("""
            INSERT INTO notifications
            (
                user_id,
                message,
                notification_type
            )
            VALUES
            (
                %s,
                %s,
                'connection_accepted'
            )
        """, (
            connection["sender_id"],
            "Your connection request was accepted."
        ))

        conn.commit()

        flash(
            "Connection accepted.",
            "success"
        )

    else:

        flash(
            "Connection request not found.",
            "error"
        )

    cursor.close()
    conn.close()

    return redirect(
        url_for("requests")
    )


# =========================================================
# REJECT REQUEST
# =========================================================

@app.route(
    "/reject-request/<int:connection_id>",
    methods=["GET", "POST"]
)
@login_required
def reject_request(connection_id):

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE connections

        SET status = 'rejected'

        WHERE id = %s
        AND receiver_id = %s
        AND status = 'pending'
    """, (
        connection_id,
        user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Connection request rejected.",
        "success"
    )

    return redirect(
        url_for("requests")
    )


# =========================================================
# CONNECTIONS
# =========================================================

@app.route("/connections")
@login_required
def connections():

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT DISTINCT
            u.id,
            u.full_name,
            u.username,
            u.email

        FROM connections c

        INNER JOIN users u
        ON
        (
            c.sender_id = u.id
            AND c.receiver_id = %s
        )

        OR

        (
            c.receiver_id = u.id
            AND c.sender_id = %s
        )

        WHERE c.status = 'accepted'

        ORDER BY u.full_name
    """, (
        user_id,
        user_id
    ))

    connections_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "connections.html",
        connections=connections_data
    )


# =========================================================
# CHATS LIST
# =========================================================

@app.route("/chats")
@login_required
def chats():

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT DISTINCT
            u.id,
            u.full_name,
            u.username,
            u.email

        FROM connections c

        INNER JOIN users u

        ON
        (
            c.sender_id = u.id
            AND c.receiver_id = %s
        )

        OR

        (
            c.receiver_id = u.id
            AND c.sender_id = %s
        )

        WHERE c.status = 'accepted'

        ORDER BY u.full_name
    """, (
        user_id,
        user_id
    ))

    chat_users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "chats.html",
        chat_users=chat_users
    )


# =========================================================
# CHAT PAGE
# =========================================================

@app.route("/chat/<int:user_id>")
@login_required
def chat(user_id):

    current_user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    # -----------------------------------------------------
    # OTHER USER
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = %s
    """, (
        user_id,
    ))

    other_user = cursor.fetchone()

    if not other_user:

        cursor.close()
        conn.close()

        flash(
            "User not found.",
            "error"
        )

        return redirect(
            url_for("chats")
        )

    # -----------------------------------------------------
    # MESSAGES
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM messages

        WHERE
        (
            sender_id = %s
            AND receiver_id = %s
        )

        OR

        (
            sender_id = %s
            AND receiver_id = %s
        )

        ORDER BY created_at ASC
    """, (
        current_user_id,
        user_id,
        user_id,
        current_user_id
    ))

    messages = cursor.fetchall()

    # -----------------------------------------------------
    # MARK RECEIVED MESSAGES AS READ
    # -----------------------------------------------------

    cursor.execute("""
        UPDATE messages
        SET is_read = 1

        WHERE sender_id = %s
        AND receiver_id = %s
    """, (
        user_id,
        current_user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return render_template(
        "chat.html",
        other_user=other_user,
        messages=messages
    )


# =========================================================
# SEND MESSAGE
# =========================================================

@app.route(
    "/chat/send/<int:user_id>",
    methods=["POST"]
)
@login_required
def send_message(user_id):

    sender_id = session["user_id"]

    message = request.form.get(
        "message",
        ""
    ).strip()

    if message:

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages
            (
                sender_id,
                receiver_id,
                message
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """, (
            sender_id,
            user_id,
            message
        ))

        conn.commit()

        cursor.close()
        conn.close()

    return redirect(
        url_for(
            "chat",
            user_id=user_id
        )
    )


# =========================================================
# MATCHES
# =========================================================

@app.route("/matches")
@login_required
def matches():

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    # -----------------------------------------------------
    # CURRENT USER LEARNING SKILLS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT s.skill_name

        FROM user_skills us

        INNER JOIN skills s
        ON us.skill_id = s.id

        WHERE us.user_id = %s
        AND us.skill_type = 'learn'
    """, (
        user_id,
    ))

    learning_rows = cursor.fetchall()

    learning_skills = [
        row["skill_name"]
        for row in learning_rows
    ]

    # -----------------------------------------------------
    # CURRENT USER TEACHING SKILLS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT s.skill_name

        FROM user_skills us

        INNER JOIN skills s
        ON us.skill_id = s.id

        WHERE us.user_id = %s
        AND us.skill_type = 'teach'
    """, (
        user_id,
    ))

    teaching_rows = cursor.fetchall()

    teaching_skills = [
        row["skill_name"]
        for row in teaching_rows
    ]

    matches_data = []

    # -----------------------------------------------------
    # OTHER USERS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            full_name,
            username

        FROM users

        WHERE id != %s

        ORDER BY full_name
    """, (
        user_id,
    ))

    other_users = cursor.fetchall()

    for other_user in other_users:

        other_id = other_user["id"]

        # Other user's teaching skills
        cursor.execute("""
            SELECT s.skill_name

            FROM user_skills us

            INNER JOIN skills s
            ON us.skill_id = s.id

            WHERE us.user_id = %s
            AND us.skill_type = 'teach'
        """, (
            other_id,
        ))

        other_teach_rows = cursor.fetchall()

        other_teach = [
            row["skill_name"]
            for row in other_teach_rows
        ]

        # Other user's learning skills
        cursor.execute("""
            SELECT s.skill_name

            FROM user_skills us

            INNER JOIN skills s
            ON us.skill_id = s.id

            WHERE us.user_id = %s
            AND us.skill_type = 'learn'
        """, (
            other_id,
        ))

        other_learn_rows = cursor.fetchall()

        other_learn = [
            row["skill_name"]
            for row in other_learn_rows
        ]

        # -------------------------------------------------
        # CAN LEARN
        # -------------------------------------------------

        can_learn = []

        for skill in learning_skills:

            for other_skill in other_teach:

                if skill.lower() == other_skill.lower():

                    can_learn.append(
                        skill
                    )

        # -------------------------------------------------
        # CAN TEACH
        # -------------------------------------------------

        can_teach = []

        for skill in teaching_skills:

            for other_skill in other_learn:

                if skill.lower() == other_skill.lower():

                    can_teach.append(
                        skill
                    )

        if can_learn or can_teach:

            other_user["can_learn"] = can_learn

            other_user["can_teach"] = can_teach

            matches_data.append(
                other_user
            )

    cursor.close()
    conn.close()

    return render_template(
        "matches.html",
        matches=matches_data
    )


# =========================================================
# NOTIFICATIONS
# =========================================================

@app.route("/notifications")
@login_required
def notifications():

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM notifications

        WHERE user_id = %s

        ORDER BY created_at DESC
    """, (
        user_id,
    ))

    notifications_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications_data
    )


# =========================================================
# MARK NOTIFICATION READ
# =========================================================

@app.route(
    "/notifications/read/<int:notification_id>"
)
@login_required
def notification_read(
    notification_id
):

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notifications

        SET is_read = 1

        WHERE id = %s
        AND user_id = %s
    """, (
        notification_id,
        user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("notifications")
    )


# =========================================================
# RECOMMENDATIONS
# =========================================================

@app.route("/recommendations")
@login_required
def recommendations():

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT s.skill_name

        FROM user_skills us

        INNER JOIN skills s
        ON us.skill_id = s.id

        WHERE us.user_id = %s
        AND us.skill_type = 'learn'
    """, (
        user_id,
    ))

    wanted = cursor.fetchall()

    wanted_skills = [
        row["skill_name"]
        for row in wanted
    ]

    recommendations_data = []

    if wanted_skills:

        placeholders = ",".join(
            ["%s"] * len(wanted_skills)
        )

        query = f"""
            SELECT DISTINCT
                u.id,
                u.full_name,
                u.username,
                s.skill_name

            FROM users u

            INNER JOIN user_skills us
            ON u.id = us.user_id

            INNER JOIN skills s
            ON us.skill_id = s.id

            WHERE u.id != %s

            AND us.skill_type = 'teach'

            AND LOWER(s.skill_name)
            IN ({placeholders})

            ORDER BY u.full_name
        """

        params = [user_id]

        params.extend(
            wanted_skills
        )

        cursor.execute(
            query,
            tuple(params)
        )

        recommendations_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "recommendations.html",
        recommendations=recommendations_data
    )


# =========================================================
# REVIEW
# =========================================================

@app.route(
    "/review/<int:user_id>",
    methods=["GET", "POST"]
)
@login_required
def review(user_id):

    reviewer_id = session["user_id"]

    if reviewer_id == user_id:

        flash(
            "You cannot review yourself.",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    # -----------------------------------------------------
    # SAVE REVIEW
    # -----------------------------------------------------

    if request.method == "POST":

        rating = request.form.get(
            "rating",
            "5"
        )

        review_text = request.form.get(
            "review_text",
            ""
        ).strip()

        try:

            rating = int(rating)

        except:

            rating = 5

        if rating < 1:
            rating = 1

        if rating > 5:
            rating = 5

        cursor.execute("""
            SELECT id

            FROM reviews

            WHERE reviewer_id = %s
            AND reviewed_user_id = %s
        """, (
            reviewer_id,
            user_id
        ))

        existing = cursor.fetchone()

        if existing:

            cursor.execute("""
                UPDATE reviews

                SET
                    rating = %s,
                    review_text = %s

                WHERE id = %s
            """, (
                rating,
                review_text,
                existing["id"]
            ))

        else:

            cursor.execute("""
                INSERT INTO reviews
                (
                    reviewer_id,
                    reviewed_user_id,
                    rating,
                    review_text
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                reviewer_id,
                user_id,
                rating,
                review_text
            ))

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Review saved successfully.",
            "success"
        )

        return redirect(
            url_for(
                "member_profile",
                user_id=user_id
            )
        )

    # -----------------------------------------------------
    # REVIEWED USER
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            full_name,
            username

        FROM users

        WHERE id = %s
    """, (
        user_id,
    ))

    reviewed_user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "review.html",
        user=reviewed_user
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT id
            FROM users
            WHERE email = %s
        """, (
            email,
        ))

        user = cursor.fetchone()

        if user:

            token = secrets.token_urlsafe(32)

            expiry = (
                datetime.now()
                + timedelta(minutes=30)
            )

            cursor.execute("""
                UPDATE users

                SET
                    reset_token = %s,
                    reset_token_expiry = %s

                WHERE id = %s
            """, (
                token,
                expiry,
                user["id"]
            ))

            conn.commit()

            reset_url = url_for(
                "reset_password",
                token=token,
                _external=True
            )

            print()
            print(
                "=========================================="
            )
            print(
                "RESET PASSWORD URL:"
            )
            print(
                reset_url
            )
            print(
                "=========================================="
            )
            print()

            flash(
                "Reset link generated. Check Flask terminal.",
                "success"
            )

        else:

            flash(
                "No account found with that email.",
                "error"
            )

        cursor.close()
        conn.close()

        return redirect(
            url_for("forgot_password")
        )

    return render_template(
        "forgot_password.html"
    )


# =========================================================
# RESET PASSWORD
# =========================================================

@app.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):

    conn = get_db_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *

        FROM users

        WHERE reset_token = %s
        AND reset_token_expiry > NOW()
    """, (
        token,
    ))

    user = cursor.fetchone()

    if not user:

        cursor.close()
        conn.close()

        flash(
            "Invalid or expired reset link.",
            "error"
        )

        return redirect(
            url_for("forgot_password")
        )

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not password:

            cursor.close()
            conn.close()

            flash(
                "Password cannot be empty.",
                "error"
            )

            return redirect(
                url_for(
                    "reset_password",
                    token=token
                )
            )

        if password != confirm_password:

            cursor.close()
            conn.close()

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for(
                    "reset_password",
                    token=token
                )
            )

        cursor.execute("""
            UPDATE users

            SET
                password = %s,
                reset_token = NULL,
                reset_token_expiry = NULL

            WHERE id = %s
        """, (
            password,
            user["id"]
        ))

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Password reset successfully.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    cursor.close()
    conn.close()

    return render_template(
        "reset_password.html",
        token=token
    )


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>404 - Page Not Found</h1>
    <p>The requested page does not exist.</p>
    """, 404


# =========================================================
# 405 ERROR
# =========================================================

@app.errorhandler(405)
def method_not_allowed(error):

    return """
    <h1>405 - Method Not Allowed</h1>
    <p>The requested method is not allowed for this URL.</p>
    """, 405


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    try:

        ensure_database_structure()

        print(
            "=========================================="
        )

        print(
            "       SKILL EXCHANGE"
        )

        print(
            "       SHADOW SYSTEM"
        )

        print(
            "=========================================="
        )

        print(
            "Database connected successfully"
        )

        print(
            "Server: http://127.0.0.1:5000"
        )

        print(
            "=========================================="
        )

        app.run(
            debug=True,
            host="127.0.0.1",
            port=5000
        )

    except Exception as error:

        print(
            "=========================================="
        )

        print(
            "DATABASE / APPLICATION ERROR"
        )

        print(
            error
        )

        print(
            "=========================================="
        )