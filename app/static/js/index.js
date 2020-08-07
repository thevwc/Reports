$( document ).ready (function() {
//    $( "p" ).text( "The DOM is now loaded and can be manipulated." );
    // Declare global variables)

    // clientLocation, staffID will be set in localStorage within login routine
    var clientLocation = ''
    var todaysDate = new Date();
    var shopNames = ['Rolling Acres', 'Brownwood']

    var curShopNumber = ''
    var curWeekDate = ''  //UPDATED FROM WEEK DROPDOWN 
    var curCoordinatorID = 'All' //UPDATED FROM COORDINATOR SELECTION
    var curCoordinatorName = '' //UPDATED FROM COORDINATOR SELECTION

    // DEFINE EVENT LISTENERS
    document.getElementById("weekSelected").addEventListener("change", weekChanged);
    document.getElementById("weekSelected").addEventListener("click", weekChanged);

    document.getElementById("shopChoice").addEventListener("click", shopClicked);
    document.getElementById("coordChoice").addEventListener("change", coordinatorChanged);

    // Note - both of these buttons link to the 'printReports' function
    document.getElementById("printReportBtn").addEventListener("click",function(){printReports('PRINT');},false);
    document.getElementById("eMailReportBtn").addEventListener("click",function(){printReports('PDF');},false);

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
    
    setShopFilter(clientLocation)
    filterWeeksShown(curShopNumber,curCoordinatorID)

    // SET EMAILSECTION TO OPAQUE
    document.getElementById('emailSection').style.opacity=.2;
    alert('opacity set to .2')
    document.getElementById("emailSection").style.display=None
});
 
// ------------------------------------------------------------------------------------------------------
// FUNCTIONS    
// ------------------------------------------------------------------------------------------------------
function printReports(destination) {
    //alert('printReports') 
    if (destination == 'PDF'){
        document.getElementById('emailSection').opacity=1
    }

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
    //alert('shop- ' + curShopNumber + '\n' + 'curCoordinatorID- ' + curCoordinatorID)
    var weeks = document.querySelectorAll('.optWeeks')
    for (i=0; i < weeks.length; i++) {
        thisWeeksCoordID = weeks[i].getAttribute('data-coordID')
        shop = weeks[i].getAttribute('data-shop')
        console.log(i,curShopNumber,curCoordinatorID)
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
    curWeekDate = document.getElementById(this.id).value
    // show coordinator
}

function coordinatorChanged () {
    curCoordinatorID = this.value
    filterWeeksShown()
}
