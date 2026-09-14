from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
from email_validator import validate_email, EmailNotValidError

load_dotenv()

db = mysql.connector.connect(
    host="127.0.0.1",
    port=3307,
    user="root",
    password=os.getenv("DB_PASSWORD"),
    database="mydb",
    use_pure=True
)

print("mysql connected")

from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

csrf = CSRFProtect(app)

app.permanent_session_lifetime = timedelta(hours=2)

@app.route("/")
def home():
    return render_template("tattoo_home.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/book", methods=["GET", "POST"])
def book():

    if request.method == "POST":
        name = request.form.get("full_name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        services = request.form.getlist("services")
        day = request.form.get("day")
        time = request.form.get("time")

        if not name or not phone or not email or not services or not day or not time:
            return render_template("book.html", booking_error="fill in all fields.")

        if not name.replace(" ", "").isalpha():
            return render_template("book.html", booking_error="Enter a valid name.")
        
        try:
            cursor = db.cursor()

            cursor.execute ("""

            SELECT id
            FROM bookings
            WHERE day = %s AND time = %s AND status != 'canceled' 
            """, (day, time))

            existing_booking = cursor.fetchone()

            if existing_booking:
                cursor.close()
                return render_template("book.html", booking_error="This date and time are already booked")    

            try:
                validate_email(email)
            except EmailNotValidError:
                return render_template("book.html", booking_error="enter a valid email address.")    
            
            if not phone.isdigit() or len(phone) != 10 or not phone.startswith("69"):
                return render_template("book.html", booking_error="Enter a valid greek mobile number.")

            sql = """
            INSERT INTO bookings
            (full_name, phone, email, day, time, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            values = (name, phone, email, day, time, "confirmed")

            cursor.execute(sql, values)

            booking_id = cursor.lastrowid
            service_sql = "SELECT id FROM services WHERE name = %s"

            for service in services:
                cursor.execute(service_sql, (service,))
                result = cursor.fetchone()

                if result is None:
                    cursor.close()
                    return render_template("book.html", booking_error="Invalid service selected.")

                service_id = result[0]

                booking_service_sql = """
                INSERT INTO booking_services
                (booking_id, service_id)
                VALUES (%s, %s)
                """

                cursor.execute(
                    booking_service_sql,
                    (booking_id, service_id)
                )

            db.commit()

            cursor.close()    

            return render_template("book.html", booking_success=True, booking_id=booking_id, name=name, day=day, time=time, services=services)
                

        except Exception as e:
            db.rollback()
            print ("database error:", e)

            return render_template("book.html", booking_error="Something went wrong. Please try again.")   

    return render_template("book.html")


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        stored_hash = os.getenv("ADMIN_PASSWORD_HASH")

        if username == os.getenv("ADMIN_USERNAME") and check_password_hash(stored_hash, password):
            session.permanent = True
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        return render_template("admin_login.html", error=True)
    return render_template("admin_login.html")    

@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    status = request.args.get("status", "all")

    search = request.args.get("search", "")

    print("SEARCH:", search)
    
    cursor = db.cursor()

    sql = """
         SELECT
            b.id,
            b.full_name,
            b.phone,
            b.email,
            b.day,
            b.time,
            b.status,
            GROUP_CONCAT(s.name SEPARATOR ', ') AS services,
            SUM(s.price) AS total_price

        FROM bookings b

        JOIN booking_services bs
            ON b.id = bs.booking_id

        JOIN services s
            ON bs.service_id = s.id     
        """         

    params = []
    conditions = []
    
    if status == "confirmed":
        conditions.append("b.status = 'confirmed'")
    
    elif status == "canceled":
        conditions.append("b.status = 'canceled'")   
    
    if search:
        conditions.append("""
            (
                b.full_name LIKE %s
                OR b.phone LIKE %s
                OR b.email LIKE %s
            )
        """)     
    
        search_value = f"%{search}%"
    
        params.extend([
            search_value,
            search_value,
            search_value
        ])

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += """
        GROUP BY
            b.id,
            b.full_name,
            b.phone,
            b.email,
            b.day,
            b.time,
            b.status
    """    

    sql += "ORDER BY b.day ASC, b.time ASC"    

    cursor.execute(sql, params)    

    bookings = cursor.fetchall()

    print("ADMIN BOOKING", bookings)

    cursor.close()

    return render_template("admin.html", bookings=bookings, current_status=status, search=search)


@app.route("/admin-dashboard")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    cursor = db.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
    """)

    total_bookings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'confirmed'
    """)

    confirmed_bookings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'canceled'
    """)

    canceled_bookings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(s.price),0)
        FROM bookings b
        JOIN booking_services bs
            ON b.id = bs.booking_id
        JOIN services s
            ON bs.service_id = s.id
        WHERE b.status = 'confirmed'        
    """)

    total_revenue = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            s.name,
            COUNT(bs.id) AS booking_count,
            SUM(s.price) AS revenue
        FROM booking_services bs
        JOIN bookings b
            ON bs.booking_id = b.id
        JOIN services s
            ON bs.service_id = s.id
        WHERE b.status = 'confirmed'
        GROUP BY s.id, s.name
        ORDER BY revenue DESC    
    """)

    revenue_by_service = cursor.fetchall()

    cursor.close()

    return render_template(
                    "admin_dashboard.html",
                    total_bookings=total_bookings,
                    confirmed_bookings=confirmed_bookings,
                    canceled_bookings=canceled_bookings,
                    total_revenue=total_revenue,
                    revenue_by_service=revenue_by_service,
                    )

@app.route("/cancel-booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    
    cursor = db.cursor()

    cursor.execute("""
        UPDATE bookings
        SET status = 'canceled'
        WHERE id = %s
    """, (booking_id,))

    db.commit()

    cursor.close()

    return redirect(url_for("admin"))



@app.route("/admin_logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return(redirect(url_for("admin_login")))

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/lashes")
def lashes():
    return render_template("lashes.html")

@app.route("/nails")
def nails():
    return render_template("nails.html")

@app.route("/tattoo")
def tattoo():
    return render_template("tattoo.html")

@app.route("/user_cancel_booking", methods=["POST"])
def user_cancel_booking():

    booking_id = request.form.get("booking_id")

    cursor = db.cursor()

    cursor.execute("""
        UPDATE bookings
        SET status = "canceled"
        WHERE id = %s
    """, (booking_id,))

    db.commit()
    cursor.close()

    return render_template("book.html", cancellation_success=True)


if __name__ == "__main__":
    app.run(debug=True)