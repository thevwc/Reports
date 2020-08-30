# routes.py

from flask import session, render_template, flash, redirect, url_for, request, jsonify, json, make_response, after_this_request
#from flask_weasyprint import HTML, render_pdf
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

    # MEMBER NAMES AND ID
    sqlMembers = "SELECT Last_Name + ', ' + First_Name + ' (' + Member_ID + ')' as name, eMail FROM tblMember_Data "
    sqlMembers += "ORDER BY Last_Name, First_Name "
    nameList = db.engine.execute(sqlMembers)
    
    return render_template("index.html",coordNames=coordNames,weeks=weeks,nameList=nameList)  #,eMails=eMails)
   



#PRINT WEEKLY MONITOR DUTY SCHEDULE FOR COORDINATOR
@app.route("/coordinatorReports/printWeeklyMonitorSchedule", methods = ['GET'])
def printWeeklyMonitorSchedule():
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
            coordinatorsEmail = ''
            coordinatorsName = '(' + str(coordinatorID) + ')'
        else:
            coordinatorsEmail = memberRecord.eMail
            if memberRecord.NickName != None and memberRecord.NickName != '':
                coordinatorsName = memberRecord.First_Name + ' ' + memberRecord.Last_Name + ' (' + memberRecord.NickName + ')'
            else:
                coordinatorsName = memberRecord.First_Name + ' ' + memberRecord.Last_Name
        
    
    
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
    
    # BUILD SELECT STATEMENT TO RETRIEVE TC MEMBERS SCHEDULE FOR CURRENT YEAR FORWARD
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
        filePath = pdfDirectoryPath + "/rptWeeklyMonitorSchedule.pdf"
        options = { 
            "enable-local-file-access": None
        }
        pdfkit.from_string(html,filePath, options=options)
        return redirect(url_for('index'))
        
        # USE THE FOLLOWING TO RENDER PDF TO SCREEN
        #return render_pdf(html(string=html))
    else:
        return render_template("rptWeeklyMonitorSchedule.html",\
            SMAMnames=SMAMnames,SMPMnames=SMPMnames,TCAMnames=TCAMnames,TCPMnames=TCPMnames,\
            SMAMtraining=SMAMtraining,SMPMtraining=SMPMtraining,TCAMtraining=TCAMtraining,TCPMtraining=TCPMtraining,\
            SMAMrows=SMAMrows,SMPMrows=SMPMrows,TCAMrows=TCAMrows,TCPMrows=TCPMrows,\
            shopName=shopName,weekOf=beginDateSTR,coordinatorsName=coordinatorsName, coordinatorsEmail=coordinatorsEmail,\
            todays_date=todays_dateSTR,\
            monDate=monDate,tueDate=tueDate,wedDate=wedDate,thuDate=thuDate,friDate=friDate,satDate=satDate)
            

#PRINT WEEKLY LIST OF CONTACTS FOR COORDINATOR
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
        #html =  render_template("rptWeeklyMonitorSchedule.h
        html = render_template("rptWeeklyContacts.html",\
            beginDate=beginDateSTR,endDate=endDateSTR,todaysDate=todays_dateSTR,\
            locationName=shopName,\
            SMmonitors=SMmonitors,TCmonitors=TCmonitors
            )
        # DEFINE PATH TO USE TO STORE PDF
        currentWorkingDirectory = os.getcwd()
        pdfDirectoryPath = currentWorkingDirectory + "/app/static/pdf"
        filePath = pdfDirectoryPath + "/rptWeeklyContacts.pdf"
        options = { 
            "enable-local-file-access": None
        }
        pdfkit.from_string(html,filePath, options=options)
        return redirect(url_for('index'))
    else:
        return render_template("rptWeeklyContacts.html",\
            beginDate=beginDateSTR,endDate=endDateSTR,todaysDate=todays_dateSTR,\
            locationName=shopName,\
            SMmonitors=SMmonitors,TCmonitors=TCmonitors
            )
    
    
#PRINT WEEKLY NOTES FOR COORDINATOR 
@app.route("/coordinatorReports/printWeeklyMonitorNotes", methods=["GET"])
def printWeeklyMonitorNotes():
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
        html =  render_template("rptWeeklyNotes.html",\
            beginDate=beginDateSTR,endDate=endDateSTR,\
            locationName=shopName,notes=notes,weekOfHdg=weekOfHdg,\
            todaysDate=todays_dateSTR
            )
        currentWorkingDirectory = os.getcwd()
        pdfDirectoryPath = currentWorkingDirectory + "/app/static/pdf"
        filePath = pdfDirectoryPath + "/rptWeeklyNotes.pdf"    
        options = {"enable-local-file-access": None}
        pdfkit.from_string(html,filePath, options=options)
        return redirect(url_for('index'))
    else:
        return render_template("rptWeeklyNotes.html",\
            beginDate=beginDateSTR,endDate=endDateSTR,\
            locationName=shopName,notes=notes,weekOfHdg=weekOfHdg,\
            todaysDate=todays_dateSTR
            )
        

@app.route("/coordinatorReports/printSubList", methods=["GET"])
def printSubList():
    destination = request.args.get('destination')
    todays_date = date.today()
    todays_dateSTR = todays_date.strftime('%-m-%-d-%Y')
    thisYear = todays_date.strftime('%Y')
    janFirstSTR = thisYear + '0101'
    janFirst = datetime.strptime(janFirstSTR,'%Y%m%d')

    # BUILD ARRAY OF NAMES OF MONITOR SUBS
    sqlSubs = "SELECT Last_Name, First_Name, Nickname, Member_ID,"
    sqlSubs += " Cell_Phone, Home_Phone, eMail, Last_Monitor_Training, Monitor_Duty_Waiver_Expiration_Date,"
    sqlSubs += " format(Monitor_Duty_Waiver_Expiration_Date,'yyyy-MM-dd') as Waiver_Expiration_Date, Restricted_From_Shop,"
    sqlSubs += " Reason_For_Restricted_From_Shop, Requires_Tool_Crib_Duty,"
    sqlSubs += " Certified, Certification_Training_Date, Certified_2, Certification_Training_Date_2,"
    sqlSubs += " Monitor_Duty_Notes,"
    sqlSubs += " Jan_Resident as Jan, Feb_Resident as Feb, Mar_Resident as Mar,"
    sqlSubs += " Apr_Resident as Apr, May_Resident as May, Jun_Resident as Jun,"
    sqlSubs += " Jul_Resident as Jul, Aug_Resident as Aug, Sep_Resident as Sep,"
    sqlSubs += " Oct_Resident as Oct, Nov_Resident as Nov, Dec_Resident as Dec"
    sqlSubs += " FROM tblMember_Data"
    sqlSubs += " WHERE Monitor_Sub = 1 and Dues_Paid = 1"
    sqlSubs += " ORDER BY Last_Name, First_Name " 
    subs = db.engine.execute(sqlSubs)
    
    subDict = []
    subItem = []
    
    for s in subs:
        memberID = s.Member_ID
       
        # CONCATENATE NICKNAME WITH LAST AND FIRST NAME
        displayName = s.Last_Name + ', ' + s.First_Name
        if s.Nickname != None:
            displayName += ' ('+s.Nickname+')'

        # DETERMINE IF TRAINING IS NEEDED
        hasWaiver = False
        if (s.Waiver_Expiration_Date != None):
            waiverDate = s.Monitor_Duty_Waiver_Expiration_Date.date()
            if (waiverDate > todays_date):
                hasWaiver = True
                trainingNeededTxt=''
            
        if hasWaiver == False:
            if TrainingNeeded(s.Last_Monitor_Training):
                trainingNeededTxt='TRAINING NEEDED'
            else:
                trainingNeededTxt=''
                
        # CHECK IF TOOL CRIB DUTY REQUIRED
        if s.Requires_Tool_Crib_Duty:
            toolCribRequested='TOOL CRIB REQUESTED'
        else:
            toolCribRequested=''

        # CHECK IF RESTRICTED FROM SHOP
        if s.Restricted_From_Shop:
            restricted = 'RESTRICTED'
        else:
            restricted = ''
        if s.Reason_For_Restricted_From_Shop == None:
            reasonRestricted = ''
        else:
            reasonRestricted = s.Reason_For_Restricted_From_Shop

        # FORMAT DATE CERTIFIED
        if s.Certification_Training_Date == None:
            certifiedDateRA = ' '
        else:
            certifiedDateRA = s.Certification_Training_Date.strftime('%m/%d/%Y')
        if s.Certification_Training_Date_2 == None:
            certifiedDateBW = ' '
        else:
            certifiedDateBW = s.Certification_Training_Date_2.strftime('%m/%d/%Y')

        # CHECK FOR MONITOR DUTY NOTES
        if s.Monitor_Duty_Notes:
            monitorDutyNotes = s.Monitor_Duty_Notes
        else:
            monitorDutyNotes = ''

        # COMBINE MONTHS IN VILLAGES
        monthsStr = ''
        if s.Jan == True:
            monthsStr =' Jan '
        else:
            monthsStr = ' -  '
        if s.Feb == True:
            monthsStr +='Feb '
        else:
            monthsStr += ' -  '
        if s.Mar == True:
            monthsStr +='Mar '
        else:
            monthsStr += ' -  '
        if s.Apr == True:
            monthsStr +='Apr '
        else:
            monthsStr += ' -  '
        if s.May == True:
            monthsStr +='May '
        else:
            monthsStr += ' -  '
        if s.Jun == True:
            monthsStr +='Jun '
        else:
            monthsStr += ' -  '
        if s.Jul == True:
            monthsStr +='Jul '
        else:
            monthsStr += ' -  '
        if s.Aug == True:
            monthsStr +='Aug '
        else:
            monthsStr += ' -  '
        if s.Sep == True:
            monthsStr +='Sep '
        else:
            monthsStr += ' -  '
        if s.Oct == True:
            monthsStr +='Oct '
        else:
            monthsStr += ' -  '
        if s.Nov == True:
            monthsStr +='Nov '
        else:
            monthsStr += ' -  '
        if s.Dec == True:
            monthsStr +='Dec '
        else:
            monthsStr += ' -  '
        


        # GET NUMBER OF PAST MONITOR DUTY ASSIGNMENTS
        completedShifts = db.session.query(func.count(MonitorSchedule.Member_ID))\
            .filter(MonitorSchedule.Member_ID == memberID)\
            .filter(MonitorSchedule.No_Show == False)\
            .filter(MonitorSchedule.Date_Scheduled < todays_date)\
            .filter(MonitorSchedule.Date_Scheduled > janFirst).scalar()
            

        # GET NUMBER OF FUTURE MONITOR DUTY ASSIGNMENTS (SINCE JANUARY 1)
        futureShifts = db.session.query(func.count(MonitorSchedule.Member_ID))\
            .filter(MonitorSchedule.Member_ID == memberID)\
            .filter(MonitorSchedule.Date_Scheduled > todays_date).scalar()

        # BUILD DICTIONARY OF MEMBERS AND RELATED DATA
        subItem = {
            'name':displayName,
            'memberID':memberID,
            'eMail': s.eMail,
            'cellPhone':s.Cell_Phone,
            'homePhone':s.Home_Phone,
            'trainingNeeded':trainingNeededTxt,
            'restricted':restricted,
            'reasonRestricted':reasonRestricted,
            'toolCribRequested':toolCribRequested,
            'certifiedRA':s.Certified,
            'dateCertifiedRA':certifiedDateRA,
            'certifiedBW':s.Certified_2,
            'dateCertifiedBW':certifiedDateBW,
            'completedShifts':completedShifts,
            'futureShifts':futureShifts,
            'monitorDutyNotes':monitorDutyNotes,
            'monthsStr':monthsStr,
            'Jan':s.Jan,
            'Feb':s.Feb,
            'Mar':s.Mar,
            'Apr':s.Apr,
            'May':s.May,
            'Jun':s.Jun,
            'Jul':s.Jul,
            'Aug':s.Aug,
            'Sep':s.Sep,
            'Oct':s.Oct,
            'Nov':s.Nov,
            'Dec':s.Dec,}
        subDict.append(subItem)
        
    if (destination == 'PDF') :  
        html =  render_template("rptSubList.html",\
            todaysDate=todays_dateSTR,subDict=subDict
            )
        currentWorkingDirectory = os.getcwd()
        pdfDirectoryPath = currentWorkingDirectory + "/app/static/pdf"
        filePath = pdfDirectoryPath + "/rptSubList.pdf"
        options = {"enable-local-file-access": None}
        pdfkit.from_string(html,filePath, options=options)
        return redirect(url_for('index'))  
        
    else:
        return render_template("rptSubList.html",\
            todaysDate=todays_dateSTR,subDict=subDict
            )
        
    return redirect(url_for('/coordinatorReports/index'))
    


@app.route("/coordinatorReports/eMailCoordinator", methods=["GET","POST"])
def eMailCoordinator():
    print('... begin /coordinatorReports/eMailCoordinator')
    # THIS ROUTINE ONLY RETURNS THE EMAIL MESSAGE TO BE USED FOR COORDINATORS ONLY EMAILS
    # ___________________________________________________________________________________

   # LOOK UP MESSAGE TO BE USED FOR EMAILS TO COORDINATORS
    sqlEmailMsgs = "SELECT [Email Name] as eMailMsgName, [Email Message] as eMailMessage FROM tblEmail_Messages "
    sqlEmailMsgs += "WHERE [Email Name] = 'Email To Coordinators'"
    eMailMessages = db.engine.execute(sqlEmailMsgs)
    for e in eMailMessages:
        eMailMsg=e.eMailMessage

    return jsonify(eMailMsg=eMailMsg)

@app.route("/coordinatorReports/eMailCoordinatorAndMonitors", methods=["GET","POST"])
def eMailCoordinatorAndMonitors():
    # GET WEEKOF DATE
    weekOf = request.args.get('weekOf')
    shopNumber = request.args.get('shopNumber')

    weekOfDAT = datetime.strptime(weekOf,'%Y-%m-%d')
    beginDateDAT = weekOfDAT
    beginDateSTR = beginDateDAT.strftime('%m-%d-%Y')
    endDateDAT = beginDateDAT + timedelta(days=6)
    endDateSTR = endDateDAT.strftime('%m-%d-%Y')

    # RETURN COORDINBATOR AND MONITORS NAMES AND EMAIL ADDRESSES; COORDINATORS PHONE
    # BUILD SELECT STATEMENT TO RETRIEVE SM MEMBERS SCHEDULE FOR CURRENT YEAR FORWARD
    sqlMonitors = "SELECT tblMember_Data.Member_ID as memberID, "
    sqlMonitors += "First_Name + ' ' + Last_Name as displayName, eMail "
    sqlMonitors += "FROM tblMember_Data "
    sqlMonitors += "LEFT JOIN tblMonitor_Schedule ON tblMonitor_Schedule.Member_ID = tblMember_Data.Member_ID "
    sqlMonitors += "WHERE Date_Scheduled between '" + beginDateSTR + "' and '" + endDateSTR + "' "
    sqlMonitors += "ORDER BY Last_Name, First_Name"
   
    monitors = db.engine.execute(sqlMonitors)
    monitorDict = []
    monitorItem = []
    savedName = ''
    
    for m in monitors:
        monitorItem = {
            'name':m.displayName,
            'eMail': m.eMail} 
        
        if savedName != m.displayName :
            monitorDict.append(monitorItem)
        savedName = m.displayName

    # LOOK UP EMAIL MESSAGE FOR COORDINATOR
    sqlEmailMsgs = "SELECT [Email Name] as eMailMsgName, [Email Message] as eMailMessage FROM tblEmail_Messages "
    sqlEmailMsgs += "WHERE [Email Name] = 'Email To Coordinators'"
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
    
    return jsonify(eMail=eMail,eMailMsg=eMailMsg,curWeekDisplayDate=displayDate)


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
        curWeekDisplayDate=displayDate
    )

@app.route("/coordinatorReports/sendEmail", methods=["GET","POST"])
def sendEmail():
    # DETERMINE PATH TO PDF FILES
    currentWorkingDirectory = os.getcwd()
    pdfDirectoryPath = currentWorkingDirectory + "/app/static/pdf"
    filePath = pdfDirectoryPath + "/printWeeklyMonitorSchedule.pdf"
   
    # GET RECIPIENT
    recipient = request.args.get('recipient')
    bcc=("Woodshop","villagesWoodShop@embarqmail.com")
    #cc=("Richard l. Hartley","hartl1r@gmail.com")
    # FOR TESTING PURPOSES ..............................
    recipient = ("Richard Hartley", "hartl1r@gmail.com")

    recipientList = []
    recipientList.append(recipient)
    subject = request.args.get('subject')
    message = request.args.get('message')
    msg = Message('Hello', sender = 'hartl1r@gmail.com', recipients = recipientList) #, bcc=bcc)
    msg.subject = subject
    msg.body = message

    # ADD ATTACHMENTS

    # DETERMINE PATH TO PDF FILES
    currentWorkingDirectory = os.getcwd()
    pdfDirectoryPath = currentWorkingDirectory + "/app/static/pdf"
    
    # CHECK FOR A SCHEDULE REPORT
    filePath = pdfDirectoryPath + "/rptWeeklyMonitorSchedule.pdf"
    if (path.exists(filePath)):
        with app.open_resource(filePath) as fp:
            msg.attach(filename="rptSchedule.pdf",disposition="attachment",content_type="application/pdf",data=fp.read())

    # CHECK FOR A CONTACTS REPORT
    filePath = pdfDirectoryPath + "/rptWeeklyContacts.pdf"
    if (path.exists(filePath)):
        with app.open_resource(filePath) as fp:
            msg.attach(filename="rptContacts.pdf",disposition="attachment",content_type="application/pdf",data=fp.read())

    # CHECK FOR A NOTES REPORT
    filePath = pdfDirectoryPath + "/rptWeeklyNotes.pdf"
    if (path.exists(filePath)):
        with app.open_resource(filePath) as fp:
            msg.attach(filename="rptNotes.pdf",disposition="attachment", content_type ="application/pdf",data=fp.read())

    # CHECK FOR A SUB LIST REPORT
    filePath = pdfDirectoryPath + "/rptSubList.pdf"
    if (path.exists(filePath)):  
        with app.open_resource(filePath) as fp:
            msg.attach(filename="rptSubList.pdf",disposition="attachment",content_type="application/pdf",data=fp.read())

    
    # SEND THE EMAIL
    mail.send(msg)
    RemovePDFfiles(pdfDirectoryPath)
    #flash ('Message sent.','SUCCESS')
    return redirect(url_for('index'))


def RemovePDFfiles(pdfDirectoryPath):
    # REMOVE PDF FILES
    
    filePath = pdfDirectoryPath + "/rptWeeklyMonitorSchedule.pdf"
    if (os.path.exists(filePath)):
        os.remove(filePath)
    
    filePath = pdfDirectoryPath + "/rptWeeklyContacts.pdf"
    if (os.path.exists(filePath)):
        os.remove(filePath)

    filePath = pdfDirectoryPath + "/rptWeeklyNotes.pdf"
    if (os.path.exists(filePath)):
        os.remove(filePath)

    filePath = pdfDirectoryPath + "/rptSubList.pdf"
    if (os.path.exists(filePath)):
        os.remove(filePath)

def TrainingNeeded(lastTrainingDate): 
    todays_date = date.today()
    todays_dateSTR = todays_date.strftime('%-m-%-d-%Y')
    thisYear = todays_date.strftime("%Y")
    lastAcceptableTrainingYear = int(thisYear) - 2
    
    if lastTrainingDate == None:
        return True
    
    try:
        lastTrainingYear = lastTrainingDate.strftime("%Y")
        if int(lastTrainingYear) <= lastAcceptableTrainingYear:
            return True
        else:
            return False
    except:
        print ('Error in TrainingNeeded routine using - ', lastTrainingDate)
        return True

