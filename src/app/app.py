from flask import Flask, render_template, request, json, redirect, url_for
import mysql.connector
import random

app = Flask(__name__)

con = mysql.connector.connect(user='imse', 
                                  database='library', 
                                  password='imsepass', 
                                  host='mysql',
                                  port='3306')
cursor = con.cursor()

@app.route("/")
def main():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/test")
def test():
    return "<h1 style='color:blue'>TEST PAGE</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)