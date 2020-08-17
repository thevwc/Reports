# routes.py

from flask import session, render_template, flash, redirect, url_for, request, jsonify, json, make_response, after_this_request
from flask_weasyprint import HTML, render_pdf
import pdfkit
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_parse
from app.models import ShopName, Member, MemberActivity, MonitorSchedule, MonitorScheduleTransaction,\
MonitorWeekNote, CoordinatorsSchedule, ControlVariables, EmailMessages

from app import app
from app import db
from sqlalchemy import func, case, desc, extract, select, update, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DBAPIError

import datetime as dt
from datetime import date, datetime, timedelta

import os.path
from os import path


from flask_mail import Mail, Message
mail=Mail(app)


@app.route('/coordinatorReports/')
@app.route('/coordinatorReports/index/')
@app.route('/coordinatorReports/index', methods=['GET'])
def index():
    # testMail = False
    # if testMail:
    #     msg = Message('Hello', sender = 'hartl1r@gmail.com', recipients = ['hartl1r@gmail.com'])
    #     msg.body = "This is the email body"
    #     mail.send(msg)
    #     return "Sent"

    # GET REQUEST


    # BUILD ARRAY OF NAMES FOR DROPDOWN LIST OF COORDINATORS
    coordNames=[]
    sqlNames = "SELECT Last_Name + ', ' + First_Name as coordName, Member_ID as coordID FROM tblMember_Data "
    sqlNames += "WHERE Monitor_Coordinator = 1 "
    sqlNames += "ORDER BY Last_Name, First_Name "
    coordNames = db.engine.execute(sqlNames)
   
    # BUILD ARRAY OF MONITOR WEEKS FOR BOTH LOCATIONS
    sqlWeeks = "SELECT Shop_Number as shopNumber, Start_Date,format(Start_Date,'MMM d, yyyy') as DisplayDate, "
    sqlWeeks += "Coordinator_ID as coordID, Last_Name + ', ' + First_Name as coordName, eMail as coordEmail "
    sqlWeeks += " FROM coordinatorsSchedule "
    sqlWeeks += "LEFT JOIN tblMember_Data ON coordinatorsSchedule.Coordinator_ID = tblMember_Data.Member_ID "
    sqlWeeks += "WHERE Start_Date >= getdate() "
    sqlWeeks += "ORDER BY Shop_Number, Start_Date"
    weeks = db.engine.execute(sqlWeeks)

    # EMAIL ADDRESSES OF COORDINATOR AND ALL MONITORS FOR WEEK
    #sqlEmailAddresses = "SELECT TOP 10 (Last_Name + ', ' + First_Name) as memberName, eMail FROM tblMember_Data ORDER BY Last_Name, First_Name"
    #eMails = db.engine.execute(sqlEmailAddresses)
    # for e in eMails:
    #     print(e.memberName,e.eMail)
    # MEMBER NAMES AND ID
    sqlMembers = "SELECT top 10 Last_Name + ', ' + First_Name + ' (' + Member_ID + ')' as name, eMail FROM tblMember_Data "
    sqlMembers += "ORDER BY Last_Name, First_Name "
    #print ('sql - ',sqlMembers)
    nameList = db.engine.execute(sqlMembers)
    # for n in nameList:
    #     print (n.name,n.eMail)

    return render_template("index.html",coordNames=coordNames,weeks=weeks,nameList=nameList)  #,eMails=eMails)
   



# PRINT WEEKLY MONITOR DUTY SCHEDULE FOR COORDINATOR
@app.route("/coordinatorReports/printWeeklyMonitorSchedule", methods = ['GET'])
def printWeeklyMonitorSchedule():
    print('printWeeklyMonitorSchedule routine')
    dateScheduled=request.args.get('date')
    shopNumber=request.args.get('shop')
    destination = request.args.get('destination')  # destination is 'PRINT or 'PDF'
 
    # LOOK UP SHOP NAME
    shopRecord = db.session.query(ShopName).filter(ShopName.Shop_Number==shopNumber).first()
    shopName = shopRecord.Shop_Name
    
    #  DATE SELECTED IS ALWAYS A MONDAY
    #  CONVERT TO DATE TYPE
    dateScheduledDat = datetime.strptime(dateScheduled,'%Y-%m-%d')
    beginDateDAT = dateScheduledDat + timedelta(days=1)
    beginDateSTR = beginDateDAT.strftime('%m-%d-%Y')

    endDateDAT = beginDateDAT + timedelta(days=6)
    endDateSTR = endDateDAT.strftime('%m-%d-%Y')

    # DEFINE COLUMN HEADING DATES
    sunDateDAT = dateScheduledDat 
    sunDate = sunDateDAT.strftime('%m-%d-%Y')
    monDateDAT = dateScheduledDat + timedelta(days=1)
    monDate = monDateDAT.strftime('%m-%d-%Y')
    tueDateDAT = dateScheduledDat + timedelta(days=2)
    tueDate = tueDateDAT.strftime('%m-%d-%Y')
    wedDateDAT = dateScheduledDat + timedelta(days=3)
    wedDate = wedDateDAT.strftime('%m-%d-%Y')
    thuDateDAT = dateScheduledDat + timedelta(days=4)
    thuDate = thuDateDAT.strftime('%m-%d-%Y')
    friDateDAT = dateScheduledDat + timedelta(days=5)
    friDate = friDateDAT.strftime('%m-%d-%Y')
    satDateDAT = dateScheduledDat + timedelta(days=6)
    satDate = satDateDAT.strftime('%m-%d-%Y')

    
    # RETRIEVE SCHEDULE FOR SPECIFIC WEEK
    todays_date = date.today()
    todays_dateSTR = todays_date.strftime('%-m-%-d-%Y')

    # GET COORDINATOR ID FROM COORDINATOR TABLE
    coordinatorRecord = db.session.query(CoordinatorsSchedule)\
        .filter(CoordinatorsSchedule.Start_Date==sunDateDAT)\
        .filter(CoordinatorsSchedule.Shop_Number==shopNumber).first()
    if coordinatorRecord == None:
        coordinatorsName = 'Not Assigned'
        coordinatorsEmail = ''
    else:
        # LOOK UP COORDINATORS NAME
        coordinatorID = coordinatorRecord.Coordinator_ID
        memberRecord = db.session.query(Member).filter(Member.Member_ID==coordinatorID).first()
        if memberRecord == None:
            coordinatorsName = '(' + str(coordinatorID) + ')'
        else:
            if memberRecord.NickName != None and memberRecord.NickName != '':
                coordinatorsName = memberRecord.First_Name + ' ' + memberRecord.Last_Name + ' (' + memberRecord.NickName + ')'
            else:
                coordinatorsName = memberRecord.First_Name + ' ' + memberRecord.Last_Name
        coordinatorsEmail = memberRecord.eMail
    
    
    sqlSMAM = "SELECT Count(tblMonitor_Schedule.Member_ID) AS SMAMrows "
    sqlSMAM += "FROM tblMonitor_Schedule "
    sqlSMAM += "WHERE tblMonitor_Schedule.Duty = 'Shop Monitor' "
    sqlSMAM += "AND tblMonitor_Schedule.AM_PM = 'AM' "
    sqlSMAM += "AND tblMonitor_Schedule.Shop_Number='" + shopNumber + "' "
    sqlSMAM += "AND tblMonitor_Schedule.Date_Scheduled >= '" + beginDateSTR + "' "
    sqlSMAM += "AND tblMonitor_Schedule.Date_Scheduled <= '" + endDateSTR + "' "
    sqlSMAM += "GROUP BY tblMonitor_Schedule.Date_Scheduled ORDER BY Count(tblMonitor_Schedule.Member_ID) DESC"
    SMAMrows = db.engine.execute(sqlSMAM).scalar()
    
    sqlSMPM = "SELECT Count(tblMonitor_Schedule.Member_ID) AS SMPMrows "
    sqlSMPM += "FROM tblMonitor_Schedule "
    sqlSMPM += "WHERE tblMonitor_Schedule.Duty = 'Shop Monitor' "
    sqlSMPM += "AND tblMonitor_Schedule.AM_PM = 'PM' "
    sqlSMPM += "AND tblMonitor_Schedule.Shop_Number='" + shopNumber + "' "
    sqlSMPM += "AND tblMonitor_Schedule.Date_Scheduled >= '" + beginDateSTR + "' "
    sqlSMPM += "AND tblMonitor_Schedule.Date_Scheduled <= '" + endDateSTR + "' "
    sqlSMPM += "GROUP BY tblMonitor_Schedule.Date_Scheduled ORDER BY Count(tblMonitor_Schedule.Member_ID) DESC"
    SMPMrows = db.engine.execute(sqlSMPM).scalar()
    
    sqlTCAM = "SELECT Count(tblMonitor_Schedule.Member_ID) AS TCAMrows "
    sqlTCAM += "FROM tblMonitor_Schedule "
    sqlTCAM += "WHERE tblMonitor_Schedule.Duty = 'Tool Crib' "
    sqlTCAM += "AND tblMonitor_Schedule.AM_PM = 'AM' "
    sqlTCAM += "AND tblMonitor_Schedule.Shop_Number='" + shopNumber + "' "
    sqlTCAM += "AND tblMonitor_Schedule.Date_Scheduled >= '" + beginDateSTR + "' "
    sqlTCAM += "AND tblMonitor_Schedule.Date_Scheduled <= '" + endDateSTR + "' "
    sqlTCAM += "GROUP BY tblMonitor_Schedule.Date_Scheduled ORDER BY Count(tblMonitor_Schedule.Member_ID) DESC"
    TCAMrows = db.engine.execute(sqlTCAM).scalar()
    
    sqlTCPM = "SELECT Count(tblMonitor_Schedule.Member_ID) AS TCPMrows "
    sqlTCPM += "FROM tblMonitor_Schedule "
    sqlTCPM += "WHERE tblMonitor_Schedule.Duty = 'Tool Crib' "
    sqlTCPM += "AND tblMonitor_Schedule.AM_PM = 'AM' "
    sqlTCPM += "AND tblMonitor_Schedule.Shop_Number='" + shopNumber + "' "
    sqlTCPM += "AND tblMonitor_Schedule.Date_Scheduled >= '" + beginDateSTR + "' "
    sqlTCPM += "AND tblMonitor_Schedule.Date_Scheduled <= '" + endDateSTR + "' "
    sqlTCPM += "GROUP BY tblMonitor_Schedule.Date_Scheduled ORDER BY Count(tblMonitor_Schedule.Member_ID) DESC"
    TCPMrows = db.engine.execute(sqlTCPM).scalar()
    

    # DEFINE ARRAYS FOR EACH GROUPING
    rows = SMAMrows 
    cols = 6    # member name and training needed Y or N
    SMAMnames = [[0 for x in range(cols)] for y in range(rows)]
    SMAMtraining = [[0 for x in range(cols)] for y in range(rows)]

    rows = SMPMrows  
    cols = 6    # member name and training needed Y or N
    SMPMnames = [[0 for x in range(cols)] for y in range(rows)]
    SMPMtraining = [[0 for x in range(cols)] for y in range(rows)]

    rows = TCAMrows 
    cols = 6    # member name and training needed Y or N
    TCAMnames = [[0 for x in range(cols)] for y in range(rows)]
    TCAMtraining = [[0 for x in range(cols)] for y in range(rows)]

    rows = TCPMrows  
    cols = 6    # member name and training needed Y or N
    TCPMnames = [[0 for x in range(cols)] for y in range(rows)]
    TCPMtraining = [[0 for x in range(cols)] for y in range(rows)]


    # BUILD SELECT STATEMENT TO RETRIEVE SM MEMBERS SCHEDULE FOR CURRENT YEAR FORWARD
    sqlSelectSM = "SELECT tblMember_Data.Member_ID as memberID, "
    sqlSelectSM += "First_Name + ' ' + Last_Name as displayName, tblShop_Names.Shop_Name, "
    sqlSelectSM += "Last_Monitor_Training as trainingDate, DATEPART(year,Last_Monitor_Training) as trainingYear, "
    sqlSelectSM += "tblMonitor_Schedule.Member_ID, DATEPART(dw,Date_Scheduled)-2 as dayOfWeek, "
    sqlSelectSM += " format(Date_Scheduled,'M/d/yyyy') as DateScheduled, DATEPART(year,Date_Scheduled) as scheduleYear, "
    sqlSelectSM += "AM_PM, Duty, No_Show, tblMonitor_Schedule.Shop_Number, tblMember_Data.Monitor_Duty_Waiver_Expiration_Date as waiver "
    sqlSelectSM += "FROM tblMember_Data "
    sqlSelectSM += "LEFT JOIN tblMonitor_Schedule ON tblMonitor_Schedule.Member_ID = tblMember_Data.Member_ID "
    sqlSelectSM += "LEFT JOIN tblShop_Names ON tblMonitor_Schedule.Shop_Number = tblShop_Names.Shop_Number "
    sqlSelectSM += "WHERE Date_Scheduled between '" + beginDateSTR + "' and '" + endDateSTR + "' "
    sqlSelectSM += "ORDER BY dayOfWeek, AM_PM,Last_Name"
    SMschedule = db.engine.execute(sqlSelectSM)
    
    # BUILD SELECT STATEMENT TO RETRIEVE SM MEMBERS SCHEDULE FOR CURRENT YEAR FORWARD
    sqlSelectTC = "SELECT tblMember_Data.Member_ID as memberID, "
    sqlSelectTC += "First_Name + ' ' + Last_Name as displayName, tblShop_Names.Shop_Name, "
    sqlSelectTC += "Last_Monitor_Training as trainingDate, DATEPART(year,Last_Monitor_Training) as trainingYear, "
    sqlSelectTC += "tblMonitor_Schedule.Member_ID, DATEPART(dw,Date_Scheduled)-0 as dayOfWeek, "
    sqlSelectTC += " format(Date_Scheduled,'M/d/yyyy') as DateScheduled, DATEPART(year,Date_Scheduled) as scheduleYear, "
    sqlSelectTC += "AM_PM, Duty, No_Show, tblMonitor_Schedule.Shop_Number, tblMember_Data.Monitor_Duty_Waiver_Expiration_Date as waiver "
    sqlSelectTC += "FROM tblMember_Data "
    sqlSelectTC += "LEFT JOIN tblMonitor_Schedule ON tblMonitor_Schedule.Member_ID = tblMember_Data.Member_ID "
    sqlSelectTC += "LEFT JOIN tblShop_Names ON tblMonitor_Schedule.Shop_Number = tblShop_Names.Shop_Number "
    sqlSelectTC += "WHERE Date_Scheduled between '" + beginDateSTR + "' and '" + endDateSTR + "' "
    sqlSelectTC += " and tblMonitor_Schedule.Duty = 'Tool Crib' "
    sqlSelectTC += "ORDER BY dayOfWeek, AM_PM, Last_Name"
    TCschedule = db.engine.execute(sqlSelectTC)

    #   BUILD SHOP MONITOR ARRAYS
    for s in SMschedule:
        
        # IS TRAINING NEEDED?
        if (s.waiver == None):
            if (s.trainingYear == None):
                trainingNeeded = 'Y'
            else:
                intTrainingYear = int(s.trainingYear) +2
                intScheduleYear = int(s.scheduleYear)
                if (intTrainingYear <= intScheduleYear):
                    trainingNeeded = 'Y'
                else:
                    trainingNeeded = 'N'
        else:
            trainingNeeded = 'N'

    

        # Group - Shop Monitor;  shift - AM
        if (s.Duty == 'Shop Monitor' and s.AM_PM == 'AM'):
            for r in range(SMAMrows):
                if (SMAMnames[r][s.dayOfWeek] == 0):
                    SMAMnames[r][s.dayOfWeek] = s.displayName
                    SMAMtraining[r][s.dayOfWeek] = trainingNeeded
                    break
        
        # Group - Shop Monitor;  shift - PM
        if (s.Duty == 'Shop Monitor' and s.AM_PM == 'PM'): 
            for r in range(SMPMrows):
                if (SMPMnames[r][s.dayOfWeek] == 0):
                    SMPMnames[r][s.dayOfWeek] = s.displayName
                    SMPMtraining[r][s.dayOfWeek] = trainingNeeded
                    break

        # Group - Tool Crib;  shift - AM
        if (s.Duty == 'Tool Crib' and s.AM_PM == 'AM'):
            for r in range(TCAMrows):
                if (TCAMnames[r][s.dayOfWeek] == 0):
                    TCAMnames[r][s.dayOfWeek] = s.displayName
                    TCAMtraining[r][s.dayOfWeek] = trainingNeeded
                    break

        # Group - Tool Crib;  shift - PM
        if (s.Duty == 'Tool Crib' and s.AM_PM == 'PM'):
            for r in range(TCPMrows):
                if (TCPMnames[r][s.dayOfWeek] == 0):
                    TCPMnames[r][s.dayOfWeek] = s.displayName
                    TCPMtraining[r][s.dayOfWeek] = trainingNeeded
                    break


    # REPLACE 0 WITH BLANK IN NAMES ARRAY
    for r in range(SMAMrows):
        c=0
        while c <= 5:
            if (SMAMnames[r][c] == 0):
                SMAMnames[r][c] = ''
            c += 1
    for r in range(SMPMrows):
            c=0
            while c <= 5:
                if (SMPMnames[r][c] == 0):
                    SMPMnames[r][c] = ''
                c += 1
    for r in range(TCAMrows):
        c=0
        while c <= 5:
            if (TCAMnames[r][c] == 0):
                TCAMnames[r][c] = ''
            c += 1
    for r in range(TCPMrows):
            c=0
            while c <= 5:
                if (TCPMnames[r][c] == 0):
                    TCPMnames[r][c] = ''
                c += 1
    
    
    if (destination == 'PDF'):
        html =  render_template("rptWeeklyMonitorSchedule.html",\
        SMAMnames=SMAMnames,SMPMnames=SMPMnames,TCAMnames=TCAMnames,TCPMnames=TCPMnames,\
        SMAMtraining=SMAMtraining,SMPMtraining=SMPMtraining,TCAMtraining=TCAMtraining,TCPMtraining=TCPMtraining,\
        SMAMrows=SMAMrows,SMPMrows=SMPMrows,TCAMrows=TCAMrows,TCPMrows=TCPMrows,\
        shopName=shopName,weekOf=beginDateSTR,coordinatorsName=coordinatorsName, coordinatorsEmail=coordinatorsEmail,\
        todays_date=todays_dateSTR,\
        monDate=monDate,tueDate=tueDate,wedDate=wedDate,thuDate=thuDate,friDate=friDate,satDate=satDate)
        
        # DEFINE PATH TO USE TO STORE PDF
        currentWorkingDirectory = os.getcwd()
        pdfDirectoryPath = currentWorkingDirectory + "/app/static/pdf"
        filePath = pdfDirectoryPath + "/printWeeklyMonitorSchedule.pdf"
        # remove the next line and the pdf will only be generated to the screen
        #pdfkit.from_string(html,filePath)

        return render_pdf(HTML(string=html))
    else:
        return render_template("rptWeeklyMonitorSchedule.html",\
            SMAMnames=SMAMnames,SMPMnames=SMPMnames,TCAMnames=TCAMnames,TCPMnames=TCPMnames,\
            SMAMtraining=SMAMtraining,SMPMtraining=SMPMtraining,TCAMtraining=TCAMtraining,TCPMtraining=TCPMtraining,\
            SMAMrows=SMAMrows,SMPMrows=SMPMrows,TCAMrows=TCAMrows,TCPMrows=TCPMrows,\
            shopName=shopName,weekOf=beginDateSTR,coordinatorsName=coordinatorsName, coordinatorsEmail=coordinatorsEmail,\
            todays_date=todays_dateSTR,\
            monDate=monDate,tueDate=tueDate,wedDate=wedDate,thuDate=thuDate,friDate=friDate,satDate=satDate)
            

# PRINT WEEKLY LIST OF CONTACTS FOR COORDINATOR
@app.route("/coordinatorReports/printWeeklyMonitorContacts", methods=['GET'])
def printWeeklyMonitorContacts():
    dateScheduled=request.args.get('date')
    shopNumber=request.args.get('shop')
    destination = request.args.get('destination')

    # GET LOCATION NAME FOR REPORT HEADING
    shopRecord = db.session.query(ShopName).filter(ShopName.Shop_Number==shopNumber).first()
    shopName = shopRecord.Shop_Name
    
    #  DETERMINE START OF WEEK DATE
    #  CONVERT TO DATE TYPE
    dateScheduledDat = datetime.strptime(dateScheduled,'%Y-%m-%d')
    dayOfWeek = dateScheduledDat.weekday()

    # GET BEGIN, END DATES FOR REPORT HEADING
    beginDateDAT = dateScheduledDat 
    beginDateSTR = beginDateDAT.strftime('%m-%d-%Y')

    endDateDAT = beginDateDAT + timedelta(days=6)
    endDateSTR = endDateDAT.strftime('%m-%d-%Y')

    weekOfHdg = beginDateDAT.strftime('%B %d, %Y')
    
    # RETRIEVE SCHEDULE FOR SPECIFIC WEEK
    todays_date = date.today()
    todays_dateSTR = todays_date.strftime('%-m-%-d-%Y')

    # VARIABLES FOR DUPLICATE NAME CHECK
    savedSMname=''
    savedTCname=''
    
    # BUILD SELECT STATEMENT TO RETRIEVE SM MEMBERS SCHEDULE FOR CURRENT YEAR FORWARD
    sqlSelectSM = "SELECT tblMember_Data.Member_ID as memberID, "
    sqlSelectSM += "First_Name + ' ' + Last_Name as displayName, "
    sqlSelectSM += "Last_Monitor_Training as trainingDate, DATEPART(year,Last_Monitor_Training) as trainingYear, "
    sqlSelectSM += "'N' as trainingNeeded,"
    sqlSelectSM += " format(Date_Scheduled,'M/d/yyyy') as DateScheduled, DATEPART(year,Date_Scheduled) as scheduleYear, "
    sqlSelectSM += "Duty, eMail, Home_Phone, Cell_Phone,tblMember_Data.Monitor_Duty_Waiver_Expiration_Date as waiver "
    sqlSelectSM += "FROM tblMember_Data "
    sqlSelectSM += "LEFT JOIN tblMonitor_Schedule ON tblMonitor_Schedule.Member_ID = tblMember_Data.Member_ID "
    sqlSelectSM += "WHERE Date_Scheduled between '" + beginDateSTR + "' and '" + endDateSTR + "' "
    sqlSelectSM += " and (tblMonitor_Schedule.Duty = 'Shop Monitor' or tblMonitor_Schedule.Duty = 'Tool Crib') "
    sqlSelectSM += " and tblMonitor_Schedule.Shop_Number = " + shopNumber 
    sqlSelectSM += "ORDER BY Duty, Last_Name, First_Name"
    monitors = db.engine.execute(sqlSelectSM)
    
    SMmonitors = []
    TCmonitors = []

    # STEP THROUGH RESULT SET, DETERMINE IF TRAINING IS NEEDED, BUILD 2D ARRAY (LIST WITHIN LIST)
    for m in monitors:
        # IS TRAINING NEEDED?
        if (m.waiver == None):  # if no waiver 
            if (m.trainingYear == None):  # if last training year is blank
                needsTraining = 'Y'
            else:
                intTrainingYear = int(m.trainingYear) +2  # int of last training year
                intScheduleYear = int(m.scheduleYear) # int of schedule year
                if (intTrainingYear <= intScheduleYear):
                    needsTraining = 'Y'
                else:
                    needsTraining = 'N'
        else:
            needsTraining = 'N'

        #   BUILD SHOP MONITOR ARRAYS
        #   PUT DATA INTO ROW OF ARRAY (SMnames or TCnames)

        #   Group - Shop Monitor; 
        if (m.Duty == 'Shop Monitor' and m.displayName != savedSMname):  # ELIMINATE DUPLICATE NAMES
            savedSMname = m.displayName
            SMmonitor = {'name':m.displayName,
                'trainingYear': m.trainingYear,
                'eMail': m.eMail,
                'homePhone':m.Home_Phone,
                'cellPhone':m.Cell_Phone,
                'needsTraining':needsTraining}
            if SMmonitor['trainingYear'] == None:
                SMmonitor['trainingYear'] = ''
            if SMmonitor['homePhone'] == None:
                SMmonitor['homePhone'] = ''
            if SMmonitor['cellPhone'] == None:
                SMmonitor['cellPhone'] = ''
            SMmonitors.append(SMmonitor)

        #   Group - Tool Crib;  
        if (m.Duty == 'Tool Crib' and m.displayName != savedTCname):    # ELIMINATE DUPLICATE NAMES
            savedTCname = m.displayName 
            TCmonitor = {'name':m.displayName,
                'trainingYear': m.trainingYear,
                'eMail': m.eMail,
                'homePhone':m.Home_Phone,
                'cellPhone':m.Cell_Phone,
                'needsTraining':needsTraining}
            if TCmonitor['trainingYear'] == None:
                TCmonitor['trainingYear'] = ''
            if TCmonitor['homePhone'] == None:
                TCmonitor['homePhone'] = ''
            if TCmonitor['cellPhone'] == None:
                TCmonitor['cellPhone'] = ''
            TCmonitors.append(TCmonitor)
            
    
    if (destination == 'PDF'):
        html = HTML("rptWeeklyContacts.html",\
             beginDate=beginDateSTR,endDate=endDateSTR,todaysDate=todays_dateSTR,\
             locationName=shopName,\
             SMmonitors=SMmonitors,TCmonitors=TCmonitors
             )
        return render_pdf(HTML(string=html))
        # WEASYPRINT .....
        #html.write_pdf('/contacts.pdf')
        # HTML(html).write_pdf('./contacts.pdf')
        #return redirect(url_for('index'))
    else:
        return render_template("rptWeeklyContacts.html",\
            beginDate=beginDateSTR,endDate=endDateSTR,todaysDate=todays_dateSTR,\
            locationName=shopName,\
            SMmonitors=SMmonitors,TCmonitors=TCmonitors
            )
    
    
# PRINT WEEKLY NOTES FOR COORDINATOR (GET approach)
@app.route("/coordinatorReports/printWeeklyMonitorNotes", methods=["GET"])
def printWeeklyMonitorNotes():
    print('PRINT printWeeklyMonitorNotes routine')
    dateScheduled=request.args.get('date')
    shopNumber=request.args.get('shop')
    destination = request.args.get('destination')
      
    # GET LOCATION NAME FOR REPORT HEADING
    shopRecord = db.session.query(ShopName).filter(ShopName.Shop_Number==shopNumber).first()
    shopName = shopRecord.Shop_Name
    
    #  DETERMINE START OF WEEK DATE
    #  CONVERT TO DATE TYPE
    dateScheduledDat = datetime.strptime(dateScheduled,'%Y-%m-%d')
    dayOfWeek = dateScheduledDat.weekday()

    # GET BEGIN, END DATES FOR REPORT HEADING (Monday, Saturday)
    beginDateDAT = dateScheduledDat + timedelta(days=1)
    beginDateSTR = beginDateDAT.strftime('%m-%d-%Y')
    yyyymmdd = dateScheduledDat.strftime('%Y-%m-%d')

    endDateDAT = beginDateDAT + timedelta(days=5)
    endDateSTR = endDateDAT.strftime('%m-%d-%Y')

    weekOfHdg = dateScheduledDat.strftime('%B %d, %Y')
    
    # RETRIEVE SCHEDULE FOR SPECIFIC WEEK
    todays_date = date.today()
    todays_dateSTR = todays_date.strftime('%-m-%-d-%Y')

    # BUILD SELECT STATEMENT TO RETRIEVE NOTES FOR SPECIFIED WEEK AND LOCATION
    sqlNotes = "SELECT Date_Of_Change, convert(nvarchar,Date_Of_Change,100) as changeDateTime, "
    sqlNotes += "convert(nvarchar,Date_Of_Change,110) as changeDate, "
    sqlNotes += "convert(nvarchar,Date_Of_Change,108) as changeTime, "
    sqlNotes += "Schedule_Note, Author_ID, Initials FROM monitorWeekNotes "
    sqlNotes += "LEFT JOIN tblMember_Data on Author_ID = Member_ID "
    sqlNotes += "WHERE WeekOf = '" + yyyymmdd + "' "
    sqlNotes += "ORDER BY Date_Of_Change"
    
    notes = db.engine.execute(sqlNotes)
    
    if (destination == 'PDF') :  
        html =  render_template("rptWeeklyMonitorSchedule.html",\
            beginDate=beginDateSTR,endDate=endDateSTR,\
            locationName=shopName,notes=notes,weekOfHdg=weekOfHdg,\
            todaysDate=todays_dateSTR
            )
        return render_pdf(HTML(string=html))
    else:
        return render_template("rptWeeklyNotes.html",\
            beginDate=beginDateSTR,endDate=endDateSTR,\
            locationName=shopName,notes=notes,weekOfHdg=weekOfHdg,\
            todaysDate=todays_dateSTR
            )
        
        return redirect(url_for('/coordinatorReports/index'))
        

        # WeasyPrint solution
        # html = render_template("rptWeeklyNotes.html",\
        #     beginDate=beginDateSTR,endDate=endDateSTR,\
        #     locationName=shopName,notes=notes,weekOfHdg=weekOfHdg,\
        #     todaysDate=todays_dateSTR
        #     )
        # return render_pdf(HTML(string=html))
        #rendered = render_template('rptWeeklyNotes.html',\
        #     beginDate=beginDateSTR,endDate=endDateSTR,\
        #     locationName=shopName,notes=notes,weekOfHdg=weekOfHdg,\
        #     todaysDate=todays_dateSTR
        #     )
        # pdf = pdfkit.from_string(rendered, False)
        # response = make_response(pdf)
        # response.headers['Content-Type'] = 'application/pdf'
        # response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'

        # return response

        # pdfkit solution
        

@app.route("/coordinatorReports/printWeeklyMonitorSubs", methods=["GET"])
def printWeeklyMonitorSubs():
    flash('Not implemented.')
    return 'Not implemented.'

@app.route("/coordinatorReports/pdfWeeklyMonitorNotes")   # NOT IMPLEMENTED
def pdfWeeklyMonitorNotes():
    dateScheduled=request.args.get('date')
    shopNumber=request.args.get('shop')
    weekOf = request.form['date']
    shop =  request.form['shop']
    return


@app.route("/coordinatorReports/eMailCoordinator", methods=["GET","POST"])
def eMailCoordinator():

    # THIS ROUTINE ONLY RETURNS THE EMAIL MESSAGE TO BE USED FOR COORDINATORS ONLY EMAILS
    # ___________________________________________________________________________________

    # GET WEEKOF DATE
    # RETURN COORDINATOR NAME, EMAIL, PHONE
    # weekOf = request.args.get('weekOf')
    # shopNumber = request.args.get('shopNumber')

   # LOOK UP EMAIL MESSAGE FOR COORDINATOR
    sqlEmailMsgs = "SELECT [Email Name] as eMailMsgName, [Email Message] as eMailMessage FROM tblEmail_Messages "
    sqlEmailMsgs += "WHERE [Email Name] = 'Email To Coordinators'"
    eMailMessages = db.engine.execute(sqlEmailMsgs)
    for e in eMailMessages:
        eMailMsg=e.eMailMessage
    #print(eMailMsg)
    return jsonify(eMailMsg=eMailMsg)

@app.route("/coordinatorReports/eMailCoordinatorAndMonitors", methods=["GET","POST"])
def eMailCoordinatorAndMonitors():
    # GET WEEKOF DATE
    weekOf = request.args.get('weekOf')
    shopNumber = request.args.get('shopNumber')

    #print('weekOf - ',weekOf,type(weekOf))

    weekOfDAT = datetime.strptime(weekOf,'%Y-%m-%d')
    beginDateDAT = weekOfDAT
    beginDateSTR = beginDateDAT.strftime('%m-%d-%Y')
    endDateDAT = beginDateDAT + timedelta(days=6)
    endDateSTR = endDateDAT.strftime('%m-%d-%Y')

    #print('begin - ',beginDateSTR,' end - ',endDateSTR)
    # RETURN COORDINBATOR AND MONITORS NAMES AND EMAIL ADDRESSES; COORDINATORS PHONE
    # BUILD SELECT STATEMENT TO RETRIEVE SM MEMBERS SCHEDULE FOR CURRENT YEAR FORWARD
    sqlMonitors = "SELECT tblMember_Data.Member_ID as memberID, "
    sqlMonitors += "First_Name + ' ' + Last_Name as displayName, eMail "
    sqlMonitors += "FROM tblMember_Data "
    sqlMonitors += "LEFT JOIN tblMonitor_Schedule ON tblMonitor_Schedule.Member_ID = tblMember_Data.Member_ID "
    sqlMonitors += "WHERE Date_Scheduled between '" + beginDateSTR + "' and '" + endDateSTR + "' "
    sqlMonitors += "ORDER BY Last_Name, First_Name"
    #print(sqlMonitors)
    monitors = db.engine.execute(sqlMonitors)
    monitorDict = []
    monitorItem = []
    savedName = ''
    
    for m in monitors:
        #print(m.displayName,m.eMail)
        monitorItem = {
            'name':m.displayName,
            'eMail': m.eMail} 
        
        if savedName != m.displayName :
            monitorDict.append(monitorItem)
        savedName = m.displayName

    # LOOK UP EMAIL MESSAGE FOR COORDINATOR
    sqlEmailMsgs = "SELECT [Email Name] as eMailMsgName, [Email Message] as eMailMessage FROM tblEmail_Messages "
    sqlEmailMsgs += "WHERE [Email Name] = 'Email To Coordinator'"
    eMailMessages = db.engine.execute(sqlEmailMsgs)
    for e in eMailMessages:
        eMailMsg=e.eMailMessage

    return jsonify(monitorDict=monitorDict,eMailMsg=eMailMsg)

@app.route("/coordinatorReports/getMembersEmailAddress", methods=["GET","POST"])
def getMembersEmailAddress():
    memberID=request.args.get('memberID')
    weekOf = request.args.get('weekOf')
    shopNumber = request.args.get('shopNumber')
    weekOfDat = datetime.strptime(weekOf,'%Y-%m-%d')
    displayDate = weekOfDat.strftime('%B %d, %Y')  #'%m/%d/%Y')

    # GET MEMBER'S EMAIL ADDRESS;
    eMail=db.session.query(Member.eMail).filter(Member.Member_ID == memberID).scalar()

    # LOOK UP EMAIL MESSAGE FOR MEMBER
    eMailMsg=db.session.query(EmailMessages.eMailMessage).filter(EmailMessages.eMailMsgName == 'Email To Members').scalar()
    
    return jsonify(eMail=eMail,eMailMsg=eMailMsg,displayDate=displayDate)


# THE FOLLOWING ROUTINE IS CALLED WHEN THE USER SELECTS A WEEK
@app.route("/coordinatorReports/getCoordinatorData", methods=["GET","POST"])
def getCoordinatorData():
    # GET WEEKOF DATE
    # RETURN COORDINATOR NAME, EMAIL, PHONE
    weekOf = request.args.get('weekOf')
    shopNumber = request.args.get('shopNumber')

    weekOfDat = datetime.strptime(weekOf,'%Y-%m-%d')
    displayDate = weekOfDat.strftime('%B %d, %Y')  #'%m/%d/%Y')

    # GET COORDINATOR ID FROM COORDINATOR TABLE
    coordinatorRecord = db.session.query(CoordinatorsSchedule)\
        .filter(CoordinatorsSchedule.Start_Date==weekOf)\
        .filter(CoordinatorsSchedule.Shop_Number==shopNumber).first()
    if coordinatorRecord == None:
        coordID= ''
        coordName = 'Not assigned.'
        coordEmail = ''
        coordPhone = ''
    else:
        # LOOK UP COORDINATORS NAME
        coordinatorID = coordinatorRecord.Coordinator_ID
        memberRecord = db.session.query(Member).filter(Member.Member_ID==coordinatorID).first()
        if memberRecord == None:
            coordID = ''
            coordName = 'Not assigned.'
            coordEmail = ''
            coordPhone = ''
        else:
            coordID = memberRecord.Member_ID
            coordName = memberRecord.First_Name + ' ' + memberRecord.Last_Name
            coordEmail = memberRecord.eMail
            coordPhone = memberRecord.Cell_Phone

    return jsonify(
        coordID=coordID,
        coordName=coordName,
        coordEmail=coordEmail,
        coordPhone=coordPhone,
        displayDate=displayDate
    )

@app.route("/coordinatorReports/sendOrSaveEmail", methods=["GET","POST"])
def sendOrSaveEmail():
    # DETERMINE PATH TO PDF FILES
    currentWorkingDirectory = os.getcwd()
    pdfDirectoryPath = currentWorkingDirectory + "/app/static/pdf"
    filePath = pdfDirectoryPath + "/printWeeklyMonitorSchedule.pdf"
   
    # GET ACTION
    action = request.args.get('action')
    recipient = request.args.get('recipient')
 
    # FOR TESTING PURPOSES ..............................
    #recipient = ("Richard Hartley", "hartl1r@gmail.com")
    recipientList = []
    recipientList.append(recipient)
    # ...................................................

    subject = request.args.get('subject')
    message = request.args.get('message')
    msg = Message('Hello', sender = 'hartl1r@gmail.com', recipients = recipientList)
    msg.subject = subject
    msg.body = message


    testingAttachments = False

    # ADD ATTACHMENTS
    if testingAttachments:
        print ('.........................  ADD ATTACHMENTS  ............................')
        # DETERMINE PATH TO PDF FILES
        currentWorkingDirectory = os.getcwd()
        pdfDirectoryPath = currentWorkingDirectory + "/app/static/pdf"
        
        # CHECK FOR A SCHEDULE REPORT
        filePath = pdfDirectoryPath + "/printWeeklyMonitorSchedule.pdf"
        if (path.exists(filePath)):
            print(filePath + ' exists.')
            msg.attach(filename=filePath,disposition="attachment",content_type="application/pdf")

        # CHECK FOR A CONTACTS REPORT
        filePath = pdfDirectoryPath + "/printWeeklyMonitorContacts.pdf"
        if (path.exists(filePath)):
            print(filePath + ' exists.')
            msg.attach(filename=filePath,disposition="attachment",content_type="application/pdf")

        # CHECK FOR A NOTES REPORT
        filePath = pdfDirectoryPath + "/printWeeklyMonitorNotes.pdf"
        if (path.exists(filePath)):
            print(filePath + ' exists.')
            msg.attach(filename=filePath,disposition="attachment",content_type="application/pdf")

        # CHECK FOR A SUBS REPORT
        filePath = pdfDirectoryPath + "/printWeeklyMonitorSubs.pdf"
        if (path.exists(filePath)):
            print(filePath + ' exists.')
            msg.attach(filename=filePath,disposition="attachment",content_type="application/pdf")
        
    # EITHER 'SEND' THE EMAIL OR 'SAVE AS DRAFT'
    if (action == 'SEND'):
        mail.send(msg)
    else:
        #  save draft is not working 
        #mail.Display(True)
        #mail.Save(msg)
        mail.save(msg)
    return 'SUCCESS'