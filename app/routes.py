# routes.py

from flask import session, render_template, flash, redirect, url_for, request, jsonify, json, make_response, after_this_request
from flask-weasyprint import HTML, render_pdf
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_parse
from app.models import ShopName, Member, MemberActivity, MonitorSchedule, MonitorScheduleTransaction,\
MonitorWeekNote, CoordinatorsSchedule, ControlVariables
from app import app
from app import db
from sqlalchemy import func, case, desc, extract, select, update, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DBAPIError

import datetime as dt
from datetime import date, datetime, timedelta


#from flask_mail import Mail

#mail = Mail(app)

# @app.route('/test')
# def test():
    # TRY TO DISPLAY rptWeeklyContacts.html WITHOUT PASSING ANY PARAMETERS
    #return render_template("rptWeeklyNotes.html")
    #return render_template("rptWeeklyContacts.html")
    #return render_template("test.html")

@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    # GET REQUEST
    # BUILD ARRAY OF NAMES FOR DROPDOWN LIST OF COORDINATORS
    coordNames=[]
    sqlNames = "SELECT Last_Name + ', ' + First_Name as coordName, Member_ID as coordID FROM tblMember_Data "
    sqlNames += "WHERE Monitor_Coordinator = 1 "
    sqlNames += "ORDER BY Last_Name, First_Name "
    coordNames = db.engine.execute(sqlNames)
   
    # BUILD ARRAY OF MONITOR WEEKS FOR BOTH LOCATIONS
    sqlWeeks = "SELECT Shop_Number, Start_Date,format(Start_Date,'MMM d, yyyy') as DisplayDate, Coordinator_ID, Last_Name + ', ' + First_Name as CoordName "
    sqlWeeks += " FROM coordinatorsSchedule "
    sqlWeeks += "LEFT JOIN tblMember_Data ON coordinatorsSchedule.Coordinator_ID = tblMember_Data.Member_ID "
    sqlWeeks += "WHERE Start_Date >= getdate() "
    sqlWeeks += "ORDER BY Shop_Number, Start_Date"
    weeks = db.engine.execute(sqlWeeks)

    return render_template("index.html",coordNames=coordNames,weeks=weeks)
   



# PRINT WEEKLY MONITOR DUTY SCHEDULE FOR COORDINATOR
@app.route("/printWeeklyMonitorSchedule", methods = ['GET'])
def printWeeklyMonitorSchedule():
    dateScheduled=request.args.get('date')
    shopNumber=request.args.get('shop')
    
    ########  try to redirect to another page that contains the following code
    
    # LOOK UP SHOP NAME
    shopRecord = db.session.query(ShopName).filter(ShopName.Shop_Number==shopNumber).first()
    shopName = shopRecord.Shop_Name
    
    #  DATE SELECTED IS ALWAYS A MONDAY
    #  CONVERT TO DATE TYPE
    dateScheduledDat = datetime.strptime(dateScheduled,'%Y-%m-%d')
    #dayOfWeek = dateScheduledDat.weekday()
    # if dayOfWeek == 6:  # if Sunday
    #     dayOfWeek = 0
# beginDate should always be a sunday 
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
    

    # DETERMINE NUMBER OF ROWS NEEDED FOR EACH GROUPING - 
    # SMAM - Shop Monitor, AM shift
    # SMPM - Shop Monitor, PM shift
    # TCAM - Tool Crib, AM shift
    # TCPM - Tool Crib, PM shift
    
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
    
    return render_template("rptWeeklyMonitorSchedule.html",\
        SMAMnames=SMAMnames,SMPMnames=SMPMnames,TCAMnames=TCAMnames,TCPMnames=TCPMnames,\
        SMAMtraining=SMAMtraining,SMPMtraining=SMPMtraining,TCAMtraining=TCAMtraining,TCPMtraining=TCPMtraining,\
        SMAMrows=SMAMrows,SMPMrows=SMPMrows,TCAMrows=TCAMrows,TCPMrows=TCPMrows,\
        shopName=shopName,weekOf=beginDateSTR,coordinatorsName=coordinatorsName, coordinatorsEmail=coordinatorsEmail,\
        todays_date=todays_dateSTR,\
        monDate=monDate,tueDate=tueDate,wedDate=wedDate,thuDate=thuDate,friDate=friDate,satDate=satDate)
        



# PRINT WEEKLY LIST OF CONTACTS FOR COORDINATOR
@app.route("/printWeeklyMonitorContacts", methods=['GET'])
def printWeeklyMonitorContacts():
    dateScheduled=request.args.get('date')
    shopNumber=request.args.get('shop')

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
            

    return render_template("rptWeeklyContacts.html",\
        beginDate=beginDateSTR,endDate=endDateSTR,todaysDate=todays_dateSTR,\
        locationName=shopName,\
        SMmonitors=SMmonitors,TCmonitors=TCmonitors
        )
    
    
# PRINT WEEKLY NOTES FOR COORDINATOR (POST approach)
# @app.route("/printWeeklyMonitorNotesPOST", methods=["POST"])
# def printWeeklyMonitorNotesPOST():
#     if request.method != 'POST':
#         return 'ERROR - Not a POST request.'

#     parameters = request.get_json()
#     if parameters == None:
#         return 'ERROR - Missing parameters.'

#     dateScheduled = parameters['date']
#     if dateScheduled == None:
#         return 'ERROR - Missing date scheduled.'

#     shopNumber = parameters['shop']
#     if shopNumber == None:
#         return 'ERROR - Missing shop number.'

#     # GET LOCATION NAME FOR REPORT HEADING
#     shopRecord = db.session.query(ShopName).filter(ShopName.Shop_Number==shopNumber).first()
#     shopName = shopRecord.Shop_Name
    
#     #  DETERMINE START OF WEEK DATE
#     #  CONVERT TO DATE TYPE
#     dateScheduledDat = datetime.strptime(dateScheduled,'%Y-%m-%d')
#     dayOfWeek = dateScheduledDat.weekday()

#     # GET BEGIN, END DATES FOR REPORT HEADING
#     beginDateDAT = dateScheduledDat - timedelta(dayOfWeek + 1)
#     beginDateSTR = beginDateDAT.strftime('%m-%d-%Y')

#     endDateDAT = beginDateDAT + timedelta(days=6)
#     endDateSTR = endDateDAT.strftime('%m-%d-%Y')

#     weekOfHdg = beginDateDAT.strftime('%B %-d, %Y')
    
#     # RETRIEVE SCHEDULE FOR SPECIFIC WEEK
#     todays_date = date.today()
#     todays_dateSTR = todays_date.strftime('%-m-%-d-%Y')

#     # BUILD SELECT STATEMENT TO RETRIEVE NOTES FOR SPECIFIED WEEK AND LOCATION
#     sqlNotes = "SELECT Date_Of_Change, convert(nvarchar,Date_Of_Change,100) as changeDateTime, "
#     sqlNotes += "convert(nvarchar,Date_Of_Change,110) as changeDate, "
#     sqlNotes += "convert(nvarchar,Date_Of_Change,108) as changeTime, "
#     sqlNotes += "Schedule_Note, Author_ID, Initials FROM monitorWeekNotes "
#     sqlNotes += "left join tblMember_Data on Author_ID = Member_ID "
#     sqlNotes += "WHERE WeekOf between '" + beginDateSTR + "' and '" + endDateSTR + "' "
#     sqlNotes += "ORDER BY Date_Of_Change"
#     notes = db.engine.execute(sqlNotes)
    
#     return render_template("rptWeeklyNotes.html",\
#         beginDate=beginDateSTR,endDate=endDateSTR,\
#         locationName=shopName,notes=notes,weekOfHdg=weekOfHdg,\
#         todaysDate=todays_dateSTR
#         )
    
# PRINT WEEKLY NOTES FOR COORDINATOR (GET approach)
@app.route("/printWeeklyMonitorNotes", methods=["GET"])
def printWeeklyMonitorNotesGET():
    destination='PDF'

    dateScheduled=request.args.get('date')
    shopNumber=request.args.get('shop')
    #destination = request.args.get('destination')
      
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
    #print(sqlNotes)

    notes = db.engine.execute(sqlNotes)
    #for n in notes:
    #    print(n.Date_Of_Change,n.Schedule_Note) 
    # 
    if (destination == 'Printer') :   
        return render_template("rptWeeklyNotes.html",\
            beginDate=beginDateSTR,endDate=endDateSTR,\
            locationName=shopName,notes=notes,weekOfHdg=weekOfHdg,\
            todaysDate=todays_dateSTR
            )
    else:
        html = render_template("rptWeeklyNotes.html",\
            beginDate=beginDateSTR,endDate=endDateSTR,\
            locationName=shopName,notes=notes,weekOfHdg=weekOfHdg,\
            todaysDate=todays_dateSTR
            )
        return render_pdf(HTML(string=html))


@app.route("/printWeeklyMonitorSubs", methods=["GET"])
def printWeeklyMonitorSubs():
    flash('Not implemented.')
    return 'Not implemented.'

@app.route("/pdfWeeklyNotes<date>/<shop>")
def pdfWeeklyNotes(date,shop):
    rendered = render_template('printWeeklyNotes.html',date=date,shop=shop)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'

    return response
