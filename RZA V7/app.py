from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from flask_bcrypt import Bcrypt
import requests
import json
import threading
from socket import gaierror, gethostbyname
from multiprocessing.dummy import Pool as ThreadPool
from urllib.parse import urlparse
from flask import Flask, render_template, jsonify
from time import gmtime, strftime
from collections import Counter
#Importing all the libraries needed

app = Flask(__name__)
bcrypt = Bcrypt(app) #creates bcrypt instance 
app.config['SECRET_KEY'] = 'thisIsSecret'
login_manager =LoginManager(app)
login_manager.login_view="login_post"

#creates a user model representing the user
class User(UserMixin):
    def __init__ (self,id,email,password, firstname=None, lastname=None, address=None, user_points=0):
        self.id = id
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.user_points = user_points
        self.authenticated = False
        def is_active(self):
            return self.is_active()
        def is_anonymous(self):
            return False
        def is_authenticated(self):
            return self.authenticated
        def is_active(self):
            return True
        def get_id(self):
            return self.id
        def get_email(self):
            return self.email
        def get_firstname(self):
            return self.firstname
        def get_user_points (self):
            return self.user_points
        


@app.route('/login', methods =['POST', 'GET'])
def login_post():
    print("login post") # for debugging
    if request.method=="GET":
        return render_template('login.html')
    print("login post 2")
    #check if alreddy logged in - if so send home
    if current_user.is_authenticated:
        print("already logged in")
        return redirect(url_for('account'))
        #standard database stuff and find the user with email
    con = sqlite3.connect("zoo.db")
    curs = con.cursor()
    email = request.form['email']
    curs.execute ("SELECT * FROM users where email = (?)",[email])
    #returns first matching user then pass the details to create a user object - unless there is nothing returned then flash a msg
    row = curs.fetchone()
    print(row)
    if row == None:
        flash('Please try logging in again')
        return render_template('login.html')
    user = list(row)
    liUser = User(int(user[0]),user[1],user[2],user[3], user[4], user[5], user[6])
    password = request.form['password']
    match = bcrypt.check_password_hash(liUser.password,password)
    #if password matches - run the login_user method 
    if match and email == liUser.email:
        login_user(liUser,remember=request.form.get('remember'))
        print("Home")
        return redirect(url_for('account'))
    else:
        flash('Pleae try logging in again')
        return render_template('login.html')
    return render_template('login.html')

@login_manager.user_loader
def load_user(id):
    conn = sqlite3.connect('zoo.db')
    curs = conn.cursor()
    curs.execute("SELECT * from users where id=(?)",[id]) #Connects to database corresnponding to userID
    liUser = curs.fetchone()
    if liUser is None:
        return None  #returns none if no user exists
    else: 
        return User(int(liUser[0]), liUser[1], liUser[2], liUser[3], liUser[4], liUser[5], liUser[6]) 
        # creates the user object with all of the columns 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
from flask import flash


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        address = request.form['address']

        # Check if the email already exists in the database
        con = sqlite3.connect("zoo.db")
        curs = con.cursor()
        curs.execute("SELECT * FROM users WHERE email=?", (email,))
        user = curs.fetchone()

        if user:
            flash('Email already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        
        # Password validation
        if len(password) < 7 or not any(char.isupper() for char in password):
            flash('Password must be at least 7 characters long and contain at least one uppercase letter.', 'error')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password)

        # Add the user to the database
        curs.execute('INSERT INTO users (email, password, firstname, lastname, address) VALUES (?, ?, ?, ?, ?)',
                     (email, hashed_password, firstname, lastname, address))
        con.commit()
        con.close()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login_post'))

    return render_template('register.html')


@app.route('/')
def home():
    return render_template('home.html')
# Creates route for index




@app.route('/bookings', methods=['POST', 'GET'])
@login_required
def createBooking():
    if request.method == 'GET':
        return render_template('bookings.html')
    elif request.method == 'POST':
        request.form.items()

        try:
            date = request.form['dateChosen']
            numTickets = int(request.form['numTickets'])

            with sqlite3.connect("zoo.db") as con:  
                cur = con.cursor()

                # Check available slots for the chosen date
                cur.execute("SELECT Slots FROM availablezoo WHERE Date = ?", (date,))
                available_slots = cur.fetchone()

                if available_slots and available_slots[0] >= int(numTickets):
                    # Sufficient slots available, proceed with booking

                    points_to_deduct = 0  # Initialize points_to_deduct
                    redeemed_tickets = 0  # Initialize redeemed_tickets

                    # Check if user has enough points to redeem
                    if current_user.user_points >= 100:
                        # Deduct 100 points for each ticket redeemed
                        points_to_deduct = min(100, numTickets * 100)
                        cur.execute("UPDATE users SET user_points = user_points - ? WHERE id = ?",
                                    (points_to_deduct, current_user.id))
                        redeemed_tickets = points_to_deduct // 100
                        numTickets -= redeemed_tickets

                        # Flash message for points redemption
                        flash(f'{redeemed_tickets} ticket(s) were redeemed with your points.')

                    # Update points for purchased tickets
                    points_earned = 20 * numTickets
                    cur.execute("UPDATE users SET user_points = user_points + ? WHERE id = ?",
                                (points_earned, current_user.id))

                    # Update available slots in availablezoo
                    cur.execute("UPDATE availablezoo SET Slots = Slots - (?) WHERE Date = ?",
                                (int(numTickets), date))

                    # Create bookings for each ticket
                    for _ in range(int(numTickets)):
                        cur.execute("INSERT INTO zoobookings (userID, dateID) VALUES (?, ?)",
                                    (current_user.id, date))

                    con.commit()
                    
                    # Calculate the remaining points accurately
                    new_user_points = current_user.user_points - points_to_deduct + points_earned

                    # Adjusted flash message for booking
                    if redeemed_tickets > 0:
                        flash(f'Successful Booking. The ticket(s) have been added to your account. You now have a total of {new_user_points} points.')
                    else:
                        flash(f'Successful Booking. The ticket(s) have been added to your account. You now have a total of {new_user_points} points.')
                else:
                    flash('Date is fully booked or not available')

        except Exception as e:
            flash(f'Error occurred during booking: {str(e)}')
            print(e)

        finally:
            return render_template("bookings.html")


@app.route("/account")
@login_required
def account():
    with sqlite3.connect("zoo.db") as con:
        cur = con.cursor()
        cur.execute("select dateID from zoobookings where userID = (?)",[current_user.id])
        rows = cur.fetchall(); 
        datesCount=list(Counter((rows)).items())
        #print(datesCount[0])
    return render_template("account.html",bookings=datesCount)


@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        # Connect to the database
        with sqlite3.connect("zoo.db") as con:
            cur = con.cursor()
            try:
                # Delete the user's record from the database based on their ID
                cur.execute("DELETE FROM users WHERE id = ?", (current_user.id,))
                con.commit()
                flash('Your account has been successfully deleted.', 'success')
                return redirect(url_for('home'))  # Redirect to the home page or any other page
            except Exception as e:
                con.rollback()
                flash('An error occurred while deleting your account. Please try again.', 'error')
                print(e)
    return render_template('delete-account.html')  # Render the confirmation page

@app.route('/manage_bookings', methods=['GET', 'POST'])
@login_required
def manage_bookings():
    if request.method == 'GET':
        conn = sqlite3.connect("zoo.db")
        cur = conn.cursor() #Standard db stuff to connect to zoo db
        cur.execute("SELECT * FROM zoobookings WHERE userID = ?", (current_user.id,)) # userID = current user id from class
        bookings = cur.fetchall() # bookings varialbe = everything retrieved
        conn.close()
        return render_template('manage_bookings.html', bookings=bookings) # returns bookings to html
    
    elif request.method == 'POST':
        booking_id = request.form.get('booking_id') # if it is post request then booking id = booking id from the form that was from the current user id class
        
        if not booking_id:
            flash('Invalid booking ID.', 'error') # if there is an issue then flash this
            return redirect(url_for('manage_bookings'))
        
        conn = sqlite3.connect("zoo.db")
        cur = conn.cursor()
        cur.execute("SELECT userID FROM zoobookings WHERE bookingID = ?", (booking_id,)) #standard db connection; select everything from the userID where the booking id is that
        result = cur.fetchone() # store everything in this variable
        
        if result and result[0] == current_user.id:
            cur.execute("DELETE FROM zoobookings WHERE bookingID = ?", (booking_id,)) # delete the booking from the zoobookings table 
            conn.commit()
            conn.close()
            flash('Booking canceled successfully.', 'success')
        else:
            flash('You are not authorized to cancel this booking.', 'error')
            #flash result if error
        return redirect(url_for('manage_bookings'))



@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/tnc")
def tnc():
    return render_template("tnc.html")

@app.route("/policy")
def policy():
    return render_template("policy.html")

@app.route("/accessibility")
def accessbility():
    return render_template("accessibility.html")


@app.route("/meetthezoo")
def meetthezoo():
    return render_template("meetthezoo.html")

@app.route("/visiting")
def visiting():
    return render_template("visiting.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404    

if __name__ == '__main__':
    app.run(debug=True)
#runs file