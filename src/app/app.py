from flask import Flask, render_template, request, json, redirect, url_for
from datetime import datetime
import mysql.connector
import random
import string

app = Flask(__name__)

con = mysql.connector.connect(user='imse', 
                                  database='library', 
                                  password='imsepass', 
                                  host='mysql',
                                  port='3306')
cursor = con.cursor()

def password(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/member/login/<m_id>')
def m_login(m_id):
    cursor.execute("SELECT username FROM members")
    ids = cursor.fetchall()
    for i in range(len(ids)):
        if m_id == ids[i][0]:
            return redirect(url_for('location_select', member=m_id))
    return redirect(url_for('error'))

@app.route('/<member>/location_select')
def location_select(member):
    cursor.execute("SELECT address FROM buildings")
    buildings = cursor.fetchall()
    return render_template('library_select.html', member=member, buildings=buildings)

@app.route('/member_dashboard/<location>/<member>+<message>')
def member_dashboard(location, member, message):
    cursor.execute("SELECT first_name FROM persons NATURAL JOIN members WHERE username = '{}'".format(member))
    name = cursor.fetchall()[0][0]
    return render_template('member_dashboard.html', location=location, name=name, member=member, message=message)

@app.route('/new_rental/<location>/<member_id>')
def rent(location, member_id):
    cursor.execute("SELECT name, title, room_number FROM books NATURAL JOIN bookauthor NATURAL JOIN authors WHERE building_address = '{}'".format(location))
    books = cursor.fetchall()
    return render_template('new_rental.html', location=location, member=member_id, books=books)

@app.route('/new_rental/<location>/<member_id>/<title>+<author>')
def rent_search(location, member_id, title, author):
    cursor.execute("SELECT name, title, room_number FROM books NATURAL JOIN bookauthor NATURAL JOIN authors WHERE name = '{}' AND title = '{}' AND building_address = '{}'".format(author, title, location))
    books = cursor.fetchall()
    return render_template('new_rental.html', location=location, member=member_id, books=books)

@app.route('/rent/<location>/<member_id>/<author>+<title>')
def do_rent(location, member_id, author, title):
    cursor.execute("SELECT isbn FROM books WHERE title = '{}'".format(title))
    isbn = cursor.fetchall()[0][0]
    date = datetime.today().strftime('%Y-%m-%d')
    cursor.execute("INSERT INTO rentals VALUES ('{}', '{}', '{}', '{}')".format(member_id, isbn, date, location))
    message = "Your rental has been saved"
    return redirect(url_for('member_dashboard', location=location, member=member_id, message=message)) 

@app.route('/new_return/<location>/<member>')
def return_book(location, member):
    cursor.execute("SELECT title, isbn FROM rentals NATURAL JOIN books WHERE member_username = '{}'".format(member))
    books = cursor.fetchall()
    cursor.execute("SELECT title, isbn FROM returns NATURAL JOIN books WHERE member_username = '{}'".format(member))
    already_returned = cursor.fetchall()
    current_books = [b for b in books if b not in already_returned]
    return render_template('new_return.html', location=location, member=member, books=current_books)

@app.route('/return/<location>/<member_id>/<title>')
def do_return(location, member_id, title):
    cursor.execute("SELECT isbn FROM books WHERE title = '{}'".format(title))
    isbn = cursor.fetchall()[0][0]
    date = datetime.today().strftime('%Y-%m-%d')
    cursor.execute("INSERT INTO returns VALUES ('{}', '{}', '{}', '{}')".format(member_id, isbn, date, location))
    message = "Thank you for returning the book."
    return redirect(url_for('member_dashboard', location=location, member=member_id, message=message))

@app.route('/update_info/<member>')
def update_info(member):
    cursor.execute("SELECT insurance_number FROM members WHERE username = '{}'".format(member))
    insurance = cursor.fetchall()[0][0]
    cursor.execute("SELECT username, password, birthday, first_name, last_name FROM members NATURAL JOIN persons WHERE insurance_number = '{}'".format(insurance))
    info = cursor.fetchall()
    return render_template('update_info.html', info=info, insurance=insurance)

@app.route('/update/<insurance>/<user>+<password>+<date>+<fname>+<lname>')
def do_update(insurance, user, password, date, fname, lname):
    cursor.execute("UPDATE persons SET first_name = '{}', last_name = '{}', birthday = '{}' WHERE insurance_number = '{}'".format(fname, lname, date, insurance)) 
    cursor.execute("UPDATE members SET username = '{}', password = '{}' WHERE insurance_number = '{}'".format(user, password, insurance))
    return redirect(url_for('main'))

@app.route('/employee/login/<e_id>')
def e_login(e_id):
    cursor.execute("SELECT staff_number FROM employees")
    ids = cursor.fetchall()
    for i in range(len(ids)):
        if e_id == str(ids[i][0]):
            return redirect(url_for('e_dashboard'))
    return redirect(url_for('error'))

@app.route('/e_dashboard/<search>/<rent>/<username>', defaults={'new_user' : None, 'new_pass' : None})
@app.route('/e_dashboard/<new_user>/<new_pass>', defaults={'search' : None, 'rent' : None, 'username' : None})
@app.route('/e_dashboard/', defaults={'search' : None, 'rent' : None, 'username' : None, 'new_user' : None, 'new_pass' : None})
def e_dashboard(search, rent, username, new_user, new_pass):
    cursor.execute("SELECT first_name, last_name, username, home_location FROM (SELECT returns.member_username FROM rentals INNER JOIN returns ON rentals.building_address <> returns.building_address) AS t1 NATURAL JOIN members NATURAL JOIN persons GROUP BY username")
    report = cursor.fetchall()
    cursor.execute("SELECT address FROM buildings")
    buildings = cursor.fetchall()
    if new_user is None:
        new_user = "        "
    if new_pass is None:
        new_pass = " "
    if username is None:
        cursor.execute("SELECT first_name, last_name, members.username, title, rental_date FROM books NATURAL JOIN rentals NATURAL JOIN members NATURAL JOIN persons")
    else:
        cursor.execute("SELECT first_name, last_name, members.username, title, rental_date FROM books NATURAL JOIN rentals NATURAL JOIN members NATURAL JOIN persons WHERE username = '{}'".format(username))
    rentals = cursor.fetchall()
    return render_template('employee_dashboard.html', rentals=rentals, buildings=buildings, new_user=new_user, new_pass=new_pass, report=report)

@app.route('/add_member/<fname>+<lname>+<insurance>+<home>')
def new_member(fname, lname, insurance, home):
    cursor.execute("INSERT INTO persons (first_name, last_name, insurance_number) VALUES ('{}','{}','{}')".format(fname, lname, insurance))
    new_username = password()
    new_password = password()
    date = datetime.today().strftime('%Y-%m-%d')
    cursor.execute("INSERT INTO members VALUES ('{}','{}','{}','{}','{}')".format(new_username, insurance, new_password, date, home))
    return redirect(url_for('e_dashboard', new_user=new_username, new_pass=new_password))

@app.route("/error")
def error():
    return render_template('error.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)