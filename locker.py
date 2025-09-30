from flask import Flask, render_template, request, redirect, url_for, flash,jsonify,session
import mysql.connector
import random
import smtplib
from datetime import datetime
import requests



app = Flask(__name__)



app.secret_key = "1234"




ESP32_IP = "http://192.168.39.173"


  # Change this to your ESP32's IP
ESP32_PORT = "80"
status = "locked"



block_status = "unblocked"
current_user=None


def generate_otp():
    return random.randint(1000, 9999)

def set_current_user(username):
    global current_user  # Declare current_user as global
    current_user = username 

# Connect to the database
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='users'
    )
    return conn

def send_email(to_email, username, password):
    from_email = "shelartanmay43@gmail.com"
    app_password = "jksu mnsd qpdd uagj"  # App-specific password
    subject = "Welcome to Kohinoor"

    message = f"""
    Subject: {subject}

    Dear {username},

    Welcome to Kohinoor!

    We are pleased to have you with us. Below are your login credentials:

    Username: {username}
    Password: {password}

    To ensure the security of your account, please click the link below to change your password and set your PIN:

    [http://127.0.0.1:5000/changepassword]

    If you have any questions or need assistance, feel free to contact us.

    Best regards,
    The Kohinoor Team
    """

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, app_password)
        server.sendmail(from_email, to_email, message)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)
        
    finally:
        server.quit()




@app.route('/',methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/logout')
def logout():
    set_current_user(None)  # Remove the current_user from the session
    return redirect(url_for('home')) 

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/check_user', methods=['POST'])
def check_user():
    username = request.form['username']
    password = request.form['password']

    # Check if fields are empty
    if not username or not password:
        error = "Please fill both the fields."
        flash(error, 'error')  # Flash the error message
        return render_template('login.html', error=error)

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if user is an admin
    cursor.execute("SELECT * FROM admin WHERE Username = %s", (username,))
    admin_user = cursor.fetchone()

    # Check if the user exists in the admin table
    if admin_user:
        
        if admin_user['password'] != password:
            error = "Incorrect credentials."
            flash(error, 'error')
            return render_template('login.html', error=error)
        set_current_user(username)
        flash("Login successful!", 'success')  # Flash success message
        return redirect(url_for('dashboard'))  # Redirect to admin dashboard

    # Check if user is a regular user
    cursor.execute("SELECT * FROM users WHERE Username = %s", (username,))
    regular_user = cursor.fetchone()

    # Check if the user exists in the users table
    if regular_user:
        
        if regular_user['Password'] != password:
            error = "Incorrect credentials"
            flash(error, 'error')
            return render_template('login.html', error=error)
        set_current_user(username)  # Store the username in session
        flash("Login successful!", 'success')  # Flash success message
        return redirect(url_for('userrequestotp'))  # Redirect to request OTP page

    # If username doesn't exist in either table
    error = "Incorrect credentials."
    flash(error, 'error')
    return render_template('login.html', error=error)




  
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Extract the first name from full name for the username
        username = full_name.split()[0]  # Assuming first name is the first part of full name

        # Check if all fields are filled and PIN is valid
        if not (full_name and email and password ):
            flash("All fields are required", 'error')
            return redirect(url_for('signup'))

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the full name or username already exists in the database
            cursor.execute("SELECT * FROM admin WHERE FullName = %s OR Username = %s", (full_name, username))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("This name or username is already taken. Please choose a different one.", 'error')
                return redirect(url_for('signup'))

            # Insert the new user into the database
            cursor.execute(
                "INSERT INTO admin (FullName, Username, Email, Password) VALUES (%s, %s, %s, %s)",
                (full_name, username, email, password)
            )
            conn.commit()
            flash("Account created successfully!", 'success')
        except mysql.connector.IntegrityError:
            flash("This email is already registered.", 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('signup'))

    return render_template('signup.html')



@app.route('/dashboard')
def dashboard():
    return render_template("user_dashboard.html")
  
@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    if request.method == 'POST':
        full_name = request.form['name']
        password = request.form['password']
        email = request.form['email']

        # Extract first name as username
        username = full_name.split()[0]
        register_date = datetime.now()

        # Database insertion
        conn = None
        try:
            conn = get_db_connection()  # Call the function to get the connection object
            cursor = conn.cursor()

            # Use the correct table and columns based on your provided structure
            query = """
                INSERT INTO users (Username, Password, Email, User_Register_Date) 
                VALUES (%s, %s, %s, %s)
            """
            values = (username, password, email, register_date)
            cursor.execute(query, values)
            conn.commit()

            # Send welcome email
            send_email(email, username, password)

            flash("User added successfully and email sent!", 'success')
            return render_template('adduser.html', success_message="User added successfully and email sent!")  # Display success message
        except mysql.connector.Error as err:
            print("Database error:", err)
            flash("Failed to add user.", 'error')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    return render_template('adduser.html')



  


@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_password = request.form['new_password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify the user with the username and password
        cursor.execute("SELECT * FROM users WHERE Username = %s AND Password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            # Update the password and pin in the database
            cursor.execute("UPDATE users SET Password = %s WHERE Username = %s", (new_password,username))
            conn.commit()
            flash("Your password has been successfully updated!", 'success')
            return redirect(url_for('login'))
        else:
            flash("Invalid username or password.", 'error')

        conn.close()

    return render_template('changepassword.html')

@app.route('/verify_user', methods=['POST'])
def verify_user():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE Username = %s AND Password = %s", (username, password))
    user = cursor.fetchone()

    if user:
        return {"status": "success", "message": "User verified. Please set a new password and PIN."}
    else:
        return {"status": "error", "message": "Invalid username or password."}



@app.route('/update_user', methods=['POST'])
def update_user():
    data = request.get_json()
    username = data['username']
    new_password = data['new_password']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify if the username exists in the database
    cursor.execute("SELECT * FROM users WHERE Username = %s", (username,))
    user = cursor.fetchone()

    if user:
        # Update the password and pin in the database
        cursor.execute("UPDATE users SET Password = %s WHERE Username = %s", (new_password,username))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Your password have been successfully updated!"}
    else:
        conn.close()
        return {"status": "error", "message": "User not found!"}





@app.route('/manageuser', methods=['GET'])
def manageuser():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT Username, Password, Email, User_Register_Date FROM users')
    users = cursor.fetchall()

    # Format the date in each row
    for user in users:
        if user.get("User_Register_Date"):
            date_str = user["User_Register_Date"].strftime("%d/%b/%Y")  # Format as DD/MON/YYYY
            user["User_Register_Date"] = date_str
    
    cursor.close()
    conn.close()
    return render_template("manageuser.html", users=users)




@app.route('/delete_user/<username>', methods=['POST'])
def delete_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE Username = %s', (username,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('manageuser'))

@app.route('/edituser', methods=['POST'])
def edit_user():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data received"})

    conn = get_db_connection()  # Store the connection in a variable
    cursor = conn.cursor()
    original_username = data.get('OriginalUsername')
    updated_username = data.get('Username')
    updated_password = data.get('Password')
    updated_email = data.get('Email')

    try:
        query = """
            UPDATE users
            SET Username=%s, Password=%s, Email=%s
            WHERE Username=%s
        """
        cursor.execute(query, (updated_username, updated_password, updated_email, original_username))
        conn.commit()  # Use the `conn` variable to commit
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        conn.close()





@app.route('/requestotp')
def requestotp():
    return render_template("requestotp.html")

@app.route('/userrequestotp')
def userrequestotp():
    return render_template("userrequestotp.html")



@app.route('/generate_otp', methods=['POST'])
def generate_and_send_otp():
    # Retrieve the username of the logged-in user
    global current_user
    username = current_user
    # Assuming session contains the logged-in user's username
    
    if not username:
        return jsonify({"error": "User is not logged in."}), 403

    otp = generate_otp()  # Generate the OTP
    otp_url = f"{ESP32_IP}:{ESP32_PORT}/receive_otp?otp={otp}"

    # Get the current date and time for logging
    current_time = datetime.now()
    access_date = current_time.strftime('%Y-%m-%d')  # Get the current date in 'YYYY-MM-DD' format
    access_time = current_time.strftime('%H:%M:%S')  # Get the current time in 'HH:MM:SS' format

    try:
        # Connect to the database
        conn = get_db_connection()  # Assuming you have this function to get DB connection
        cursor = conn.cursor()

        # Insert OTP access log into the lock_log table
        cursor.execute("""
            INSERT INTO lock_log (Username, Access_Type, Access_Date, Access_Time)
            VALUES (%s, %s, %s, %s)
        """, (username, 'Otp', access_date, access_time))

        # Commit the transaction
        conn.commit()

        # Sending OTP to ESP32
        response = requests.get(otp_url)

        return jsonify({"otp": otp, "status": response.text})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)})

    except Exception as e:
        # Handle any database-related errors
        return jsonify({"error": f"Database error: {str(e)}"})

    finally:
        # Close the database connection
        if conn:
            conn.close()



@app.route('/current_status', methods=['GET'])
def lockstatus():
    global status
    global current_user
    # Handle status update from ESP32 (through URL parameter)
    new_status = request.args.get('status')
    if new_status:
        status = new_status
        print(f"Status updated by ESP32: {status}")

        # Only insert into lock_log if the lock is opened (status == 'Lock')
        if status == "opened":
            # Get the current date and time for logging
            current_time = datetime.now()
            access_date = current_time.strftime('%Y-%m-%d')  # Current date in 'YYYY-MM-DD' format
            access_time = current_time.strftime('%H:%M:%S')  # Current time in 'HH:MM:SS' format
            
            # Retrieve the username of the logged-in user
            username = current_user
            print(username)# Assuming session contains the logged-in user's username

            if username:
                try:
                    # Connect to the database
                    conn = get_db_connection()  # Assuming you have this function to get DB connection
                    cursor = conn.cursor()

                    # Insert lock access log into the lock_log table
                    cursor.execute("""
                        INSERT INTO lock_log (Username, Access_Type, Access_Date, Access_Time)
                        VALUES (%s, %s, %s, %s)
                    """, (username, 'Lock', access_date, access_time))
                    print("Successful")

                    # Commit the transaction
                    conn.commit()

                except Exception as e:
                    print(f"Error inserting lock log: {str(e)}")

                finally:
                    # Close the database connection
                    if conn:
                        conn.close()

    # If the request is coming from the browser (GET /current_status), render the lockstatus.html
    return render_template('lockstatus.html', status=status)

    # Return the current status in JSON format for other requests (like AJAX)
    return jsonify({"status": status})



@app.route('/locklog')
def locklog():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to get all lock logs
    cursor.execute("SELECT * FROM lock_log")
    lock_logs = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Render the locklog template and pass the fetched data
    return render_template("locklog.html", lock_logs=lock_logs)


@app.route('/sendblockmail', methods=['GET'])
def sendblockmail():
    sendblockmailtouser("shelartanmay43@gmail.com")


def sendblockmailtouser(to_email):
    from_email = "shelarcb2@gmail.com"
    app_password = "lfzt arsq bmmt cwza"  # App-specific password
    subject = "Welcome to Kohinoor"

    message = f"""
    Subject: Alert: Multiple Incorrect OTP Attempts for Locker Access

Dear Tanmay,

I hope this email finds you well.

This is to inform you that there have been three consecutive failed attempts to access the locker by entering an incorrect OTP. This event may indicate a potential unauthorized access attempt.

Details:

User Name: {current_user}
Event: 3 consecutive incorrect OTP entries
Status: Locker access locked for security
Please take any necessary steps or investigations as required.

Thank you for your attention to this matter.

    """

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, app_password)
        server.sendmail(from_email, to_email, message)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)
    finally:
        server.quit()

    
@app.route('/blockstatus')
def blockstatus():
    return render_template('blockstatus.html', status=block_status)
    
@app.route('/block', methods=['POST'])
def block():
    try:
        response = requests.get(f"{ESP32_IP}/block_unlock?action=block")
        if response.status_code == 200:
            return "Blocked Successfully", 200
        else:
            return "Failed to Block", 500
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/unblock', methods=['POST'])
def unblock():
    try:
        response = requests.get(f"{ESP32_IP}/block_unlock?action=unblock")
        if response.status_code == 200:
            return "Unblocked Successfully", 200
        else:
            return "Failed to Unblock", 500
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/block_status', methods=['GET'])
def update_status():
    global block_status
    status = request.args.get('status')
    if status:
        block_status = status
        return "Status Updated", 200
    return "Invalid Request", 400


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
