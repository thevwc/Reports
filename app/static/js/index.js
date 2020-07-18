//$(document).ready (function() {

// DEFINE VARIABLES
// Color constants
const colors = {
    bg_NeedSM:  "#0000FF",  // Blue
    fg_NeedSM:  "#FFFFFF",  // White 
    bg_NeedTC:  "#00FF00",  // Green
    fg_NeedTC:  "#000000",  // Black (#000000)
    bg_NeedBoth:"#FF0000",  // Red (#FF0000)
    fg_NeedBoth:"#FFFFFF",  // White (#FFFFFF)
    bg_Filled:  "#FFFFFF",  // White (#FFFFFF)
    fg_Filled:  "#000000",  // Black (#000000)
    bg_Sunday:  "#cccccc",  // Light grey
    fg_Sunday:  "#FFFFFF",  // White (#FFFFFF)
    bg_Closed:  "#2E86C1",  // Aqua
    fg_Closed:  "#FFFFFF",  // White (#FFFFFF)
    bg_ToManySM:"#FAFE02",  // Yellow
    fg_ToManySM:"#000000",  // Black
    bg_ToManyTC:"#FE4E02",  // Orange
    fg_ToManyTC:"#000000",  // Black
    bg_PastDate:"#cccccc",  // Light grey
    fg_PastDate:"#FFFFFF"   // White (#FFFFFF)
};

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
document.getElementById("shopChoice").addEventListener("change", shopChanged);
document.getElementById("coordChoice").addEventListener("change", coordinatorChanged);
document.getElementById("printReportBtn").addEventListener("click",printReports);

// prt = document.getElementById("printByPost")
// address = "/printWeeklyMonitorSchedulePOST?dateScheduled="+ curWeekDate + "&shopNumber=" + curShopNumber 
// lnk = "window.location.href='" + address +"'"
// prt.setAttribute("onclick",lnk)


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
filterWeeksShown()

// ------------------------------------------------------------------------------------------------------
// FUNCTIONS    
// ------------------------------------------------------------------------------------------------------
function printReports() {
    reportSelected = false
    if (curWeekDate == null  || curWeekDate == '') {
        alert('You must select a date.')
        return 
    }
    
    if (document.getElementById('scheduleID').checked) {
        reportSelected = true
        printWeeklyMonitorSchedule(curWeekDate,curShopNumber)
    }
    if (document.getElementById('notesID').checked) {
        reportSelected = true
        printWeeklyMonitorNotes(curWeekDate,curShopNumber)
    }
    if (document.getElementById('contactsID').checked) {
        reportSelected = true
        printWeeklyMonitorContacts(curWeekDate,curShopNumber)
    }
    if (document.getElementById('subsID').checked) {
        reportSelected = true
        printWeeklyMonitorSubs(curWeekDate,curShopNumber)
    }

    if (reportSelected == false) {
        alert('You must select at least one report.')
        return
    }

}

function shopChanged() {
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
  

function printWeeklyMonitorSchedule(beginDate,shopNumber) {
    // SEND DATE AND SHOPNUMBER TO SERVER
    var xhttp = new XMLHttpRequest();    
    xhttp.open("GET", "/printWeeklyMonitorSchedule?dateScheduled=" + beginDate + "&shopNumber=" + shopNumber , true);
    xhttp.send();
}

function weekChanged () {
    curWeekDate = document.getElementById(this.id).value
}

function coordinatorChanged () {
    curCoordinatorID = this.value
    filterWeeksShown()
}

function printWeeklyMonitorNotes() {
    alert('Routine has not been implemented.')
    return
}
function printWeeklyMonitorContacts(beginDate,shopNumber) {
    // SEND DATE AND SHOPNUMBER TO SERVER
    var xhttp = new XMLHttpRequest();  
    xhttp.open("GET", "/printWeeklyMonitorContacts?dateScheduled=" + beginDate + "&shopNumber=" + shopNumber , true);
    xhttp.send();
    return
}
function printWeeklyMonitorSubs() {
    alert('Routine has not been implemented.')
    return
}