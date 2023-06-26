from flask import Flask, request, render_template, request, redirect
import mysql.connector

trial = Flask(__name__)

mydb=mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="jillshals",
  database="dbms_project"
)
cur=mydb.cursor()


cur.execute("CREATE TABLE wallet(username VARCHAR(20) NOT NULL REFERENCES users (username), balance INT);")
cur.execute("INSERT INTO wallet VALUES('jill2301,1200')")
mydb.commit()
cur.execute("SELECT * FROM wallet")
sta=cur.fetchall()
print(sta)
