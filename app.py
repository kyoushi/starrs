from mysql.connector import pooling
from datetime import datetime
from flask import Flask, redirect, url_for, request, render_template
import atexit
import requests

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
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT User_userId, firstName, lastName, email, password FROM applicant INNER JOIN person ON person.userId = applicant.User_userId;;"
    )
    applicants = mycursor.fetchall()


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
    transcript = myresult[0][0]

    print(transcript)

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
    print(password)

    res = render_template(
        "students/student.html", password=password
    )
    return res

@app.route("/students/degreeCourses", methods=["POST"])
def degreeCourses():
    studentId = request.form["studentId"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT c.courseNumber, c.title, c.credits, sc.Student_User_userId FROM department_has_course dc INNER JOIN course c ON dc.Course_courseNumber=c.courseNumber INNER JOIN department_has_student ds ON dc.Department_idDepartment=ds.Department_idDepartment LEFT JOIN student_has_course sc ON sc.Course_courseNumber=c.courseNumber WHERE ds.Student_User_userId=%s;" % studentId
    )
    degreeCourses = mycursor.fetchall()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber WHERE sc.Student_User_userId=%s;" % studentId
    )
    credits = mycursor.fetchall()
    totalCredits = credits[0][0]

    if totalCredits is None:
        totalCredits = 0

    res = render_template(
        "students/degreeCourses.html", degreeCourses=degreeCourses, studentId=studentId, totalCredits=totalCredits
    )

    return res

@app.route("/students/modifyDegreeCourses", methods=["POST"])
def modifyDegreeCourses():
    studentId = request.form["studentId"]
    courseNumber = request.form["courseNumber"]
    action = request.form["action"]

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
        "SELECT c.courseNumber, c.title, c.credits, sc.Student_User_userId FROM department_has_course dc INNER JOIN course c ON dc.Course_courseNumber=c.courseNumber INNER JOIN department_has_student ds ON dc.Department_idDepartment=ds.Department_idDepartment LEFT JOIN student_has_course sc ON sc.Course_courseNumber=c.courseNumber WHERE ds.Student_User_userId=%s;" % studentId
    )
    degreeCourses = mycursor.fetchall()

    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber WHERE sc.Student_User_userId=%s;" % studentId
    )
    credits = mycursor.fetchall()
    totalCredits = credits[0][0]

    if totalCredits is None:
        totalCredits = 0

    res = render_template(
        "students/degreeCourses.html", degreeCourses=degreeCourses, studentId=studentId, totalCredits=totalCredits
    )

    return res

@app.route("/students/enrollCourses", methods=["POST"])
def enrollCourses():
    studentId = request.form["studentId"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT s.sectionNumber, s.year, s.semester, c.courseNumber, c.title, c.credits, p.firstName, p.lastName, ss.Student_User_userId, s.Instructor_Staff_Person_userId  FROM starss.student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId LEFT JOIN student_has_section ss ON ss.Section_sectionNumber=s.sectionNumber  WHERE sc.Student_User_userId=%s;" % studentId
    )
    enrollCourses = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM starss.student_has_section ss INNER JOIN course c ON ss.Section_Course_courseNumber=c.courseNumber WHERE ss.Student_User_userId=%s;" % studentId
    )
    credits = mycursor.fetchall()
    mydb.close()
    totalCredits = credits[0][0]

    if totalCredits is None:
        totalCredits = 0


    res = render_template(
        "students/enrollCourses.html", enrollCourses=enrollCourses, studentId=studentId, totalCredits=totalCredits
    )

    return res   

@app.route("/students/modifyEnroll", methods=["POST"])
def modifyEnroll():
    studentId = request.form["studentId"]
    courseNumber = request.form["courseNumber"]
    sectionNumber = request.form["sectionNumber"]
    instructorId = request.form["instructorId"]
    action = request.form["action"]

    print(studentId)
    print(courseNumber)
    print(sectionNumber)
    print(instructorId)
    print(action)

    if action == 'Register':
        mydb = dbConnect()
        mycursor = mydb.cursor()
        sql = "INSERT INTO student_has_section (Student_User_userId, Section_sectionNumber, Section_Course_courseNumber, Section_Instructor_Staff_Person_userId, grade) VALUES (%s,%s,%s,%s,%s)"
        val = (studentId, sectionNumber, courseNumber, instructorId, 'In Progress')
        mycursor.execute(sql, val)
        mydb.commit()
        mydb.close()
    elif action == 'Drop':
        mydb = dbConnect()
        mycursor = mydb.cursor()
        sql = "DELETE FROM student_has_section WHERE (Student_User_userId = %s) and (Section_sectionNumber = %s) and (Section_Course_courseNumber = %s) and (Section_Instructor_Staff_Person_userId = %s)"
        valTranscript = (studentId, sectionNumber, courseNumber, instructorId)
        mycursor.execute(sql,valTranscript)
        mydb.commit()
        mydb.close()


    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT s.sectionNumber, s.year, s.semester, c.courseNumber, c.title, c.credits, p.firstName, p.lastName, ss.Student_User_userId, s.Instructor_Staff_Person_userId  FROM starss.student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId LEFT JOIN student_has_section ss ON ss.Section_sectionNumber=s.sectionNumber  WHERE sc.Student_User_userId=%s;" % studentId
    )
    enrollCourses = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM starss.student_has_section ss INNER JOIN course c ON ss.Section_Course_courseNumber=c.courseNumber WHERE ss.Student_User_userId=%s;" % studentId
    )
    credits = mycursor.fetchall()
    mydb.close()
    totalCredits = credits[0][0]

    if totalCredits is None:
        totalCredits = 0

    res = render_template(
        "students/enrollCourses.html", enrollCourses=enrollCourses, studentId=studentId, totalCredits=totalCredits
    )

    return res

@app.route("/students/viewGrades", methods=["POST"])
def viewGrades():
    studentId = request.form["studentId"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT s.sectionNumber, s.year, s.semester, c.courseNumber, c.title, c.credits, p.firstName, p.lastName, ss.Student_User_userId, s.Instructor_Staff_Person_userId, ss.grade  FROM starss.student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId LEFT JOIN student_has_section ss ON ss.Section_sectionNumber=s.sectionNumber  WHERE sc.Student_User_userId=%s;" % studentId
    )
    courses = mycursor.fetchall()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT SUM(c.credits) FROM starss.student_has_section ss INNER JOIN course c ON ss.Section_Course_courseNumber=c.courseNumber WHERE ss.Student_User_userId=%s AND ss.grade <> 'In Progress';" % studentId
    )
    credits = mycursor.fetchall()
    mydb.close()
    totalCredits = credits[0][0]

    if totalCredits is None:
        totalCredits = 0


    res = render_template(
        "students/viewGrades.html", courses=courses, studentId=studentId, totalCredits=totalCredits
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
        "SELECT Applicant_User_userId, program FROM application where idApplication = %s" % id
    )
    application = mycursor.fetchall()

    applicationUserId=application[0][0]
    program=application[0][1]

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
    print(myresult)    
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
    print(myresult)    
    return render_template('staff/gcUpdateApplications.html', my_list=myresult)

@app.route("/staff/gcUpdateApplicationForm/<id>")
def gcUpdateApplicationForm(id):
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

    return render_template('staff/gcUpdateApplication.html', received=received, recommendations=recommendations, idApplication=id)

@app.route("/staff/gradeStudents")
def gradeStudents():
    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT s.User_userId, p.firstName, p.lastName, ds.Department_idDepartment FROM student s INNER JOIN person p on p.userId=s.User_userId INNER JOIN department_has_student ds ON s.User_userId=ds.Student_User_userId WHERE s.User_userId IN (SELECT DISTINCT(ss.Student_User_userId) FROM student_has_section ss INNER JOIN person p on p.userId=ss.Student_User_userId);"
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
        "SELECT ps.userId, ps.firstName, ps.lastName, s.sectionNumber, s.Course_courseNumber, p.firstName, p.lastName, ss.grade  FROM starss.student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId INNER JOIN student_has_section ss ON ss.Section_sectionNumber=s.sectionNumber INNER JOIN person ps ON ps.userId=sc.Student_User_userId WHERE sc.Student_User_userId=%s;" % studentId
    )
    courses = mycursor.fetchall()
    print(courses)    
    return render_template('staff/gradeStudent.html', courses=courses)

@app.route("/staff/grade", methods=["POST"])
def grade():
    studentId = request.form["studentId"]
    sectionNumber = request.form["sectionNumber"]
    grade = request.form["grade"]

    mydb = dbConnect()
    mycursor = mydb.cursor()
    sqlTranscript = "UPDATE student_has_section SET grade = %s WHERE (Student_User_userId = %s) AND (Section_sectionNumber = %s)"
    valTranscript = (grade, studentId, sectionNumber)
    mycursor.execute(sqlTranscript,valTranscript)
    mydb.commit()
    mydb.close()

    mydb = dbConnect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT ps.userId, ps.firstName, ps.lastName, s.sectionNumber, s.Course_courseNumber, p.firstName, p.lastName, ss.grade  FROM starss.student_has_course sc INNER JOIN course c ON sc.Course_courseNumber=c.courseNumber INNER JOIN section s ON c.courseNumber=s.Course_courseNumber INNER JOIN person p ON p.userId=s.Instructor_Staff_Person_userId INNER JOIN student_has_section ss ON ss.Section_sectionNumber=s.sectionNumber INNER JOIN person ps ON ps.userId=sc.Student_User_userId WHERE sc.Student_User_userId=%s;" % studentId
    )
    courses = mycursor.fetchall()
    print(courses)    
    return render_template('staff/gradeStudent.html', courses=courses)

    return ''


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

    

    print(mycursor.rowcount, "record inserted.")

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
