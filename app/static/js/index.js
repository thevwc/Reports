//$( document ).ready (function() {
//  PAGE LOAD ROUTINES
    // Declare global variables)

    // clientLocation, staffID will be set in localStorage within login routine
    var curCoordinatorID = 'All' //UPDATED FROM COORDINATOR SELECTION
    var clientLocation = ''
    var todaysDate = new Date();
    var shopNames = ['Rolling Acres', 'Brownwood']

    // UPDATED ON LOAD AND SHOP CHANGE
    var curShopNumber = ''
    var curShopName = ''

    //UPDATED FROM WEEK CHANGE ROUTINE
    var curWeekDate = '' 
    var curWeekDisplayDate = '' 
    var curCoordinatorName = '' 
    var curCoordinatorEmail = ''
    var curCoordinatorPhone = ''
    var curManagersEmail = ''

    // UPDATED FROM SEND TO SELECTION OF 'COORDINATOR AND MONITORS'
    var curMonitorsEmailAddresses = []
    var curMonitorsNames = []


    // SET INITIAL PAGE VALUES
    // SET BACKGROUND TO OPAQUE FOR:  REPORT CHOICES, PRINT/EMAIL CHOICE, SEND TO options, and EMAIL SEND/SAVE/CLEAR options
    //clearEmailData()

    // DEFINE EVENT LISTENERS
    document.getElementById("weekSelected").addEventListener("change", weekChanged);
    document.getElementById("shopChoice").addEventListener("change", shopChanged);
    document.getElementById("coordChoice").addEventListener("change", coordinatorChanged);
    document.getElementById("selectpicker").addEventListener("change",memberSelectedRtn)

    // Note - both of these buttons link to the 'printReports' function
    document.getElementById("printReportBtn").addEventListener("click",function(){printReports('PRINT');},false);
    document.getElementById("eMailReportBtn").addEventListener("click",function(){printReports('PDF');},false);

    // TOGGLE ACTIVE CLASS FOR 'PRINT' AND 'Email PDFs' BUTTONS
    $('.prtOrEmailBtn').click(function() {
        $('button.prtOrEmailBtn.active').removeClass('active');
        $(this).addClass('active');
    })
    
    // GET STAFFID THAT WAS STORED BY THE LOGIN ROUTINE
    if (!localStorage.getItem('staffID')) {
        alert("local storage for 'staffID' is missing; 604875 is being used.")
        localStorage.setItem('staffID','604875')
    }
    staffID = localStorage.getItem('staffID')
    

    // GET clientLocation THAT WAS STORED BY THE LOGIN ROUTINE
    if (!localStorage.getItem('clientLocation')) {
        alert("local storage for 'clientLocation' is missing; RA assumed.")
        localStorage.setItem('clientLocation','RA')
    }
    clientLocation = localStorage.getItem('clientLocation')

    // SET DROP DOWN MENU INITIAL VALUES
    setShopFilter(clientLocation)
    filterTheWeeksShown()
// END PAGE LOAD ROUTINES



// BEGIN FUNCTIONS

// THE FOLLOWING ROUTINE RETRIEVES THE MESSAGE THAT IS TO BE INSERTED INTO A 'COORDINATORS ONLY' EMAIL
$('#coordinatorOnlyID').click(function(){
    // THE FOLLOWING LINE IS TEMPORARY;  THE VARIABLE curWeekDate IS BEING RESET BECAUSE AFTER THE THE WINDOW.PRINT COMMAND THE PAGE IS RELOADED
    curWeekDate = document.getElementById('weekSelected').value
    if (curWeekDate == ''){
        alert("Please select a date.")
        return 
    }
    clearEmailData() 
    $.ajax({
        url : "/coordinatorReportseMailCoordinator",
        type: "GET",
        data : {
            weekOf: curWeekDate,
            shopNumber: curShopNumber},
        success: function(data, textStatus, jqXHR)
        {
            // INSERT RECIPIENT
            document.getElementById('eMailRecipientID').value = curCoordinatorEmail
            
            // BUILD SUBJECT LINE
            subject = "Monitor Duty for Week Of " + curWeekDisplayDate + " at " + curShopName
            document.getElementById('eMailSubjectID').value=subject 

            // WRITE MESSAGE
            message = "DO NOT SEND EMAILS REGARDING MONITOR DUTY TO THE WORKSHOP.\n\n"
            message += "CALL OR EMAIL ACCORDING TO THE INSTRUCTIONS BELOW.\n"
            message += "THIS SCHEDULE IS FOR THE " + curShopName.toUpperCase() + " LOCATION\n\n"
            message += "Please remember to contact your coordinator, " + curCoordinatorName + ", if you make any changes or have questions.\n"
            message += "My phone number is " + curCoordinatorPhone + " and my Email is " + curCoordinatorEmail + "."
            message += '\n' + data.eMailMsg
            document.getElementById('eMailMsgID').value=message 

        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            alert('ERROR from eMailCoordinator')
        }
    });
})

$('#coordinatorAndMonitorsID').click(function(){
    // THE FOLLOWING LINE IS TEMPORARY;  THE VARIABLE curWeekDate IS BEING RESET BECAUSE AFTER THE THE WINDOW.PRINT COMMAND THE PAGE IS RELOADED
    curWeekDate = document.getElementById('weekSelected').value
    if (curWeekDate == ''){
        alert("Please select a date.")
        return 
    } 

    clearEmailData()
    $.ajax({
        url : "/coordinatorReportseMailCoordinatorAndMonitors",
        type: "GET",
        data : {
            weekOf: curWeekDate,
            shopNumber: curShopNumber},
        success: function(data, textStatus, jqXHR)
        {
            // COPY LIST OF MONITORS TO GLOBAL VARIABLE
            curMonitorsEmailAddresses = data.monitorDict

            // INSERT COORDINATOR'S EMAIL INTO 'TO' LINE
            document.getElementById('eMailRecipientID').value = curCoordinatorEmail
            

            // BUILD SUBJECT LINE
            subject = "Monitor Duty for Week Of " + curWeekDisplayDate + " at " + curShopName
            document.getElementById('eMailSubjectID').value=subject 

            // BUILD MESSAGE
            message = "CALL OR EMAIL ACCORDING TO THE INSTRUCTIONS BELOW.\n"
            message += "Coordinators: Please copy the email addresses below into the 'To... ' field of your email.  "
            message += "Then delete them from the text below and send the email out.\n"

            // APPEND MONITOR EMAIL ADDRESSES TO END OF MESSAGE (COORDINATORS WILL COPY THEN PASTE INTO A NEW EMAIL)
            for (i=0; i < curMonitorsEmailAddresses.length; i++) {
                message += curMonitorsEmailAddresses[i]['eMail'] + ';'
            }

            // APPEND REST OF MSG TO 'MESSAGE'
            message += "\n\nDO NOT SEND EMAILS REGARDING MONITOR DUTY TO THE WORKSHOP.\n\n"
            message += "CALL OR EMAIL ACCORDING TO THE INSTRUCTIONS BELOW"
            message += "THIS SCHEDULE IS FOR THE " + curShopName.toUpperCase() + " LOCATION\n\n"
            message += "Please remember to contact your coordinator, " + curCoordinatorName + ", if you make any changes or have questions.\n"
            message += "My phone number is " + curCoordinatorPhone + " and my Email is " + curCoordinatorEmail + "."
            message += '\n' + data.eMailMsg + '\n'
            // COPY 'MESSAGE' TO FORM
            document.getElementById('eMailMsgID').value=message 

        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            alert('ERROR from eMailCoordinatorAndMonitors\n'+textStatus+'\n' + errorThrown)
        }
    });
})
    
// RESPOND TO CLICK OF ONE OF THE EMAIL BUTTONS
// SET ACTIVE BUTTON; EXECUTE 'SEND', 'SAVE', OR 'CLEAR' FUNCTION
// DEPENDING ON WHICH BUTTON WAS CLICKED
$('.eMailBtn').click(function() {
    
    // REMOVE 'ACTIVE' FROM BUTTONS
    $('button.eMailBtn.active').removeClass('active');
    
    // ADD ACTIVE TO BUTTON JUST CLICKED
    $(this).addClass('active');

    // CALL APPROPRIATE FUNCTION
    if (this.id == 'sendBtn') {
        console.log('sendBtn')
        sendOrSaveEmail('SEND')
    }
    if (this.id == 'saveBtn') {
        console.log('saveBtn')
        sendOrSaveEmail('SAVE')
    }
    if (this.id == 'clearBtn') {
        console.log('clearBtn')
        clearEmailData()
    }
})


// CLEAR THE EMAIL FORM; SET OPACITY TO .2
function clearEmailData() {
    curMonitorEmailAddresses = []
    document.getElementById('eMailRecipientID').value = ''
    document.getElementById('eMailSubjectID').value=''
    document.getElementById('eMailMsgID').value=''
    hideEmailForm()
}

function printReports(destination) {
    if (destination == 'PDF'){
        showEmailForm()
    }
    // THE FOLLOWING LINE IS TEMPORARY;  THE VARIABLE curWeekDate IS BEING RESET BECAUSE AFTER THE THE WINDOW.PRINT COMMAND THE PAGE IS RELOADED
    curWeekDate = document.getElementById('weekSelected').value
    if (curWeekDate == '') {
        alert("Please select a week date.")
        return
    }

    shopInitials = document.getElementById('shopChoice').value
    if (shopInitials == '') {
        alert("Please select a location.")
        return
    }
    if (shopInitials == 'RA') {
        curShopNumber = '1'
    }
    else {
        curShopNumber = '2'
    }

    reportSelected = false
    
    // SET UP APPROPRIATE LINKS FOR scheduleBtn, notesBtn, contactsBtn, and subsBtn
    var scheduleBtn = document.getElementById('printScheduleLink');
    link='/coordinatorReports/printWeeklyMonitorSchedule?date=' + curWeekDate + '&shop=' + curShopNumber + '&destination=' + destination
    scheduleBtn.setAttribute('href', link)
    
    var notesBtn = document.getElementById('printNotesLink');
    link='/coordinatorReports/printWeeklyMonitorNotes?date=' + curWeekDate + '&shop=' + curShopNumber + '&destination=' + destination
    notesBtn.setAttribute('href', link)

    var contactsBtn = document.getElementById('printContactsLink');
    link='/coordinatorReports/printWeeklyMonitorContacts?date=' + curWeekDate + '&shop=' + curShopNumber + '&destination=' + destination
    contactsBtn.setAttribute('href', link)

    var subsBtn = document.getElementById('printSubsLink');
    link='/coordinatorReports/printWeeklyMonitorSubs?date='  + curWeekDate + '&shop=' + curShopNumber + '&destination=' + destination
    subsBtn.setAttribute('href', link)
    
    if (document.getElementById('scheduleID').checked) {
        reportSelected = true
        scheduleBtn.click()
    }

    if (document.getElementById('notesID').checked) {
        reportSelected = true
        notesBtn.click()
    }
    if (document.getElementById('contactsID').checked) {
        reportSelected = true
        contactsBtn.click()
    }
    if (document.getElementById('subsID').checked) {
        alert('This report is not available at this time.')
        reportSelected = true
        //subsBtn.click()
    }

    if (reportSelected != true) {
        alert('No reports have been selected.')
        return
    }
}

function myFunction() {
    document.getElementById("demo").innerHTML = "Hello World";
  }

// function emailReports() {
//     alert('Not implemented')
// }

function shopChanged() {
    setShopFilter(this.value)
    filterTheWeeksShown()
}

function setShopFilter(shopLocation) {
    //alert('setShopFilter contains - '+ shopLocation)
    switch(shopLocation){
        case 'RA':
            localStorage.setItem('shopFilter','RA')
            document.getElementById("shopChoice").selectedIndex = 0; //optItemion Rolling Acres
            shopFilter = 'RA'
            curShopNumber = '1'
            curShopName = shopNames[0]
            break;
        case 'BW':
            localStorage.setItem('shopFilter','BW')
            document.getElementById("shopChoice").selectedIndex = 1; //optItemion Brownwood
            shopFilter = 'BW'
            curShopNumber = '2'
            curShopName = shopNames[1]
            break;
        default:
            alert('Missing local storage variable for shop location; RA assumed')
            localStorage.setItem('shopFilter','RA')
            document.getElementById("shopChoice").selectedIndex = 0; //optItemion Rolling Acres
            shopFilter = 'RA'
            curShopNumber = '1'
            curShopName = shopNames[0]
    } 
    //alert('shopName is now - '+ curShopName)  
}


function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();
    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;
    yyyymmdd = year + month + day
    return yyyymmdd;
}

 // FILTER WEEKS DROPDOWN ON SHOPNUMBER AND COORDINATOR ID
function filterTheWeeksShown() {
    var weeks = document.querySelectorAll('.optWeeks')
    for (i=0; i < weeks.length; i++) {
        thisWeeksCoordID = weeks[i].getAttribute('data-coordID')
        shop = weeks[i].getAttribute('data-shop')
        if ((shop == curShopNumber && curCoordinatorID == 'All')
        || (shop == curShopNumber && thisWeeksCoordID == curCoordinatorID)){
            weeks[i].style.display = ''
        }
        else {
            weeks[i].style.display = 'none'
            continue
        }
    }
}
  

function weekChanged () {
    curWeekDate = this.value
    showEmailForm()

    // RETRIEVE COORDINATOR INFORMATION FROM SERVER
    $.ajax({
        url : "/coordinatorReports/getCoordinatorData",
        type: "GET",
        data : {
            weekOf: curWeekDate,
            shopNumber: curShopNumber},
        success: function(data, textStatus, jqXHR)
        {
            curCoordinatorID = data.coordID 
            curCoordinatorName = data.coordName
            curCoordinatorEmail = data.coordEmail
            curCoordinatorPhone = data.coordPhone
            curManagersEmail = data.curManagersEmail
            curWeekDisplayDate = data.displayDate

            // BUILD MESSAGE FOR coordinatorInfoID
            if (curCoordinatorID != '') {
                //document.getElementById('coordinatorHeading').innerHTML = ''
                document.getElementById('coordHdgBeforeDate').innerHTML = "The coordinator for the week of " 
                document.getElementById('coordHdgDate').innerHTML = curWeekDisplayDate 
                document.getElementById('coordHdgBeforeName').innerHTML = ' is ' 
                document.getElementById('coordHdgName').innerHTML = curCoordinatorName 
                document.getElementById('coordHdgBeforePhone').innerHTML = ' and may be contacted at '
                document.getElementById('coordHdgPhone').innerHTML = curCoordinatorPhone 
                document.getElementById('coordHdgBeforeEmail').innerHTML = ' or by email at '
                document.getElementById('coordHdgEmailLink').href = 'mailto:' + curCoordinatorEmail
                document.getElementById('coordHdgEmailLink').innerHTML = curCoordinatorEmail
            }
            else {
                document.getElementById('coordHdgBeforeDate').innerHTML = "A coordinator has not been assigned for this week."
                document.getElementById('coordHdgDate').innerHTML = ''
                document.getElementById('coordHdgBeforeName').innerHTML = '' 
                document.getElementById('coordHdgName').innerHTML = ''
                document.getElementById('coordHdgBeforePhone').innerHTML = ''
                document.getElementById('coordHdgPhone').innerHTML = ''
                document.getElementById('coordHdgBeforeEmail').innerHTML = ''
                document.getElementById('coordHdgEmailLink').href = '#'
                document.getElementById('coordHdgEmailLink').innerHTML = ''
            }
    
            //alert('success from getCoordinatorData')   
        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            alert('ERROR from getCoordinatorData')
        }
    });
    }

    function coordinatorChanged () {
        curCoordinatorID = this.value
        filterTheWeeksShown()
    }

    function memberSelectedRtn() {
        selectedMember = this.value
        lastEight = selectedMember.slice(-8)
        curMemberID= lastEight.slice(1,7)

        // THE FOLLOWING LINE IS TEMPORARY;  THE VARIABLE curWeekDate IS BEING RESET BECAUSE AFTER THE THE WINDOW.PRINT COMMAND THE PAGE IS RELOADED
        curWeekDate = document.getElementById('weekSelected').value
        
        // REQUEST MEMBER's EMAIL ADDRESS FROM SERVER
        $.ajax({
            url : "/coordinatorReports/getMembersEmailAddress",
            type: "GET",
            data : {memberID: curMemberID,
                    weekOf: curWeekDate,
                    shopNumber: curShopNumber},

            success: function(data, textStatus, jqXHR)
            { 
                clearEmailData() 
                // INSERT RECIPIENT EMAIL ADDRESS
                document.getElementById('eMailRecipientID').value = data.eMail

                // BUILD SUBJECT LINE
                subject = "Monitor Duty for Week Of " + curWeekDisplayDate + " at " + curShopName
                document.getElementById('eMailSubjectID').value=subject 

                // BUILD MESSAGE
                message = data.eMailMsg
                document.getElementById('eMailMsgID').value=message 

            },
            
            error: function (jqXHR, textStatus, errorThrown)
            {
                alert('ERROR from getMembersEmailAddress\n'+textStatus+'\n' + errorThrown)
            }
        })
    }


    function sendOrSaveEmail(action) {
        $.ajax({
            url : "/coordinatorReportssendOrSaveEmail",
            type: "GET",
            data : {
                action: action,
                recipient:document.getElementById('eMailRecipientID').value,
                subject:document.getElementById('eMailSubjectID').value,
                message:document.getElementById('eMailMsgID').value
            },
            success: function(data, textStatus, jqXHR)
            {
                alert(data)

            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                alert('ERROR from eMailCoordinator')
            }
        });
    }
    

function showEmailForm() {
    document.getElementById('rptChoices').style.opacity=1;
    document.getElementById('prtReports').style.opacity=1;
    document.getElementById('sendToOptions').style.opacity=1;
    document.getElementById('emailButtons').style.opacity=1;
}

function hideEmailForm() {
    document.getElementById('rptChoices').style.opacity=.2;
    document.getElementById('prtReports').style.opacity=.2;
    document.getElementById('sendToOptions').style.opacity=.2;
    document.getElementById('emailButtons').style.opacity=.2;
}
// END OF FUNCTIONS
