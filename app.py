from mysql.connector import pooling
from datetime import datetime
from flask import Flask, redirect, url_for, request, render_template
import atexit

app = Flask(__name__)


def exit_handler():
    print("My application is ending!")
    mydb = dbConnect()
    if mydb.is_connected():
        mydb.close()
        print("MySQL connection is closed")


atexit.register(exit_handler)


def dbConnect():
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="pynative_pool",
        pool_size=5,
        pool_reset_session=True,
        host="localhost",
        database="starss",
        user="root",
        password="Limatambo77",
    )

    print("Printing connection pool properties ")
    print("Connection Pool Name - ", connection_pool.pool_name)
    print("Connection Pool Size - ", connection_pool.pool_size)

    # Get connection object from a pool
    connection_object = connection_pool.get_connection()

    if connection_object.is_connected():
        db_Info = connection_object.get_server_info()
        print(
            "Connected to MySQL database using connection pool ... MySQL Server version on ",
            db_Info,
        )
        return connection_object


############################################################################################
#################################  FRONT END   #############################################
############################################################################################


@app.route("/")
def home():
    return render_template("home.html")


############################################################################################


@app.route("/prospectiveStudents")
def prospectiveStudents():
    res = render_template(
        "prospectiveStudents/prospectiveStudents.html",
        some="variables",
        you="want",
        toPass=["to", "your", "template"],
    )
    return res


@app.route("/prospectiveStudents/application")
def prospectiveStudentsApplication():
    res = render_template("prospectiveStudents/admissionApplication.html")
    return res


@app.route("/prospectiveStudents/success/<studentID>")
def prospectiveStudentsApplicationSubmitted(studentID):
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM person WHERE userId =%s" % studentID)
    myresult = mycursor.fetchall()
    firstName = myresult[0][1]
    lastName = myresult[0][3]

    res = render_template(
        "prospectiveStudents/applicationSubmitted.html",
        message="Welcome %s %s your Student ID is  %s"
        % (firstName, lastName, studentID),
    )
    return res


@app.route("/prospectiveStudents/checkStatus")
def prospectiveStudentsStatus():
    res = render_template("prospectiveStudents/checkApplicantStatus.html")
    return res

@app.route("/prospectiveStudents/accepted")
def prospectiveStudentAccepted():
    res = render_template("prospectiveStudents/admissionAccepted.html")
    return res    


@app.route("/prospectiveStudents/applicationStatus/<password>")
def applicationStatus(password):
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT applicationStatus FROM application WHERE Applicant_User_userId =%s"
        % password
    )
    myresult = mycursor.fetchall()
    status = myresult[0][0]

    print(status)

    mycursor.execute(
        "SELECT COUNT(*) FROM recomendationletter WHERE Application_idApplication =%s"
        % password
    )
    myresult = mycursor.fetchall()
    count = myresult[0][0]

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT priorTranscript FROM application WHERE Applicant_User_userId =%s"
        % password
    )
    myresult = mycursor.fetchall()
    transcript = myresult[0][0]

    print(transcript)

    statusMessage = ""

    if status == "Accepted":
        return redirect(url_for('prospectiveStudentAccepted'))
    elif status == "Rejected":
        statusMessage = "Your Status is '%s'" % (
            "Your application for admission has been denied."
        )
    elif count == 0:
        statusMessage = "Your Status is '%s'" % (
            "Application Incomplete – recommendation letters materials missing"
        )
    elif not transcript:
        statusMessage = "Your Status is '%s'" % (
            "Application Incomplete – transcript materials missing"
        )
    else:
        statusMessage = "Application Complete and Under Review/No Decision Yet"

    res = render_template(
        "prospectiveStudents/applicationSubmitted.html",
        message=statusMessage,
    )
    return res


############################################################################################


@app.route("/students")
def students():
    res = render_template(
        "students/students.html",
        some="variables",
        you="want",
        toPass=["to", "your", "template"],
    )
    return res


############################################################################################


@app.route("/staff")
def staff():
    res = render_template(
        "staff/staff.html",
        some="variables",
        you="want",
        toPass=["to", "your", "template"],
    )
    return res


############################################################################################


@app.route("/alumni")
def alumni():
    res = render_template(
        "alumni/alumni.html",
        some="variables",
        you="want",
        toPass=["to", "your", "template"],
    )
    return res


############################################################################################
#################################  API   ###################################################
############################################################################################


@app.route("/checkAdmissionApplication", methods=["POST"])
def checkApplicationStatusAPI():
    email = request.form["email"]
    password = request.form["password"]

    return redirect(url_for("applicationStatus", password=password))


@app.route("/studentApply", methods=["POST"])
def studentApplyAPI():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    firstName = request.form["firstName"]
    middleName = request.form["middleName"]
    lastName = request.form["lastName"]
    email = request.form["email"]
    streetAddress = request.form["streetAddress"]
    city = request.form["city"]
    state = request.form["state"]
    zipcode = request.form["zipcode"]
    homePhone = request.form["homePhone"]
    workPhone = request.form["workPhone"]
    mobilePhone = request.form["mobilePhone"]

    program = request.form["program"]
    greScoreVerbal = request.form["greScoreVerbal"]
    priorWorkExperience = request.form["priorWorkExperience"]
    admissionTerm = request.form["admissionTerm"]
    areaOfInterest = request.form["areaOfInterest"]

    if request.form.get("degree1"):
        degree1 = request.form["degree1"]
        print(degree1)
    else:
        degree1 = None
    graduationYear1 = request.form["graduationYear1"]
    gpa1 = request.form["gpa1"]
    collegeName1 = request.form["collegeName1"]

    if request.form.get("degree2"):
        degree2 = request.form["degree2"]
        print(degree2)
    else:
        degree2 = None
    graduationYear2 = request.form["graduationYear2"]
    gpa2 = request.form["gpa2"]
    collegeName2 = request.form["collegeName2"]

    title1 = request.form["title1"]
    name1 = request.form["name1"]
    email1 = request.form["email1"]
    affiliation1 = request.form["affiliation1"]

    title2 = request.form["title2"]
    name2 = request.form["name2"]
    email2 = request.form["email2"]
    affiliation2 = request.form["affiliation2"]

    title3 = request.form["title3"]
    name3 = request.form["name3"]
    email3 = request.form["email3"]
    affiliation3 = request.form["affiliation3"]

    sql = "INSERT INTO person (firstName, middleName, lastName, email, streetAddress, city, state, zipcode, homePhone, workPhone, mobilePhone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (
        firstName,
        middleName,
        lastName,
        email,
        streetAddress,
        city,
        state,
        zipcode,
        homePhone,
        workPhone,
        mobilePhone,
    )
    mycursor.execute(sql, val)
    userID = mycursor.lastrowid
    mydb.commit()

    sql = "INSERT INTO applicant (User_userId) VALUES (%s)"
    val = (userID,)
    mycursor.execute(sql, val)
    mydb.commit()

    mycursor = mydb.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO application (Applicant_User_userId, program, greScoreVerbal, priorWorkExperience, admissionTerm, dateReceived, areaOfInterest) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    val = (
        userID,
        program,
        greScoreVerbal,
        priorWorkExperience,
        admissionTerm,
        timestamp,
        areaOfInterest,
    )
    mycursor.execute(sql, val)
    applicationID = mycursor.lastrowid
    mydb.commit()

    if name1:
        sql = "INSERT INTO recomendationletter (Application_idApplication, Application_Applicant_User_userId, name, affiliation, email, title) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (
            applicationID,
            userID,
            name1,
            affiliation1,
            email1,
            title1,
        )
        mycursor.execute(sql, val)
        mydb.commit()

    if name2:
        sql = "INSERT INTO recomendationletter (Application_idApplication, Application_Applicant_User_userId, name, affiliation, email, title) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (
            applicationID,
            userID,
            name2,
            affiliation2,
            email2,
            title2,
        )
        mycursor.execute(sql, val)
        mydb.commit()

    if name3:
        sql = "INSERT INTO recomendationletter (Application_idApplication, Application_Applicant_User_userId, name, affiliation, email, title) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (
            applicationID,
            userID,
            name3,
            affiliation3,
            email3,
            title3,
        )
        mycursor.execute(sql, val)
        mydb.commit()

    if degree1:
        sql = "INSERT INTO priordegree (Application_idApplication, Application_Applicant_User_userId, collegeName, graduationYear, gpa, degree) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (
            applicationID,
            userID,
            collegeName1,
            graduationYear1,
            gpa1,
            degree1,
        )
        mycursor.execute(sql, val)
        mydb.commit()

    if degree2:
        sql = "INSERT INTO priordegree (Application_idApplication, Application_Applicant_User_userId, collegeName, graduationYear, gpa, degree) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (
            applicationID,
            userID,
            collegeName2,
            graduationYear2,
            gpa2,
            degree2,
        )
        mycursor.execute(sql, val)
        mydb.commit()

    print(mycursor.rowcount, "record inserted.")

    # mycursor.execute("SELECT * FROM person WHERE email ='%s'" % email)

    # myresult = mycursor.fetchall()

    # studentID = myresult[0][0]

    mydb.close()

    return redirect(
        url_for("prospectiveStudentsApplicationSubmitted", studentID=userID)
    )


if __name__ == "__main__":
    app.run(debug=True)
