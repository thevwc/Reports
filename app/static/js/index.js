//$( document ).ready (function() {
//    $( "p" ).text( "The DOM is now loaded and can be manipulated." );
    // Declare global variables)

    // clientLocation, staffID will be set in localStorage within login routine
    var curCoordinatorID = 'All' //UPDATED FROM COORDINATOR SELECTION
    var clientLocation = ''
    var todaysDate = new Date();
    var shopNames = ['Rolling Acres', 'Brownwood']

    var curShopNumber = ''
    var curWeekDate = ''  //UPDATED FROM WEEK DROPDOWN 
    
    var curCoordinatorName = '' //UPDATED FROM COORDINATOR SELECTION
    var curRecipient = ''
    var curMultipleRecipients = []

    // DEFINE EVENT LISTENERS
    document.getElementById("weekSelected").addEventListener("change", weekChanged);
    document.getElementById("weekSelected").addEventListener("click", weekChanged);

    document.getElementById("shopChoice").addEventListener("click", shopClicked);
    document.getElementById("coordChoice").addEventListener("change", coordinatorChanged);

    // Note - both of these buttons link to the 'printReports' function
    document.getElementById("printReportBtn").addEventListener("click",function(){printReports('PRINT');},false);
    document.getElementById("eMailReportBtn").addEventListener("click",function(){printReports('PDF');},false);

    //document.getElementById("coordinatorOnly").addEventListener("click",coordinatorOnly);
    //document.getElementById("coordinatorAndMonitors").addEventListener("click",coordinatorAndMonitors);
    //document.getElementById("memberOnly").addEventListener("click",memberOnly);
    

    if (!localStorage.getItem('staffID')) {
        localStorage.setItem('staffID','111111')
    }
    staffID = localStorage.getItem('staffID')
    

    // IF clientLocation IS NOT FOUND IN LOCAL STORAGE
    // THEN PROMPT WITH MODAL FORM FOR LOCATION AND YEAR
    if (!clientLocation) {
        localStorage.setItem('clientLocation','RA')
    }
    clientLocation = localStorage.getItem('clientLocation')
    console.log('on page load the variable curCoordinatorID-',curCoordinatorID)
    setShopFilter(clientLocation)
    filterWeeksShown()

    // SET EMAILSECTION TO OPAQUE
    //document.getElementById('emailSection').style.opacity=.2;
    //alert('opacity set to .2')
    //document.getElementById("emailSection").style.display= 'None'
    
    $('#coordinatorOnlyID').click(function(){ 
        $.ajax({
            url : "/eMailCoordinator",
            type: "GET",
            data : {
                weekOf: curWeekDate,
                shopNumber: curShopNumber},
            success: function(data, textStatus, jqXHR)
            {
                alert(data.coordName + '\n' + data.coordID + '\n' + data.coordEmail + '\n' + data.coordPhone
                + '\n' + data.displayDate + '\n' + data.shopName + '\n' + data.eMailMsg)
                // WRITE RECIPIENT
                curRecipient = data.coordEmail

                // BUILD SUBJECT LINE
                subject = "Monitor Duty for Week Of " + data.displayDate + " at " + data.shopName
                document.getElementById('eMailSubjectID').value=subject 

                // WRITE MESSAGE
                message = "DO NOT SEND EMAILS REGARDING MONITOR DUTY TO THE WORKSHOP.\n\n"
                message += "CALL OR EMAIL ACCORDING TO THE INSTRUCTIONS BELOW.\n"
                message += "THIS SCHEDULE IS FOR THE " + data.shopName.toUpperCase() + " LOCATION\n\n"
                message += "Please remember to contact your coordinator, " + data.coordName + ", if you make any changes or have questions.\n"
                message += "My phone number is " + data.coordPhone + " and my Email is " + data.coordEmail + "."
                message += '\n' + data.eMailMsg
                alert (message)
                document.getElementById('eMailMsgID').value=message 

            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                alert('ERROR from eMailCoordinator')
            }
        });
    })
    
    $('#coordinatorAndMonitorsID').click(function(){ 
        $.ajax({
            url : "/eMailCoordinatorAndMonitors",
            type: "POST",
            data : {
                weekOf: curWeekDate,
                shopNumber: curShopNumber},
            success: function(data, textStatus, jqXHR)
            {
                alert('success from eMailCoordinatorAndMonitors')
                //data - response from server
                // receive coordName, coordEmail, coordPhone
                
            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                alert('ERROR from eMailCoordinator')
            }
        });
    })

    $('#memberOnlyID').click(function(){ 
        $.ajax({
            url : "/eMailMember",
            type: "POST",
            data : {
                memberID:curMemberID,
                weekOf: curWeekDate,
                shopNumber: curShopNumber
            },
            success: function(data, textStatus, jqXHR)
            {
                alert('success from eMailMember')
                //data - response from server
                // receive coordName, coordEmail, coordPhone
                
            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                alert('ERROR from eMailCoordinator')
            }
        });
    })
    
    
 
// ------------------------------------------------------------------------------------------------------
// FUNCTIONS    
// ------------------------------------------------------------------------------------------------------
function printReports(destination) {
    console.log("printReports")
    //alert('printReports') 
    if (destination == 'PDF'){
        console.log('set opacity = 1')
        //document.getElementById('emailSection').opacity=1
        document.getElementById('emailSection').style.opacity=1
    }

    //curWeekDate = document.getElementById('weekSelected').value
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
    
    var scheduleBtn = document.getElementById('printScheduleLink');
    link='/printWeeklyMonitorSchedule?date=' + curWeekDate + '&shop=' + curShopNumber + '&destination=' + destination
    scheduleBtn.setAttribute('href', link)
    
    var notesBtn = document.getElementById('printNotesLink');
    link='/printWeeklyMonitorNotes?date=' + curWeekDate + '&shop=' + curShopNumber + '&destination=' + destination
    notesBtn.setAttribute('href', link)

    var contactsBtn = document.getElementById('printContactsLink');
    link='/printWeeklyMonitorContacts?date=' + curWeekDate + '&shop=' + curShopNumber + '&destination=' + destination
    contactsBtn.setAttribute('href', link)

    var subsBtn = document.getElementById('printSubsLink');
    link='/printWeeklyMonitorSubs?date='  + curWeekDate + '&shop=' + curShopNumber + '&destination=' + destination
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

function shopClicked() {
    setShopFilter(this.value)
    filterWeeksShown()
}

function setShopFilter(shopLocation) {
    switch(shopLocation){
        case 'RA':
            localStorage.setItem('shopFilter','RA')
            document.getElementById("shopChoice").selectedIndex = 0; //Option Rolling Acres
            shopFilter = 'RA'
            curShopNumber = '1'
            break;
        case 'BW':
            localStorage.setItem('shopFilter','BW')
            document.getElementById("shopChoice").selectedIndex = 1; //Option Brownwood
            shopFilter = 'BW'
            curShopNumber = '2'
            break;
        default:
            localStorage.setItem('shopFilter','RA')
            document.getElementById("shopChoice").selectedIndex = 0; //Option Rolling Acres
            shopFilter = 'RA'
            curShopNumber = '1'
    }   
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
function filterWeeksShown() {
    console.log('@filterWeeksShown the variable curCoordinatorID contains -', curCoordinatorID)
    //alert('shop- ' + curShopNumber + '\n' + 'curCoordinatorID- ' + curCoordinatorID)
    var weeks = document.querySelectorAll('.optWeeks')
    for (i=0; i < weeks.length; i++) {
        thisWeeksCoordID = weeks[i].getAttribute('data-coordID')
        shop = weeks[i].getAttribute('data-shop')
        console.log(i,curShopNumber, curCoordinatorID)
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
    //coordName = 
    //coordEmail =


    // weeks = document.getElementById(weekSelected)
    // curSelectionValue = weeks.value
    // console.log('curSelectionValue = ', curSelectionValue)

    // name1 = this.options[this.selectedIndex].getAttribute("data-coordname").value
    // console.log('name1=', name1)

    // sel = document.getElementById('weekSelected')
    // console.log('value of selected item-',sel.value)
    // Reference to selected option -
    // var opt = sel.options[sel.selectedIndex]
    // console.log(opt.value)

    // Get attribute data-coordname from selected option -
    // console.log(opt.getAttribute('data-coordname').value)
    // document.getElementById('coordinatorsName').innerHTML = 'new name'

    //console.log('@weekChanged variable curWeekDate-',curWeekDate)
    //console.log('@ weekChanged this.value -',this.value)
    // selectedWeek = document.getElementById(this.id)
    // console.log('selectWeek value-', selectedWeek.value)
    // coordNme = selectedWeek.options.getAttribute('data-coordname').value
    // console.log('coordNme-',coordNme)
    // document.getElementById('coordinatorsName').innerHTML = coordNme
    //curWeekDate = document.getElementById(this.id).value;
    
    // x = this.options[this.selectedIndex].getAttribute('data-coordname').value
    // console.log('x=',x)
    //console.log('coordinator - ' + this.getAttribute('data-coordname').value)
    //alert('coordinator - ' + this.getAttribute('data-coordname').value)
    // show coordinator
}

function coordinatorChanged () {
    curCoordinatorID = this.value
    filterWeeksShown()
}

// function coordinatorOnly() {
//     alert('button clicked')
//     console.log('btn clicked')
    // var  formData = "name=ravi&age=31";  //Name value Pair
    // or
    // var formData = {name:"ravi",age:"31"}; //Array 



function coordinatorAndMonitors() {
    alert('button coordinatorOnly clicked')
}

function memberOnly() {
    alert('memberOnly function')
}

// CLICK ON ONE OF THREE SEND TO BUTTONS
// $('.sendToOptions button').click(function(){
//     alert('jquery button clicked -' + this.value)
//     alert('jquery button id - ' + this.id)   
// })

//});