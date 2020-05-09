import random
import names
import os
import mysql.connector
import string

from mysql.connector import errorcode
from datetime import timedelta
from datetime import datetime

NUM_PERSONS = int(os.environ.get("PERSONS", 20))
NUM_FRIENDS = int(NUM_PERSONS * 0.5)
NUM_EMPLOYEES = int(NUM_PERSONS * 0.2)
NUM_MEMBERS = int(NUM_PERSONS * 0.8)
NUM_AUTHORS = int(os.environ.get("AUTHORS", 10))
NUM_BOOKS = int(os.environ.get("BOOKS", 30))
NUM_BUILDINGS = int(os.environ.get("BUILDINGS", 2))
NUM_SHELVES = int(NUM_BUILDINGS * 50)
NUM_RENTALS = int(NUM_BOOKS * 0.9)
NUM_RETURNS = int(NUM_BOOKS * 0.4)

TABLES = {}
TABLES['persons'] = (
    """CREATE TABLE persons (
        first_name varchar(32),
        last_name varchar(32),
        birthday date,
        insurance_number int(8) NOT NULL,
        PRIMARY KEY(insurance_number)
    )"""
)
TABLES['friends'] = (
    """CREATE TABLE friends (
        insurance_number int(8) NOT NULL,
        friend_insurance int(8) NOT NULL,
        PRIMARY KEY (insurance_number, friend_insurance),
        FOREIGN KEY (friend_insurance) REFERENCES persons (insurance_number) ON DELETE CASCADE
    )"""
)
TABLES['buildings'] = (
    """CREATE TABLE buildings (
        address varchar(32) NOT NULL,
        rooms int(1) NOT NULL,
        PRIMARY KEY (address)
    )"""
)
TABLES['shelves'] = (
    """CREATE TABLE shelves (
        room_number int(1) NOT NULL,
        capacity int(3) NOT NULL,
        building_address varchar(32) NOT NULL,
        PRIMARY KEY (room_number, building_address),
        FOREIGN KEY (building_address) REFERENCES buildings (address) ON DELETE CASCADE
    )"""
)
TABLES['employees'] = (
    """CREATE TABLE employees (
        staff_number int(8) NOT NULL AUTO_INCREMENT,
        insurance_number int(8) UNIQUE NOT NULL,
        salary int(4) NOT NULL,
        building_address varchar(32) NOT NULL,
        PRIMARY KEY (staff_number),
        FOREIGN KEY (building_address) REFERENCES buildings (address) ON DELETE CASCADE,
        FOREIGN KEY (insurance_number) REFERENCES persons (insurance_number) ON DELETE CASCADE
    )"""
)
TABLES['members'] = (
    """CREATE TABLE members (
        username varchar(8) NOT NULL,
        insurance_number int(8) UNIQUE NOT NULL,
        password varchar(8) NOT NULL,
        join_date date NOT NULL,
        home_location varchar(32) NOT NULL,
        PRIMARY KEY (username),
        FOREIGN KEY (home_location) REFERENCES buildings (address) ON DELETE CASCADE,
        FOREIGN KEY (insurance_number) REFERENCES persons (insurance_number) ON DELETE CASCADE
    )"""
)
TABLES['authors'] = (
    """CREATE TABLE authors (
        name varchar(32) NOT NULL,
        birthday date NOT NULL,
        PRIMARY KEY (name)
    )"""
)
TABLES['books'] = (
    """CREATE TABLE books (
        isbn int(13) NOT NULL AUTO_INCREMENT,
        title varchar(32) NOT NULL,
        room_number int(1) NOT NULL,
        building_address varchar(32) NOT NULL,
        PRIMARY KEY (isbn),
        FOREIGN KEY (room_number, building_address) REFERENCES shelves (room_number, building_address) ON DELETE CASCADE
    )"""
)
TABLES['bookauthor'] = (
    """CREATE TABLE bookauthor (
        isbn int(13) NOT NULL,
        author_name varchar(32) NOT NULL,
        PRIMARY KEY (isbn, author_name),
        FOREIGN KEY (isbn) REFERENCES books (isbn) ON DELETE CASCADE,
        FOREIGN KEY (author_name) REFERENCES authors (name) ON DELETE CASCADE
    )"""
)
TABLES['rentals'] = (
    """CREATE TABLE rentals (
        member_username varchar(8) NOT NULL,
        isbn int(13) NOT NULL,
        rental_date date NOT NULL,
        building_address varchar(32) NOT NULL,
        PRIMARY KEY (member_username, isbn, rental_date, building_address),
        FOREIGN KEY (member_username) REFERENCES members (username) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (building_address) REFERENCES shelves (building_address),
        FOREIGN KEY (isbn) REFERENCES books (isbn) ON DELETE CASCADE
    )"""
)
TABLES['returns'] = (
    """CREATE TABLE returns (
        member_username varchar(8) NOT NULL,
        isbn int(13) NOT NULL,
        return_date date NOT NULL,
        building_address varchar(32) NOT NULL,
        PRIMARY KEY (member_username, isbn, return_date, building_address),
        FOREIGN KEY (member_username) REFERENCES members (username) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (building_address) REFERENCES shelves (building_address),
        FOREIGN KEY (isbn) REFERENCES books (isbn) ON DELETE CASCADE
    )
    """
)

def password(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def random_date():
    delta = datetime.strptime('1/1/2020', '%d/%m/%Y') - datetime.strptime('1/1/1900', '%d/%m/%Y')
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return datetime.strptime('1/1/1900', '%d/%m/%Y') + timedelta(seconds=random_second)

if __name__ == '__main__':
    con = mysql.connector.connect(user='imse', 
                                  database='library', 
                                  password='imsepass', 
                                  host='mysql',
                                  port='3306')
    cursor = con.cursor()

    first_person_row_id = None
    first_book_row_id = None
    first_author_row_id = None

    for tab in TABLES:
        table_info = TABLES[tab]
        try:
            cursor.execute(table_info)
        except mysql.connector.Error as error:
            if error.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("exists")
            else:
                print(error.msg)
        else:
            print("OK")
    
    cursor.execute("DELETE FROM persons")
    for i in range (NUM_PERSONS):
        stmt = "INSERT INTO persons VALUES ('{}','{}','{}','{}')".format(names.get_first_name(), 
                                                                         names.get_last_name(), 
                                                                         random_date().strftime('%Y-%m-%d'), 
                                                                         random.randint(10000000, 99999999))
        try:
            cursor.execute(stmt)
            if first_person_row_id is None:
                first_person_row_id = cursor.lastrowid
            con.commit()
        except:
            continue
    
    cursor.execute("DELETE FROM friends") 
    cursor.execute("SELECT insurance_number FROM persons")
    people = cursor.fetchall()
    for i in range (NUM_FRIENDS):
        stmt = "INSERT INTO friends VALUES ('{}','{}')".format(int(random.choice(people)[0]), int(random.choice(people)[0]))
        try:
            cursor.execute(stmt)
            con.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            continue
    
    cursor.execute("DELETE FROM buildings")
    for i in range(NUM_BUILDINGS):
        stmt = "INSERT INTO buildings VALUES ('{}','{}')".format("Address_"+str(i), random.randint(0, 6))
        try:
            cursor.execute(stmt)
            con.commit()
        except:
            continue
    
    cursor.execute("DELETE FROM shelves")
    cursor.execute("SELECT address FROM buildings")
    buildings = cursor.fetchall()
    for i in range(NUM_SHELVES):
        stmt = "INSERT INTO shelves VALUES ('{}','{}','{}')".format(random.randint(0, 9), random.randint(100, 999), random.choice(buildings)[0])
        try:
            cursor.execute(stmt)
            con.commit()
        except:
            continue

    cursor.execute("DELETE FROM employees")
    person = random.choice(people)
    people.remove(person)
    stmt = "INSERT INTO employees VALUES ('{}','{}','{}','{}')".format(10000000, person[0], random.randint(1000, 1200), random.choice(buildings)[0])
    try:
        cursor.execute(stmt)
        con.commit()
    except mysql.connector.Error as err:
        print(err.msg)
        pass
    for i in range(NUM_EMPLOYEES-1):
        person = random.choice(people)
        people.remove(person)
        stmt = "INSERT INTO employees (insurance_number, salary, building_address) VALUES ('{}','{}','{}')".format(person[0], random.randint(1000, 1200), random.choice(buildings)[0])
        try:
            cursor.execute(stmt)
            con.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            continue

    cursor.execute("DELETE FROM members")
    first = True
    for i in range(NUM_MEMBERS):
        person = random.choice(people)
        people.remove(person)
        if first is True:
            stmt = "INSERT INTO members VALUES ('{}','{}','{}','{}','{}')".format("12345678", person[0], password(), random_date(), random.choice(buildings)[0])
            first = False
        else:
            stmt = "INSERT INTO members VALUES ('{}','{}','{}','{}','{}')".format(password(), person[0], password(), random_date(), random.choice(buildings)[0])
        try:
            cursor.execute(stmt)
            con.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            continue

    cursor.execute("DELETE FROM authors")
    for i in range(NUM_AUTHORS):
        stmt = "INSERT INTO authors VALUES ('{}', '{}')".format(names.get_full_name(), random_date())
        try:
            cursor.execute(stmt)
            con.commit()
        except:
            continue
    
    cursor.execute("DELETE FROM books")
    cursor.execute("SELECT room_number, building_address FROM shelves")
    shelves = cursor.fetchall()
    stmt = "INSERT INTO books VALUES ('{}','{}')".format(1000000000000, "The life of " + names.get_full_name())
    try:
        cursor.execute(stmt)
        con.commit()
    except:
        pass
    for i in range(NUM_BOOKS):
        stmt = "INSERT INTO books (title, room_number, building_address) VALUES ('{}', '{}', '{}')".format("The life of " + names.get_full_name(), random.choice(shelves)[0], random.choice(shelves)[1])
        try:
            cursor.execute(stmt)
            con.commit()
        except:
            continue
    
    cursor.execute("DELETE FROM bookauthor")
    cursor.execute("SELECT isbn FROM books")
    books = cursor.fetchall()
    cursor.execute("SELECT name FROM authors")
    authors = cursor.fetchall()
    for book in books:
        stmt = "INSERT INTO bookauthor VALUES ('{}','{}')".format(book[0], random.choice(authors)[0])
        try:
            cursor.execute(stmt)
            con.commit()
        except:
            continue

    cursor.execute("DELETE FROM rentals")
    cursor.execute("SELECT username FROM members")
    members = cursor.fetchall()
    for i in range(NUM_RENTALS):
        stmt = "INSERT INTO rentals VALUES ('{}','{}','{}','{}')".format(random.choice(members)[0], random.choice(books)[0], random_date(), random.choice(buildings)[0])
        try:
            cursor.execute(stmt)
            con.commit()
        except:
            continue
    
    cursor.execute("DELETE FROM returns")
    for i in range(NUM_RETURNS):
        stmt = "INSERT INTO returns VALUES ('{}','{}','{}','{}')".format(random.choice(members)[0], random.choice(books)[0], random_date(), random.choice(buildings)[0])
        try:
            cursor.execute(stmt)
            con.commit()
        except:
            continue
    
    cursor.close()
    con.close()
        
        