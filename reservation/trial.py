import mysql.connector

mydb = mysql.connector.connect(host='localhost',user='root',passwd='jillshals',database='mod1_moviebooking')

mycursor=mydb.cursor()

mycursor.execute("select * from Movie_details")

for i in mycursor:
    print(i)
