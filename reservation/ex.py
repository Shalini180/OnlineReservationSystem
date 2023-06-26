from flask import Flask, request, render_template, request, redirect
import mysql.connector

ex = Flask(__name__)

mydb=mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="jillshals",
  database="dbms_project"
)

cur_user=''

@ex.route('/login',methods=['GET','POST'])
def index():
    global cur_user
    cur_user=''
    if request.method == 'POST':
        userDetails = request.form
        uname=userDetails['username']
        passwd=userDetails['passwd']
        cur=mydb.cursor()
        cur.execute("SELECT * FROM p_users WHERE username=%s AND pass=%s",(uname,passwd))
        details=cur.fetchall()
        if len(details)==0:
            return render_template('loginpage.html',msg="Invalid username or password")
        else:
            cur_user=uname
            return redirect('/home')
    return render_template('loginpage.html',msg="")

@ex.route('/signup',methods=['GET','POST'])
def signup():
    global cur_user
    cur_user=''
    if request.method == 'POST':
        newdetails=request.form
        name=newdetails['Name']
        uname=newdetails['Username']
        email=newdetails['Email']
        passw=newdetails['Password']
        cpass=newdetails['Conf_pass']
        if passw!=cpass:
            return render_template('signup.html',msg="The passwords don't match")
        else:
            cur=mydb.cursor()
            cur.execute("SELECT username from p_users")
            all_usernames=cur.fetchall()
            all_names=[]
            for i in all_usernames:
                all_names.append(i[0])
            if uname in all_names:
                return render_template('signup.html',msg="Username already exists")
            else:
                cur.execute("INSERT INTO p_users VALUES(%s,%s,%s,%s)",(uname,name,email,passw))
                a='50000'
                cur.execute("INSERT INTO USERW VALUES(%s,%s)",(uname,a))
                mydb.commit()
                cur.close()
                cur_user=uname
                return redirect('/home')
    return render_template('signup.html')

@ex.route('/home')
def users():
    return render_template('homepage.html')

@ex.route('/flight_index',methods=['GET','POST'])
def flights():
    global cur_user
    if cur_user=='':
        return redirect('/login')
    cur=mydb.cursor()
    cur.execute("SELECT * FROM airport")
    routes=cur.fetchall()
    if request.method=='POST':
        payment=request.form.get('optradio')
        a='a'
        detail=payment.split('--')
        cur.execute("SELECT * FROM userw WHERE cname=%s and 'a'=%s",(cur_user,a))
        bal=cur.fetchall()
        bal=bal[0][1]
        if int(bal)<int(detail[1]):
            return render_template('flight_index.html',airports=routes,msg="Insufficient balance in account")
        else:
            bal=int(bal)-int(detail[1])
            bal=str(bal)
            cur.execute("UPDATE userw SET bal=%s WHERE cname=%s",(bal,cur_user))
            mydb.commit()
            cur.execute("SELECT * FROM contains WHERE cname=%s and 'a'=%s",(cur_user,a))
            con=cur.fetchall()
            c=len(con)
            c+=1
            cur.execute("INSERT INTO contains VALUES(%s,'DEBIT','FLIGHT',%s,%s)",(cur_user,detail[1],c))
            mydb.commit()
            cur.execute("SELECT * FROM FLIGHTS a,AIRLINE b WHERE a.flight_code=%s and a.airlineid=b.airlineid and 'a'=%s ",(detail[0],a))
            flig=cur.fetchall()
            cur.execute("SELECT * FROM airport WHERE AP_ID=%s and 'a'=%s",(flig[0][1],a))
            sta=cur.fetchall()
            cur.execute("SELECT * FROM airport WHERE AP_ID=%s and 'a'=%s",(flig[0][2],a))
            des=cur.fetchall()
        return render_template('payment_receipt.html',flight=flig,source=sta,dest=des)
    elif request.method == 'GET':
        fro=request.args.get('From')
        to=request.args.get('To')
        if fro!=None and to!=None:
            fro=fro.split(' - ')
            to=to.split(' - ')
            a='a'
            cur=mydb.cursor()
            cur.execute("SELECT * FROM airport WHERE state=%s and 'a'=%s",(fro[0],a))
            sta=cur.fetchall()
            sid=sta[0][0]
            cur.execute("SELECT * FROM airport WHERE state=%s and 'a'=%s",(to[0],a))
            des=cur.fetchall()
            did=des[0][0]
            cur.execute("SELECT * FROM flights WHERE source=%s AND destination=%s",(sid,did))
            flight_ticket=cur.fetchall()
            for i in range(len(flight_ticket)):
                f=list(flight_ticket[i])
                f[1]=sta[0][1]
                f[2]=des[0][1]
                cur.execute("SELECT * FROM airline WHERE AIRLINEID=%s and 'a'=%s",(f[5],a))
                aname=cur.fetchall()
                f[5]=aname[0][1]
                flight_ticket[i]=tuple(f)
            return render_template('flight_index.html',airports=routes,flight_ticket=flight_ticket)

    return render_template('flight_index.html',airports=routes)

@ex.route('/bus_index',methods=['GET','POST'])
def bus():
    global cur_user
    if cur_user=='':
        return redirect('/login')
    cur=mydb.cursor()
    cur.execute("SELECT * FROM bus_route")
    routes=cur.fetchall()
    SOURCE=[]
    DEST=[]
    for i in routes:
        if i[1] not in SOURCE:
            SOURCE.append(i[1])
        if i[2] not in DEST:
            DEST.append(i[2])
    SOURCE.sort()
    DEST.sort()
    if request.method=='POST':
        payment=request.form.get('optradio')
        a='a'
        detail=payment.split('--')
        cur.execute("SELECT * FROM userw WHERE cname=%s and 'a'=%s",(cur_user,a))
        bal=cur.fetchall()
        bal=bal[0][1]
        if int(bal)<int(detail[1]):
            return render_template('bus_index.html',source=SOURCE,desti=DEST,msg="Insufficient balance in account")
        else:
            bal=int(bal)-int(detail[1])
            bal=str(bal)
            cur.execute("UPDATE userw SET bal=%s WHERE cname=%s",(bal,cur_user))
            mydb.commit()
            cur.execute("SELECT * FROM contains WHERE cname=%s and 'a'=%s",(cur_user,a))
            con=cur.fetchall()
            c=len(con)
            c+=1
            cur.execute("INSERT INTO contains VALUES(%s,'DEBIT','BUS',%s,%s)",(cur_user,detail[1],c))
            mydb.commit()
            return render_template('payment.html')
    elif request.method == 'GET':
        fro=request.args.get('From')
        to=request.args.get('To')
        if fro!=None and to!=None:
            cur.execute("SELECT * FROM bus a,bus_route b WHERE a.routeid=b.r_id AND b.src=%s AND b.dest=%s",(fro,to))
            buses=cur.fetchall()
            return render_template('bus_index.html',source=SOURCE,desti=DEST,bus=buses)
    return render_template('bus_index.html',source=SOURCE,desti=DEST)


@ex.route('/train_index',methods=['GET','POST'])
def trains():
    global cur_user
    if cur_user=='':
        return redirect('/login')
    cur=mydb.cursor()
    cur.execute("SELECT city FROM station")
    stations=cur.fetchall()
    STATIONS=[]
    for i in stations:
        if i[0] not in STATIONS:
            STATIONS.append(i[0])
    STATIONS.sort()
    if request.method=='POST':
        payment=request.form.get('optradio')
        a='a'
        detail=payment.split('--')
        cur.execute("SELECT * FROM userw WHERE cname=%s and 'a'=%s",(cur_user,a))
        bal=cur.fetchall()
        bal=bal[0][1]
        if int(bal)<int(detail[1]):
            return render_template('train_index.html',sta=STATIONS,msg="Insufficient balance in account")
        else:
            bal=int(bal)-int(detail[1])
            bal=str(bal)
            cur.execute("UPDATE userw SET bal=%s WHERE cname=%s",(bal,cur_user))
            mydb.commit()
            cur.execute("SELECT * FROM contains WHERE cname=%s and 'a'=%s",(cur_user,a))
            con=cur.fetchall()
            c=len(con)
            c+=1
            cur.execute("INSERT INTO contains VALUES(%s,'DEBIT','TRAIN',%s,%s)",(cur_user,detail[1],c))
            mydb.commit()
            return render_template('payment.html')
    elif request.method == 'GET':
        f=request.args.get('From')
        t=request.args.get('To')
        if f!=None and t!=None:
            a='a'
            cur.execute("SELECT * FROM station WHERE city=%s and 'a'=%s",(f,a))
            sta=cur.fetchall()
            sid=sta[0][0]
            sname=sta[0][1]
            cur.execute("SELECT * FROM station WHERE city=%s and 'a'=%s",(t,a))
            des=cur.fetchall()
            did=des[0][0]
            dname=des[0][1]
            cur.execute("SELECT * FROM train WHERE destination_id=%s and source_id=%s",(did,sid))
            trains=cur.fetchall()
            cur.execute("SELECT * FROM train a,train_stops b WHERE a.train_no=b.train_no")
            jt=cur.fetchall()
            l=[]
            for i in jt:
                for j in jt:
                    if i[0]==j[0] and i[10]==sid and j[10]==did and i[11]<j[11]:
                        t=tuple([i[0],i[1],did,dname,sid,sname,i[6],i[7],i[8]])
                        if t not in trains:
                            trains.append(t)
            return render_template('train_index.html',sta=STATIONS,train=trains)
    return render_template('train_index.html',sta=STATIONS)


@ex.route('/wallet')
def wallet():
    global cur_user
    if cur_user=='':
        return redirect('/login')
    cur=mydb.cursor()
    a='a'
    cur.execute("SELECT * FROM userw WHERE cname=%s and 'a'=%s",(cur_user,a))
    bal=cur.fetchall()
    bal=bal[0][1]
    cur.execute("SELECT * FROM contains WHERE cname=%s and 'a'=%s ORDER BY count DESC",(cur_user,a))
    history=cur.fetchall()
    print(history)
    return render_template('wallet.html',balance=bal,his=history)


@ex.route('/flight-conformation')
def payment_receipt():
    return render_template('payment_receipt.html')

@ex.route('/conformation')
def payment():
    return render_template('payment.html')

if __name__ == '__main__':
    ex.run(debug=True)
