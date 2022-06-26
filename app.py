from mysql.connector import (connection)
from datetime import datetime
from flask import Flask, redirect, url_for, request, render_template
from datetime import date
# import atexit

app = Flask(__name__)


# def exit_handler():
#     print("My application is ending!")
#     mydb = dbConnect()
#     if mydb.is_connected():
#         mydb.close()
#         print("MySQL connection is closed")


# atexit.register(exit_handler)


def dbConnect():
    cnx = connection.MySQLConnection(user='root', password='Limatambo77',
                              host='localhost',
                              database='starss4')
    return cnx

    # connection_pool = pooling.MySQLConnectionPool(
    #     pool_name="pynative_pool",
    #     pool_size=32,
    #     pool_reset_session=True,
    #     host="localhost",
    #     database="starss",
    #     user="root",
    #     password="Limatambo77",
    # )

    # print("Printing connection pool properties ")
    # print("Connection Pool Name - ", connection_pool.pool_name)
    # print("Connection Pool Size - ", connection_pool.pool_size)

    # # Get connection object from a pool
    # connection_object = connection_pool.get_connection()

    # if connection_object.is_connected():
    #     db_Info = connection_object.get_server_info()
    #     print(
    #         "Connected to MySQL database using connection pool ... MySQL Server version on ",
    #         db_Info,
    #     )
    #     return connection_object


############################################################################################
#################################  FRONT END   #############################################
############################################################################################


@app.route("/")
def home():
    return render_template("home.html")


############################################################################################

@app.route("/person/modify", methods=["POST"])
def modifyInfo():
    userId = request.form["userId"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM person  WHERE person.userId=%s;" % userId
    )
    personalInfo = mycursor.fetchall()
    mydb.close()

    previousUrl = request.referrer
    
    res = render_template(
        "modfyPersonalInfo.html", personalInfo=personalInfo, previousUrl=previousUrl
    )

    return res  

@app.route("/person/updateInfo", methods=["POST"])
def updateInfo():
    previousUrl = request.form["previousUrl"]
    userId = request.form["userId"]
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

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE person SET firstName = %s, middleName = %s, lastName = %s, email = %s, streetAddress = %s, city = %s, state = %s, zipcode = %s, homePhone = %s, workPhone = %s, mobilePhone = %s WHERE (userId = %s)"
    valTranscript = (firstName, middleName, lastName, email, streetAddress, city, state, zipcode, homePhone, workPhone, mobilePhone, userId)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()
    mydb.close()

    return redirect(previousUrl)

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
    mydb.close()
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
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT User_userId, firstName, lastName, email, password FROM applicant INNER JOIN person ON person.userId = applicant.User_userId;;"
    )
    applicants = mycursor.fetchall()
    mydb.close()


    res = render_template("prospectiveStudents/checkApplicantStatus.html", applicants=applicants)
    return res

@app.route("/prospectiveStudents/accepted")
def prospectiveStudentAccepted():
    id=request.args.get('id')
    userId=request.args.get('userId')

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT status FROM student WHERE User_userId =%s"
        % userId
    )
    myresult = mycursor.fetchall()
    mydb.close()
    status = myresult[0][0]

    print(status)

    res = render_template("prospectiveStudents/admissionAccepted.html",id=id, userId=userId, status=status)
    return res 

@app.route("/prospectiveStudents/accept", methods=["POST"])
def acceptAdmission():
    id = request.form["idApplication"]
    studentID = request.form["idUser"]
    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE student SET status = %s WHERE User_userId = %s"
    valTranscript = (1,studentID)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()
    mydb.close()

    return redirect(url_for("home"))
      


@app.route("/prospectiveStudents/applicationStatus/<password>")
def applicationStatus(password):
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT applicationStatus, idApplication, applicationDecision, Applicant_User_userId FROM application WHERE Applicant_User_userId =%s"
        % password
    )
    myresult = mycursor.fetchall()
    status = myresult[0][0]
    idApplication = myresult[0][1]
    applicationDecision = myresult[0][2]
    Applicant_User_userId = myresult[0][3]

    print(status)

    mycursor.execute(
        "SELECT COUNT(*) FROM recomendationletter WHERE Application_idApplication =%s"
        % idApplication
    )
    myresult = mycursor.fetchall()
    count = myresult[0][0]

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT priorTranscript FROM application WHERE idApplication =%s"
        % idApplication
    )
    myresult = mycursor.fetchall()
    mydb.close()
    transcript = myresult[0][0]

    statusMessage = ""

    if status == "Accepted":
        return redirect(url_for('prospectiveStudentAccepted', id=idApplication, userId=Applicant_User_userId))
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
    elif applicationDecision == "reject":
        statusMessage = "Your Status is '%s'" % (
            "Admission Decision: Rejected"
        ) 
    elif applicationDecision == "admit":
        statusMessage = "Your Status is '%s'" % (
            "Admission Decision: Accepted"
        )
    elif applicationDecision == "admitWithAid":
            statusMessage = "Your Status is '%s'" % (
            "Admission Decision: Accepted"
        )               
    else:
        statusMessage = "Application Complete and Under Review/No Decision Yet"

    mydb.close()

    res = render_template(
        "prospectiveStudents/applicationSubmitted.html",
        message=statusMessage,
    )
    return res


############################################################################################


@app.route("/students")
def students():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT User_userId, firstName, lastName, email, password FROM student INNER JOIN person ON student.User_userId = person.userId WHERE status = 1;"
    )
    activeStudents = mycursor.fetchall()

    res = render_template(
        "students/students.html",
        activeStudents=activeStudents
    )
    return res

@app.route("/students/studentLogin", methods=["POST"])
def studentLogin():
    email = request.form["email"]
    password = request.form["password"]

    return redirect(url_for("student", password=password))  

@app.route("/students/student/<password>")
def student(password):
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT p.userId, p.firstName, p.middleName, p.lastName , p.homePhone, p.workPhone, p.mobilePhone, p.email, p.streetAddress, p.city, p.state, p.zipcode FROM student s INNER JOIN person p ON s.User_userId = p.userId WHERE s.User_userId =%s;"
        % password
    )
    personalInfo = mycursor.fetchall()
    mydb.close()

    res = render_template(
        "students/student.html", personalInfo=personalInfo, password=password
    )
    return res

@app.route("/students/degreeCourses", methods=["POST"])
def degreeCourses():
    studentId = request.form["studentId"]


    print('studentId')
    print(studentId)
    print('studentId')

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT c.courseNumber, c.title, c.credits FROM department_has_course dc INNER JOIN course c ON dc.Course_courseNumber=c.courseNumber where dc.Department_idDepartment IN ((SELECT Department_idDepartment FROM department_has_student WHERE Student_User_userId=%s));" % studentId
    )
    degreeCourses = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT c.courseNumber FROM department_has_course dc INNER JOIN course c ON dc.Course_courseNumber=c.courseNumber where dc.Department_idDepartment IN ((SELECT Department_idDepartment FROM department_has_student WHERE Student_User_userId=%s));" % studentId
    )
    degreeCoursesRemove = mycursor.fetchall()
    mydb.close()
    

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT Course_courseNumber FROM student_has_course WHERE Student_User_userId=%s;" % studentId
    )
    studentCourses = mycursor.fetchall()
    mydb.close()


    x = []
    y = []

    for a in degreeCoursesRemove:
        x.append(a[0])

    for a in studentCourses:
            y.append(a[0])    
    

    for i in range(0, len(x)):
        for j in range(0, len(y)):
            if x[i]==y[j]:
                print('Hola');
                x[i]='added'
    
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber WHERE sc.Student_User_userId=%s;" % studentId
    )
    credits = mycursor.fetchall()
    mydb = dbConnect()
    mydb.close()

    totalCredits = credits[0][0]

    if totalCredits is None:
        totalCredits = 0

    previousUrl = request.referrer

    print(previousUrl)

    print(degreeCourses)
    print(len(degreeCourses))

    print("Remover")
    print(x)
    print(len(x))
    print("Remover")

    res = render_template(
        "students/degreeCourses.html", degreeCourses=degreeCourses, studentId=studentId, totalCredits=totalCredits, remover=x, previousUrl=previousUrl
    )

    return res

@app.route("/students/modifyDegreeCourses", methods=["POST"])
def modifyDegreeCourses():
    studentId = request.form["studentId"]
    courseNumber = request.form["courseNumber"]
    action = request.form["action"]
    action = request.form["action"]
    previousUrl = request.form["previousUrl"]

    print('HHHHHHH')
    print(previousUrl)

    if action == 'Add':
        print('=========================');
        print('ADDED');
        mydb = dbConnect()
        mycursor = mydb.cursor()
        sql = "INSERT INTO student_has_course (Student_User_userId, Course_courseNumber) VALUES (%s,%s)"
        val = (studentId, courseNumber)
        mycursor.execute(sql, val)
        mydb.commit()
    elif action == 'Remove':
        print('=========================');
        print('REMOVED');
        mydb = dbConnect()
        mycursor = mydb.cursor()
        sql = "DELETE FROM student_has_course WHERE (Student_User_userId = %s) and (Course_courseNumber = %s)"
        valTranscript = (studentId, courseNumber)
        mycursor.execute(sql,valTranscript)
        mydb.commit()


    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT c.courseNumber, c.title, c.credits FROM department_has_course dc INNER JOIN course c ON dc.Course_courseNumber=c.courseNumber where dc.Department_idDepartment IN ((SELECT Department_idDepartment FROM department_has_student WHERE Student_User_userId=%s));" % studentId
    )
    degreeCourses = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT c.courseNumber FROM department_has_course dc INNER JOIN course c ON dc.Course_courseNumber=c.courseNumber where dc.Department_idDepartment IN ((SELECT Department_idDepartment FROM department_has_student WHERE Student_User_userId=%s));" % studentId
    )
    degreeCoursesRemove = mycursor.fetchall()
    mydb.close()
    

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT Course_courseNumber FROM student_has_course WHERE Student_User_userId=%s;" % studentId
    )
    studentCourses = mycursor.fetchall()
    mydb.close()


    x = []
    y = []

    for a in degreeCoursesRemove:
        x.append(a[0])

    for a in studentCourses:
            y.append(a[0])    
    

    for i in range(0, len(x)):
        for j in range(0, len(y)):
            if x[i]==y[j]:
                x[i]='added'

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber WHERE sc.Student_User_userId=%s;" % studentId
    )
    credits = mycursor.fetchall()
    totalCredits = credits[0][0]

    if totalCredits is None:
        totalCredits = 0

    res = render_template(
        "students/degreeCourses.html", degreeCourses=degreeCourses, studentId=studentId, totalCredits=totalCredits, remover=x, previousUrl=previousUrl
    )

    return res

@app.route("/students/enrollCourses", methods=["POST"])
def enrollCourses():
    studentId = request.form["studentId"]

    print(studentId)

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT s.sectionNumber, s.year, s.semester, c.courseNumber, c.title, c.credits, p.firstName, p.lastName, sc.Student_User_userId, s.Instructor_Staff_Person_userId  FROM student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId WHERE sc.Student_User_userId=%s;" % studentId
    )
    enrollCourses = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT s.sectionNumber FROM student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId WHERE sc.Student_User_userId=%s;" % studentId
    )
    enrollCoursesRemove = mycursor.fetchall()
    mydb.close()


    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT Section_sectionNumber FROM section_has_student WHERE section_has_student.Student_User_userId=%s;" % studentId
    )
    studentSection = mycursor.fetchall()
    mydb.close()

    x = []
    y = []

    for a in enrollCoursesRemove:
        x.append(a[0])

    for a in studentSection:
            y.append(a[0])    
    
    for i in range(0, len(x)):
        for j in range(0, len(y)):
            if x[i]==y[j]:
                x[i]='added'

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM section_has_student ss INNER JOIN course c ON ss.Section_Course_courseNumber=c.courseNumber WHERE ss.Student_User_userId=%s;" % studentId
    )
    credits = mycursor.fetchall()
    mydb.close()
    totalCredits = credits[0][0]

    if totalCredits is None:
        totalCredits = 0

    previousUrl = request.referrer

    res = render_template(
        "students/enrollCourses.html", enrollCourses=enrollCourses, studentId=studentId, totalCredits=totalCredits, remover=x, previousUrl=previousUrl
    )

    return res   

@app.route("/students/modifyEnroll", methods=["POST"])
def modifyEnroll():
    studentId = request.form["studentId"]
    courseNumber = request.form["courseNumber"]
    sectionNumber = request.form["sectionNumber"]
    instructorId = request.form["instructorId"]
    semester = request.form["semester"]
    year = request.form["year"]
    action = request.form["action"]
    previousUrl = request.form["previousUrl"]

    if action == 'Register':
        mydb = dbConnect()
        mycursor = mydb.cursor()
        sql = "INSERT INTO section_has_student (Student_User_userId, Section_sectionNumber, Section_Course_courseNumber, Section_Instructor_Staff_Person_userId, grade, Section_year, Section_semester) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        print(sql)
        val = (studentId, sectionNumber, courseNumber, instructorId, 'In Progress',year,semester)
        print(val)
        mycursor.execute(sql, val)
        mydb.commit()
        mydb.close()
    elif action == 'Drop':
        mydb = dbConnect()
        mycursor = mydb.cursor()
        sql = "DELETE FROM section_has_student WHERE (Student_User_userId = %s) and (Section_sectionNumber = %s) and (Section_Course_courseNumber = %s) and (Section_Instructor_Staff_Person_userId = %s)  and (Section_year = %s  and (Section_semester = %s"
        valTranscript = (studentId, sectionNumber, courseNumber, instructorId, year, semester)
        mycursor.execute(sql,valTranscript)
        mydb.commit()
        mydb.close()


    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT s.sectionNumber, s.year, s.semester, c.courseNumber, c.title, c.credits, p.firstName, p.lastName, sc.Student_User_userId, s.Instructor_Staff_Person_userId  FROM student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId WHERE sc.Student_User_userId=%s;" % studentId
    )
    enrollCourses = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT s.sectionNumber FROM student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId WHERE sc.Student_User_userId=%s;" % studentId
    )
    enrollCoursesRemove = mycursor.fetchall()
    mydb.close()


    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT Section_sectionNumber FROM section_has_student WHERE section_has_student.Student_User_userId=%s;" % studentId
    )
    studentSection = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM section_has_student ss INNER JOIN course c ON ss.Section_Course_courseNumber=c.courseNumber WHERE ss.Student_User_userId=%s;" % studentId
    )
    credits = mycursor.fetchall()
    mydb.close()
    totalCredits = credits[0][0]

    x = []
    y = []

    for a in enrollCoursesRemove:
        x.append(a[0])

    for a in studentSection:
            y.append(a[0])    
    
    for i in range(0, len(x)):
        for j in range(0, len(y)):
            if x[i]==y[j]:
                x[i]='added'

    if totalCredits is None:
        totalCredits = 0

    res = render_template(
        "students/enrollCourses.html", enrollCourses=enrollCourses, studentId=studentId, totalCredits=totalCredits, remover=x, previousUrl=previousUrl
    )

    return res

@app.route("/students/viewGrades", methods=["POST"])
def viewGrades():
    studentId = request.form["studentId"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT DISTINCT s.sectionNumber, s.year, s.semester, c.courseNumber, c.title, c.credits, p.firstName, p.lastName, ss.Student_User_userId, s.Instructor_Staff_Person_userId, ss.grade  FROM student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId LEFT JOIN section_has_student ss ON ss.Section_sectionNumber=s.sectionNumber  WHERE ss.Student_User_userId=%s;" % studentId
    )
    courses = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM section_has_student ss INNER JOIN course c ON ss.Section_Course_courseNumber=c.courseNumber WHERE ss.Student_User_userId=%s AND ss.grade <> 'In Progress';" % studentId
    )
    credits = mycursor.fetchall()
    mydb.close()
    totalCredits = credits[0][0]

    if totalCredits is None:
        totalCredits = 0

    previousUrl = request.referrer

    print(previousUrl)

    res = render_template(
        "students/viewGrades.html", courses=courses, studentId=studentId, totalCredits=totalCredits, previousUrl=previousUrl
    )

    return res    

@app.route("/students/applyGraduation", methods=["POST"])
def applyGraduation():
    studentId = request.form["studentId"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT avg(g.gradeNo) FROM section_has_student ss INNER JOIN gradeconversion g ON ss.grade=g.grade where ss.Student_User_userId=%s AND ss.grade <> 'In Progress';" % studentId
    )
    my_list = mycursor.fetchall()
    mydb.close()

    message='Graduate Application Denied: '

    if my_list[0][0] != None:
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT avg(g.gradeNo) FROM section_has_student ss INNER JOIN gradeconversion g ON ss.grade=g.grade where ss.Student_User_userId=%s AND ss.grade <> 'In Progress';" % studentId
        )
        my_list = mycursor.fetchall()
        mydb.close()

        gpa=my_list[0][0]

        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT COUNT(ss.grade) FROM section_has_student ss INNER JOIN course c ON ss.Section_Course_courseNumber=c.courseNumber WHERE ss.Student_User_userId=%s AND ss.grade IN ('C','F');" % studentId
        )
        my_list = mycursor.fetchall()
        mydb.close()

        badGrades = my_list[0][0]

        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT SUM(c.credits) FROM section_has_student ss INNER JOIN course c ON ss.Section_Course_courseNumber=c.courseNumber WHERE ss.Student_User_userId=%s AND ss.grade <> 'In Progress';" % studentId
        )
        my_list = mycursor.fetchall()
        mydb.close()

        accumulatedCredits = my_list[0][0]

        
        flag=True
        if (gpa<3.0):
            flag=False
            message=message+"| GPA: '%s' less than 3.0 |" % (gpa)
            mydb = dbConnect()
            mycursor = mydb.cursor()
            sql = "INSERT ignore INTO graduateapplication (status, Student_User_userId) VALUES (%s,%s)"
            val = ('Not Cleared', studentId)
            mycursor.execute(sql, val)
            mydb.commit()
            mydb.close()
        if (badGrades>2):
            flag=False
            message=message+"| More than '%s' Grades below B, Only 2 allowed |" % (badGrades)
            mydb = dbConnect()
            mycursor = mydb.cursor()
            sql = "INSERT ignore INTO graduateapplication (status, Student_User_userId) VALUES (%s,%s)"
            val = ('Not Cleared', studentId)
            mycursor.execute(sql, val)
            mydb.commit()
            mydb.close()
        if (accumulatedCredits < 30):
            flag=False
            message=message+"| Accumulated '%s', at least 30 is required |" % (accumulatedCredits)
            mydb = dbConnect()
            mycursor = mydb.cursor()
            sql = "INSERT ignore INTO graduateapplication (status, Student_User_userId) VALUES (%s,%s)"
            val = ('Not Cleared', studentId)
            mycursor.execute(sql, val)
            mydb.commit()
            mydb.close()

        if (flag==True):
            message="Your are cleared for graduation, you application has been submitted for Approval!"
            mydb = dbConnect()
            mycursor = mydb.cursor()
            sql = "INSERT ignore INTO graduateapplication (status, Student_User_userId) VALUES (%s,%s)"
            val = ('Cleared', studentId)
            mycursor.execute(sql, val)
            mydb.commit()
            mydb.close()

    else:
        message=message+"You are not enrolled into courses or you are not graded yet"
        print('A')
        mydb = dbConnect()
        mycursor = mydb.cursor()
        sql = "INSERT ignore INTO graduateapplication (status, Student_User_userId) VALUES (%s,%s)"
        val = ('Not Cleared', studentId)
        mycursor.execute(sql, val)
        mydb.commit()
        mydb.close()
        print('B')

    res = render_template(
         "students/graduateApplication.html", message=message
    )

    return res       

############################################################################################


@app.route("/staff")
def staff():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT staff.Person_userId as personId, person.email as email, CASE WHEN instructor.Staff_Person_userId IS NOT NULL THEN 'YES' END as instructor, CASE WHEN advisor.Staff_Person_userId IS NOT NULL THEN 'YES' END as advisor, CASE WHEN reviewer.Staff_Person_userId IS NOT NULL THEN 'YES' END as reviewer, CASE WHEN gs.Staff_Person_userId IS NOT NULL THEN 'YES' END as gs FROM staff INNER JOIN person ON staff.Person_userId=person.userId LEFT JOIN gs ON staff.Person_userId=gs.Staff_Person_userId LEFT JOIN instructor ON staff.Person_userId=instructor.Staff_Person_userId LEFT JOIN advisor ON staff.Person_userId=advisor.Staff_Person_userId LEFT JOIN reviewer ON staff.Person_userId=reviewer.Staff_Person_userId;"
    )
    staff = mycursor.fetchall()
    mydb.close()

    res = render_template(
        "staff/staff.html",
        staff=staff
    )
    return res

@app.route("/staff/staffLogin", methods=["POST"])
def staffLogin():
    email = request.form["email"]
    password = request.form["password"]

    previousUrl = request.referrer

    return redirect(url_for("staffPage", password=password)) 

@app.route("/staff/staff/<password>")
def staffPage(password):
    print(password)
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT staff.Person_userId as personId, CASE WHEN instructor.Staff_Person_userId IS NOT NULL THEN 'YES' END as instructor, CASE WHEN advisor.Staff_Person_userId IS NOT NULL THEN 'YES' END as advisor, CASE WHEN reviewer.Staff_Person_userId IS NOT NULL THEN 'YES' END as reviewer, CASE WHEN gs.Staff_Person_userId IS NOT NULL THEN 'YES' END as gs FROM staff LEFT JOIN gs ON staff.Person_userId=gs.Staff_Person_userId LEFT JOIN instructor ON staff.Person_userId=instructor.Staff_Person_userId LEFT JOIN advisor ON staff.Person_userId=advisor.Staff_Person_userId LEFT JOIN reviewer ON staff.Person_userId=reviewer.Staff_Person_userId WHERE staff.Person_userId=%s;"
        % password
    )
    roles = mycursor.fetchall()
    mydb.close()

    # mydb = dbConnect()
    # mycursor = mydb.cursor()
    # mycursor.execute(
    #     "SELECT a.graduationYear, ac.gpa, d.name FROM alumni a INNER JOIN alumni_has_academics aa ON a.Person_userId=aa.academics_Student_User_userId INNER JOIN academics ac ON aa.academics_Student_User_userId=ac.Student_User_userId INNER JOIN department d ON ac.program=d.idDepartment WHERE a.Person_userId =%s;"
    #     % password
    # )
    # academics = mycursor.fetchall()
    # mydb.close()

    print(roles)
    previousUrl = request.referrer

    res = render_template(
        "staff/staffPage.html", roles=roles, previousUrl=previousUrl, password=password
    )
    return res

@app.route("/staff/viewAdvisees", methods=["POST"])
def viewAdvisees():
    userId = request.form["userId"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT ad_st.Student_User_userId FROM advisor a INNER JOIN advisor_has_student ad_st ON a.Staff_Person_userId=ad_st.Advisor_Staff_Person_userId WHERE a.Staff_Person_userId=%s;" % userId
    )
    advisees = mycursor.fetchall()
    mydb.close()

    res = render_template(
        "staff/advisees.html", advisees=advisees, previousUrl = request.referrer
    )

    return res

@app.route("/staff/viewApplication", methods=["POST"])
def viewApplication():
    studentId = request.form["studentId"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM application where Applicant_User_userId=%s;" % studentId
    )
    application = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM person WHERE person.userId=%s;" % studentId
    )
    personalInfo = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM recomendationletter WHERE Application_Applicant_User_userId=%s;" % studentId
    )
    recommendations = mycursor.fetchall()
    mydb.close()


    res = render_template(
        "prospectiveStudents/admissionApplicationView.html", application=application[0], personalInfo=personalInfo[0], recommendations=recommendations
    )

    return res


@app.route("/staff/changeAdvisor", methods=["POST"])
def changeAdvisor():
    if request.form.get("studentID"):
        studentID = request.form["studentID"]
        print(studentID)
    else:
        advisorID = None
    if request.form.get("advisorID"):
        advisorID = request.form["advisorID"]
        print(advisorID)
    else:
        program = None

    mydb = dbConnect()
    mycursor = mydb.cursor()
    # sql = "INSERT INTO advisor_has_student (Advisor_Staff_Person_userId, Student_User_userId) VALUES (%s,%s) ON DUPLICATE KEY UPDATE Advisor_Staff_Person_userId=%s, Student_User_userId=%s"
    sql = "UPDATE advisor_has_student SET Advisor_Staff_Person_userId = %s WHERE Student_User_userId = %s"
    # val = (advisorID, studentID,advisorID, studentID)
    val = (advisorID, studentID)
    mycursor.execute(sql, val)
    mydb.commit()   

    return 'res'

@app.route("/staff/statistics", methods=["POST"])
def statistics():
    if request.form.get("term"):
        term = request.form["term"]
        print(term)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT AVG((application.greScoreVerbal + application.greScoreQuantitative + application.greScoreAnalytical)/3) AS average FROM application WHERE application.admissionTerm=\"%s\";" % term
        )
        my_list = mycursor.fetchall()
        gre=my_list[0][0]

        print(gre)

        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT COUNT(*) FROM application WHERE application.applicationDecision = 'reject' AND application.admissionTerm=\"%s\";" % term
        )
        my_list = mycursor.fetchall()
        rejectCount=my_list[0][0]

        print(rejectCount)

        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT COUNT(*) FROM application WHERE applicationDecision = 'admit' AND application.admissionTerm=\"%s\";" % term
        )
        my_list = mycursor.fetchall()
        admitCount=my_list[0][0]


        return render_template('staff/statistics.html', gre=gre, rejectCount=rejectCount, admitCount=admitCount, column='program', filter=term)
    else:
        program = None
    if request.form.get("program"):
        program = request.form["program"]
        print(program)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT AVG((application.greScoreVerbal + application.greScoreQuantitative + application.greScoreAnalytical)/3) AS average FROM application WHERE application.program=\"%s\";" % program
        )
        my_list = mycursor.fetchall()
        gre=my_list[0][0]

        print(gre)

        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT COUNT(*) FROM application WHERE application.applicationDecision = 'admit' AND application.program=\"%s\";" % program
        )
        my_list = mycursor.fetchall()
        rejectCount=my_list[0][0]

        print(rejectCount)

        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT COUNT(*) FROM application WHERE applicationDecision = 'admit' AND application.program=\"%s\";" % program
        )
        my_list = mycursor.fetchall()
        admitCount=my_list[0][0]

        print(admitCount)

        return render_template('staff/statistics.html', gre=gre, rejectCount=rejectCount, admitCount=admitCount, column='program', filter=program)
    else:
        program = None


@app.route("/staff/alumniList", methods=["POST"])
def alumniList():
    if request.form.get("term"):
        term = request.form["term"]
        print(term)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT alumni.Person_userId, person.email, alumni.graduationYear, application.admissionTerm, application.program FROM alumni INNER JOIN person ON alumni.Person_userId=person.userId INNER JOIN application ON application.Applicant_User_userId=alumni.Person_userId WHERE application.admissionTerm=\"%s\";" % term
        )
        my_list = mycursor.fetchall()
        print(my_list)    
        return render_template('staff/admittedApplicants.html', my_list=my_list)
    else:
        program = None
    if request.form.get("program"):
        program = request.form["program"]
        print(program)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT alumni.Person_userId, person.email, alumni.graduationYear, application.admissionTerm, application.program FROM alumni INNER JOIN person ON alumni.Person_userId=person.userId INNER JOIN application ON application.Applicant_User_userId=alumni.Person_userId WHERE application.program=\"%s\";" % program
        )
        my_list = mycursor.fetchall()
        print(my_list)    
        return render_template('staff/alumniList.html', my_list=my_list)
    else:
        program = None


@app.route("/staff/currentStudents", methods=["POST"])
def currentStudents():
    if request.form.get("term"):
        term = request.form["term"]
        print(term)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT student.User_userId FROM student INNER JOIN application ON application.Applicant_User_userId=student.User_userId WHERE student.status=1 AND application.admissionTerm=\"%s\";" % term
        )
        my_list = mycursor.fetchall()
        print(my_list)    
        return render_template('staff/currentStudents.html', my_list=my_list)
    else:
        program = None
    if request.form.get("program"):
        program = request.form["program"]
        print(program)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT student.User_userId FROM student INNER JOIN application ON application.Applicant_User_userId=student.User_userId WHERE student.status=1 AND application.program=\"%s\";" % program
        )
        my_list = mycursor.fetchall()
        print(my_list)    
        return render_template('staff/currentStudents.html', my_list=my_list)
    else:
        program = None
          

@app.route("/staff/admittedStudents", methods=["POST"])
def admittedStudents():
    if request.form.get("term"):
        term = request.form["term"]
        print(term)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT Applicant_User_userId, idApplication, dateReceived, admissionTerm, program  FROM application WHERE (applicationDecision = 'admit' OR applicationDecision = 'admitWithAid') AND admissionTerm=\"%s\";" % term
        )
        my_list = mycursor.fetchall()
        print(my_list)    
        return render_template('staff/admittedApplicants.html', my_list=my_list)
    else:
        program = None
    if request.form.get("program"):
        program = request.form["program"]
        print(program)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT Applicant_User_userId, idApplication, dateReceived, admissionTerm, program  FROM application WHERE (applicationDecision = 'admit' OR applicationDecision = 'admitWithAid') AND program=\"%s\";" % program
        )
        my_list = mycursor.fetchall()
        print(my_list)    
        return render_template('staff/admittedApplicants.html', my_list=my_list)
    else:
        program = None
    

@app.route("/staff/graduateApplicants", methods=["POST"])
def graduateApplicants():
    if request.form.get("term"):
        term = request.form["term"]
        print(term)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT ga.Student_User_userId, p.firstName, p.lastName, ds.Department_idDepartment, ga.status, a.admissionTerm FROM graduateapplication ga INNER JOIN person p ON ga.Student_User_userId=p.userId INNER JOIN department_has_student ds ON ga.Student_User_userId=ds.Student_User_userId INNER JOIN application a ON ds.Student_User_userId=a.Applicant_User_userId WHERE (ga.status <> 'Cleared' OR ga.status <> 'Graduated') AND a.admissionTerm=\"%s\";" % term
        )
        students = mycursor.fetchall()
        print(students)    
        return render_template('staff/graduateStudentApplicants2.html', students=students)
    else:
        program = None
    if request.form.get("program"):
        program = request.form["program"]
        print(program)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT ga.Student_User_userId, p.firstName, p.lastName, ds.Department_idDepartment, ga.status, a.admissionTerm FROM graduateapplication ga INNER JOIN person p ON ga.Student_User_userId=p.userId INNER JOIN department_has_student ds ON ga.Student_User_userId=ds.Student_User_userId INNER JOIN application a ON ds.Student_User_userId=a.Applicant_User_userId WHERE (ga.status <> 'Cleared' OR ga.status <> 'Graduated') AND ds.Department_idDepartment=\"%s\";" % program
        )
        students = mycursor.fetchall()
        print(students)    
        return render_template('staff/graduateStudentApplicants2.html', students=students)
    else:
        program = None

@app.route("/staff/graduateApplicantsCleared", methods=["POST"])
def graduateApplicantsCleared():
    if request.form.get("term"):
        term = request.form["term"]
        print(term)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT ga.Student_User_userId, p.firstName, p.lastName, ds.Department_idDepartment, ga.status, a.admissionTerm FROM graduateapplication ga INNER JOIN person p ON ga.Student_User_userId=p.userId INNER JOIN department_has_student ds ON ga.Student_User_userId=ds.Student_User_userId INNER JOIN application a ON ds.Student_User_userId=a.Applicant_User_userId WHERE (ga.status = 'Cleared') AND a.admissionTerm=\"%s\";" % term
        )
        students = mycursor.fetchall()
        print(students)    
        return render_template('staff/graduateStudentApplicants2.html', students=students)
    else:
        program = None
    if request.form.get("program"):
        program = request.form["program"]
        print(program)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
        "SELECT ga.Student_User_userId, p.firstName, p.lastName, ds.Department_idDepartment, ga.status, a.admissionTerm FROM graduateapplication ga INNER JOIN person p ON ga.Student_User_userId=p.userId INNER JOIN department_has_student ds ON ga.Student_User_userId=ds.Student_User_userId INNER JOIN application a ON ds.Student_User_userId=a.Applicant_User_userId WHERE (ga.status = 'Cleared') AND ds.Department_idDepartment=\"%s\";" % program
        )
        students = mycursor.fetchall()
        print(students)    
        return render_template('staff/graduateStudentApplicants2.html', students=students)
    else:
        program = None        

@app.route("/staff/searchApplicant", methods=["POST"])
def searchApplicant():
    if request.form.get("id"):
        studentId = request.form["id"]
        print(studentId)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT Applicant_User_userId, idApplication, dateReceived, priorTranscript, applicationStatus FROM person INNER JOIN application ON person.userId=application.Applicant_User_userId WHERE person.userId=%s;" % studentId
        )
        myresult = mycursor.fetchall()
        mydb.close()  
    else:
        program = None
    if request.form.get("lastname"):
        lastname = request.form["lastname"]
        print(lastname)
        mydb = dbConnect()
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT Applicant_User_userId, idApplication, dateReceived, priorTranscript, applicationStatus FROM person INNER JOIN application ON person.userId=application.Applicant_User_userId WHERE person.lastName=\"%s\";" % lastname
        )
        myresult = mycursor.fetchall()
        mydb.close()
    else:
        lastname = None

    return render_template('staff/gcUpdateApplications.html', my_list=myresult)
   

@app.route("/staff/finalDecisionApplications")
def finalDecisionApplications():
    mydb = dbConnect()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT DISTINCT idApplication FROM application INNER JOIN applicationrecommendation ON application.idApplication = applicationrecommendation.Application_idApplication WHERE application.applicationDecision IS NULL;"
    )
    reviewedApplications = mycursor.fetchall()

    print(reviewedApplications)

    args = [] 
     
    for reviewedApplication in reviewedApplications:
        args.append(reviewedApplication[0])
    
    if len(args) > 0:
        sql="SELECT Applicant_User_userId, idApplication, dateReceived, priorTranscript FROM application WHERE idApplication IN (%s) AND applicationStatus ='Complete'"
        in_p=', '.join(list(map(lambda x: '%s', args)))
        sql = sql % in_p
        mycursor.execute(sql, args)
        finalApplications = mycursor.fetchall()
    else:
        finalApplications = []

    print(finalApplications)

    return render_template('staff/finalDecisionApplications.html', application=finalApplications)

@app.route("/staff/formallyAdmitApplicants")
def formallyAdmitApplicants():
    mydb = dbConnect()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM application where applicationDecision IN ('admit','admitWithAid') AND applicationStatus <> 'Accepted';"
    )
    admitedApplications = mycursor.fetchall()

    print(admitedApplications)

    return render_template('staff/formallyAdmitApplicants.html', application=admitedApplications)

@app.route("/staff/formallyAdmitApplicantsForm/<id>")
def formallyAdmitApplicantsForm(id):
 
    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE application SET applicationStatus = %s WHERE idApplication = %s"
    valTranscript = ('Accepted', id)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT Applicant_User_userId, program, admissionTerm FROM application where idApplication = %s" % id
    )
    application = mycursor.fetchall()

    applicationUserId=application[0][0]
    program=application[0][1]
    term=application[0][2]

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT Advisor_Staff_Person_userId FROM applicationrecommendation where Application_idApplication = %s" % id
    )
    applicationrecommendation = mycursor.fetchall()

    advisorId=applicationrecommendation[0][0]


    mycursor = mydb.cursor()
    sql = "INSERT INTO student (User_userId, status) VALUES (%s,%s)"
    val = (applicationUserId, 0)
    mycursor.execute(sql, val)
    mydb.commit()

    mycursor = mydb.cursor()
    sql = "INSERT INTO department_has_student (Student_User_userId, Department_idDepartment) VALUES (%s,%s)"
    val = (applicationUserId, program)
    mycursor.execute(sql, val)
    mydb.commit()

    mycursor = mydb.cursor()
    sql = "INSERT INTO advisor_has_student (Advisor_Staff_Person_userId, Student_User_userId) VALUES (%s,%s)"
    val = (advisorId, applicationUserId)
    mycursor.execute(sql, val)
    mydb.commit()

    mycursor = mydb.cursor()
    sql = "INSERT INTO academics (program, term, Student_User_userId) VALUES (%s,%s,%s)"
    val = (program, term, applicationUserId)
    mycursor.execute(sql, val)
    mydb.commit()


    return redirect(
        url_for("formallyAdmitApplicants")
    )

@app.route("/staff/finalDecisionForm/<id>")
def finalDecisionForm(id):
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM application WHERE idApplication =%s"
        % id
    )
    application = mycursor.fetchall()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM priordegree WHERE Application_idApplication =%s"
        % id
    )
    priordegree = mycursor.fetchall()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM recomendationletter WHERE Application_idApplication =%s"
        % id
    )
    recommendations = mycursor.fetchall()

    print(application)

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM person WHERE userId =%s"
        % application[0][1]
    )
    person = mycursor.fetchall()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM applicationrecommendation WHERE Application_idApplication =%s"
        % id
    )
    applicationrecommendation = mycursor.fetchall()

    return render_template('staff/finalDecisionApplication.html', person=person, application=application, priordegree=priordegree, recommendations=recommendations, applicationrecommendation=applicationrecommendation)    

@app.route("/staff/reviewApplications")
def reviewApplications():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT Applicant_User_userId, idApplication, dateReceived, priorTranscript FROM application WHERE applicationStatus ='Complete'"
    )
    myresult = mycursor.fetchall()
    mydb.close()
    return render_template('staff/reviewApplications.html', my_list=myresult)

@app.route("/staff/reviewApplicationForm/<id>")
def reviewApplication(id):
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM application WHERE idApplication =%s"
        % id
    )
    application = mycursor.fetchall()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM priordegree WHERE Application_idApplication =%s"
        % id
    )
    priordegree = mycursor.fetchall()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM recomendationletter WHERE Application_idApplication =%s"
        % id
    )
    recommendations = mycursor.fetchall()

    print(application)

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM person WHERE userId =%s"
        % application[0][1]
    )
    person = mycursor.fetchall()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT userId, firstName, lastName FROM advisor INNER JOIN person ON advisor.Staff_Person_userId = person.userId"
    )
    advisor = mycursor.fetchall()

    print(priordegree)

    return render_template('staff/reviewApplication.html', person=person, application=application, priordegree=priordegree, recommendations=recommendations, advisor=advisor)    

@app.route("/staff/updateApplications")
def updateApplications():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT Applicant_User_userId, idApplication, dateReceived, priorTranscript, applicationStatus FROM application"
    )
    myresult = mycursor.fetchall()
    mydb.close() 

    previousUrl = request.referrer

    return render_template('staff/gcUpdateApplications.html', my_list=myresult, previousUrl=previousUrl)

@app.route("/staff/gcUpdateApplicationForm", methods=["POST"])
def gcUpdateApplicationForm():
    previousUrl = request.form["previousUrl"]
    id = request.form["idApplication"]

    print(previousUrl)
    print(id)

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT priorTranscript FROM application WHERE idApplication =%s"
        % id
    )
    myresult = mycursor.fetchall()
    if (myresult[0][0] == 1):
        received='1'
    elif (myresult[0][0] == 0):
        received='0'
    else:
        received='0'

    mycursor.execute(
        "SELECT * FROM recomendationletter WHERE Application_idApplication =%s"
        % id
    )
    recommendations = mycursor.fetchall()
    mydb.close()

    return render_template('staff/gcUpdateApplication.html', received=received, recommendations=recommendations, idApplication=id, previousUrl=previousUrl)

@app.route("/staff/gradeStudents")
def gradeStudents():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT s.User_userId, p.firstName, p.lastName, ds.Department_idDepartment FROM student s INNER JOIN person p on p.userId=s.User_userId INNER JOIN department_has_student ds ON s.User_userId=ds.Student_User_userId WHERE s.User_userId IN (SELECT DISTINCT(ss.Student_User_userId) FROM section_has_student ss INNER JOIN person p on p.userId=ss.Student_User_userId);"
    )
    students = mycursor.fetchall()
    print(students)    
    return render_template('staff/gradeStudents.html', students=students)

@app.route("/staff/gradeStudent", methods=["POST"])
def gradeStudent():
    studentId = request.form["studentId"]

    print(studentId)

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT ps.userId, ps.firstName, ps.lastName, ss.Section_sectionNumber, ss.Section_Course_courseNumber, pi.firstName, pi.lastName, ss.grade FROM section_has_student ss INNER JOIN course c INNER JOIN person ps ON ps.userId=ss.Student_User_userId INNER JOIN person pi ON ss.Section_Instructor_Staff_Person_userId=pi.userId where ss.Section_Course_courseNumber=c.courseNumber and ss.Student_User_userId=%s;" % studentId
    )
    courses = mycursor.fetchall()
   
    return render_template('staff/gradeStudent.html', courses=courses)

@app.route("/staff/grade", methods=["POST"])
def grade():
    studentId = request.form["studentId"]
    sectionNumber = request.form["sectionNumber"]
    grade = request.form["grade"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE section_has_student SET grade = %s WHERE (Student_User_userId = %s) AND (Section_sectionNumber = %s)"
    valTranscript = (grade, studentId, sectionNumber)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT avg(g.gradeNo) FROM section_has_student ss INNER JOIN gradeconversion g ON ss.grade=g.grade where ss.Student_User_userId=%s AND ss.grade <> 'In Progress';" % studentId
    )
    my_list = mycursor.fetchall()
    mydb.close()

    gpa=my_list[0][0]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE academics SET gpa = %s WHERE (Student_User_userId = %s)"
    valTranscript = (gpa, studentId)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()
    mydb.close()    

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT ps.userId, ps.firstName, ps.lastName, ss.Section_sectionNumber, ss.Section_Course_courseNumber, pi.firstName, pi.lastName, ss.grade FROM section_has_student ss INNER JOIN course c INNER JOIN person ps ON ps.userId=ss.Student_User_userId INNER JOIN person pi ON ss.Section_Instructor_Staff_Person_userId=pi.userId where ss.Section_Course_courseNumber=c.courseNumber and ss.Student_User_userId=%s;" % studentId
    )
    courses = mycursor.fetchall()
  
    return render_template('staff/gradeStudent.html', courses=courses)

@app.route("/staff/graduateStudentApplicants")
def graduateStudentApplicants():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT ga.Student_User_userId, p.firstName, p.lastName, ds.Department_idDepartment, ga.status FROM graduateapplication ga INNER JOIN person p ON ga.Student_User_userId=p.userId INNER JOIN department_has_student ds ON ga.Student_User_userId=ds.Student_User_userId WHERE ga.status = 'Cleared';"
    )
    students = mycursor.fetchall()
    print(students)    
    return render_template('staff/graduateStudentApplicants.html', students=students)

@app.route("/staff/approveGraduation", methods=["POST"])
def approveGraduation():
    studentId = request.form["studentId"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE graduateapplication SET status = %s, GS_Staff_Person_userId = %s WHERE (Student_User_userId = %s)"
    valTranscript = ('Graduated', 1, studentId)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE student SET status = %s WHERE (User_userId = %s)"
    valTranscript = (0, studentId)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE student SET status = %s WHERE (User_userId = %s)"
    valTranscript = (0, studentId)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sql = "INSERT INTO alumni (graduationYear, Person_userId) VALUES (%s,%s)"
    val = (date.today().year, studentId)
    mycursor.execute(sql, val)
    mydb.commit()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sql = "INSERT INTO alumni_has_academics (Alumni_Person_userId, academics_Student_User_userId) VALUES (%s,%s)"
    val = (studentId, studentId)
    mycursor.execute(sql, val)
    mydb.commit()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT ga.Student_User_userId, p.firstName, p.lastName, ds.Department_idDepartment, ga.status FROM graduateapplication ga INNER JOIN person p ON ga.Student_User_userId=p.userId INNER JOIN department_has_student ds ON ga.Student_User_userId=ds.Student_User_userId WHERE ga.status = 'Cleared';"
    )
    students = mycursor.fetchall()
    print(students)    
    return render_template('staff/graduateStudentApplicants.html', students=students)

############################################################################################


@app.route("/alumni")
def alumni():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT p.userId, p.firstName, p.lastName, p.email, p.password FROM alumni a INNER JOIN person p ON a.Person_userId = p.userId;"
    )
    activeAlumni = mycursor.fetchall()

    res = render_template(
        "/alumni/alumni.html",
        activeAlumni=activeAlumni
    )
    return res

@app.route("/alumni/alumniLogin", methods=["POST"])
def alumniLogin():
    email = request.form["email"]
    password = request.form["password"]

    return redirect(url_for("alumnus", password=password))  

@app.route("/alumni/alumni/<password>")
def alumnus(password):
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT p.userId, p.firstName, p.middleName, p.lastName , p.homePhone, p.workPhone, p.mobilePhone, p.email, p.streetAddress, p.city, p.state, p.zipcode FROM alumni a INNER JOIN person p ON a.Person_userId = p.userId WHERE a.Person_userId =%s;"
        % password
    )
    personalInfo = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT a.graduationYear, ac.gpa, d.name FROM alumni a INNER JOIN alumni_has_academics aa ON a.Person_userId=aa.academics_Student_User_userId INNER JOIN academics ac ON aa.academics_Student_User_userId=ac.Student_User_userId INNER JOIN department d ON ac.program=d.idDepartment WHERE a.Person_userId =%s;"
        % password
    )
    academics = mycursor.fetchall()
    mydb.close()

    res = render_template(
        "alumni/alumnus.html", personalInfo=personalInfo, academics=academics
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

def convertScore(score):
    if score=='high':
        return 'top 5%'
    elif score=='midHigh':
        return '85-94%'
    elif score=='midLow':
        return '70-84%'
    elif score=='low':
        return 'below 70%'
    else:
        return None


@app.route("/staff/finalDecisionApplication", methods=["POST"])
def finalDecisionApplication():
    finalDecision = request.form["finalDecision"]
    idApplication = request.form["idApplication"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sql = "UPDATE application SET applicationDecision = %s WHERE idApplication = %s"
    val = (finalDecision, idApplication)
    mycursor.execute(sql,val)
    mydb.commit()

    return redirect(
        url_for("finalDecisionApplications")
    )

@app.route("/staff/reviewerReviewApplication", methods=["POST"])
def reviewerReviewApplication():
    recommendation = request.form["recommendation"]
    recommendationComments = request.form["recommendationComments"]
    personId = request.form["personId"]
    idApplication = request.form["idApplication"]
    recommendAdvisor = request.form["recommendAdvisor"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM reviewer"
    )
    myresult = mycursor.fetchall()

    reviewer = myresult[0][0]

    if recommendAdvisor == 'empty':
        recommendAdvisor=None


    sql = "INSERT INTO applicationrecommendation (recommendation, comments, Application_idApplication, Application_Applicant_User_userId, Reviewer_Staff_Person_userId, Advisor_Staff_Person_userId) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (
        recommendation,
        recommendationComments,
        idApplication,
        personId,
        reviewer,
        recommendAdvisor,
    )
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    userID = mycursor.lastrowid
    mydb.commit()
    mydb.close()

    return redirect(
        url_for("reviewApplications")
    )

@app.route("/staff/gcUpdateApplication", methods=["POST"])
def gcUpdateApplication():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlRecommendation = "UPDATE recomendationletter SET score = %s WHERE RecomendationLetterId = %s"

    idApplication = request.form["idApplication"]
    transcript = request.form["transcript"]

    sqlTranscript = "UPDATE application SET priorTranscript = %s WHERE idApplication = %s"

    if transcript == 'received':
        valTranscript = (1, idApplication)
        mycursor.execute(sqlTranscript,valTranscript)
        mydb.commit()
    elif transcript == 'notReceived':
        valTranscript = (0, idApplication)
        mycursor.execute(sqlTranscript,valTranscript)
        mydb.commit()

    if "score1" in request.form:
        score1 = request.form["score1"]
    if "score2" in request.form:
        score2 = request.form["score2"]
    if "score3" in request.form:
        score3 = request.form["score3"]    

    if "recommendation1" in request.form:
        recommendation1 = request.form["recommendation1"]
        val = (convertScore(score1), recommendation1)
        mycursor.execute(sqlRecommendation,val)
        mydb.commit()
    if "recommendation2" in request.form:
        recommendation2 = request.form["recommendation2"]
        val = (convertScore(score2), recommendation2)
        mycursor.execute(sqlRecommendation,val)
        mydb.commit()
    if "recommendation3" in request.form:
        recommendation3 = request.form["recommendation3"]     
        val = (convertScore(score3), recommendation3)
        mycursor.execute(sqlRecommendation,val)
        mydb.commit()
    
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT Applicant_User_userId, priorTranscript FROM application WHERE idApplication =%s"
        % idApplication
    )

    received='0'

    myresult = mycursor.fetchall()
    if (myresult[0][1] == 1):
        received='1'

    print(received)

    Applicant_User_userId = myresult[0][0]

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT score FROM recomendationletter WHERE Application_idApplication =%s"
        % idApplication
    )
    recommendations = mycursor.fetchall()

    flag = True

    if len(recommendations) == 0:
        flag = False

    for recommendation in recommendations:
        if recommendation[0] == 'None':
            flag = False
        elif recommendation[0] is None:
            flag= False
    
    if ((flag == True) & (received=='1')):
        sqlTranscript = "UPDATE application SET applicationStatus = %s WHERE idApplication = %s"
        valTranscript = ('Complete', idApplication)
        mycursor.execute(sqlTranscript,valTranscript)
        mydb.commit()
    else:
        sqlTranscript = "UPDATE application SET applicationStatus = %s WHERE idApplication = %s"
        valTranscript = ('Incomplete', idApplication)
        mycursor.execute(sqlTranscript,valTranscript)
        mydb.commit()

    mydb.close()

    return redirect(
        url_for("updateApplications")
    )


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
    greScoreAnalytical  = request.form["greScoreAnalytical"]
    greScoreQuantitative = request.form["greScoreQuantitative"]
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
    sql = "INSERT INTO application (Applicant_User_userId, program, greScoreVerbal, greScoreAnalytical, greScoreQuantitative, priorWorkExperience, admissionTerm, dateReceived, areaOfInterest) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (
        userID,
        program,
        greScoreVerbal,
        greScoreAnalytical,
        greScoreQuantitative,
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
        mydb.close()

    
    print(mycursor.rowcount, "record inserted.")

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE application SET applicationStatus = %s WHERE idApplication = %s"
    valTranscript = ('Incomplete', applicationID)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()
    mydb.close()

    return redirect(
        url_for("prospectiveStudentsApplicationSubmitted", studentID=userID)
    )


if __name__ == "__main__":
    app.run(debug=True)
