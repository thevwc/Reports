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
document.getElementById("weekSelected").addEventListener("click", weekChanged);

document.getElementById("shopChoice").addEventListener("click", shopClicked);
document.getElementById("coordChoice").addEventListener("change", coordinatorChanged);
document.getElementById("printReportBtn").addEventListener("click",printReports);
// document.getElementById("printWeeklyMonitorNotes").addEventListener("click",printWeeklyMonitorNotes);

// var btn = document.getElementById('prtScheduleBtn');
// btn.onclick = function() {
// location.assign('https://localhost:5000/printWeeklyMonitorSchedule?date=2020-08-10&shop=1');
// }



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
    
    if (curShopNumber == null || curShopNumber == '') {
        shop=document.getElementById('shopChoice').value
        alert('A locationmust be selected')
        return 
    }
    
    var scheduleBtn = document.getElementById('printScheduleLink');
    link='/printWeeklyMonitorSchedule?date=2020-08-09&shop=1'
    link='/printWeeklyMonitorSchedule?date=' + curWeekDate + '&shop=' + curShopNumber
    scheduleBtn.setAttribute('href', link)
    
    var notesBtn = document.getElementById('printNotesLink');
    link='/printWeeklyMonitorNotes?date=' + curWeekDate + '&shop=' + curShopNumber
    notesBtn.setAttribute('href', link)
    
    var contactsBtn = document.getElementById('printContactsLink');
    link='/printWeeklyMonitorContacts?date=' + curWeekDate + '&shop=' + curShopNumber
    contactsBtn.setAttribute('href', link)

    var subsBtn = document.getElementById('printSubsLink');
    link='/printWeeklyMonitorSubs?date='  + curWeekDate + '&shop=' + curShopNumber
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
        reportSelected = true
        subsBtn.click()

        // printWeeklyMonitorSubs(curWeekDate,curShopNumber)
    }

    if (reportSelected != True) {
        alert('No reports have been selected.')
        return
    }
}

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
  

// function printWeeklyMonitorSchedule(beginDate,shopNumber) {
//     // SEND DATE AND SHOPNUMBER TO SERVER
//     var httpRequest = new XMLHttpRequest(); 
//     httpRequest.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//             document.write(httpRequest.responseText)
//             document.close()
//             //print(httpRequest.responseText)
//         }
//     };
//     httpRequest.open("GET", "/printWeeklyMonitorSchedule?date=" + beginDate + "&shop=" + shopNumber , true);
//     httpRequest.send();
// }

function weekChanged () {
    curWeekDate = document.getElementById(this.id).value
    // show coordinator
}

function coordinatorChanged () {
    curCoordinatorID = this.value
    filterWeeksShown()
}


// FOLLOWING DID NOT WORK; FETCH MAY NOT BE THE RIGHT APPROACH FOR LAUNCHING REPORT FROM JAVASCRIPT
// function printWeeklyMonitorNotes(beginDate,shopNumber) {
//     let data = new FormData();
//     data.date=beginDate
//     data.shop=shopNumber
//     //data = {'date':'20200810','shop:1'}

//     var baseurl = window.location.origin;
//     fetch(`${baseurl}/printWeeklyMonitorNotes`,
//     {
//         method: "POST",
//         headers: new Headers({
//             //'Content-Type': 'application/x-www-form-urlencoded'
//             'Content-Type': 'application/json'
//         }),
//         body:JSON.stringify(data)
//     })
//     .then(function(res){ return res.json(); })
//     .then(function(data){ alert( JSON.stringify( data ))})
//     .catch(function (error) {
//         console.log('Request failure: ', error);
//     });


//     // let url = new URL('http://localhost:5000/printWeeklyMonitorNotes')
    // url.search = new URLSearchParams({
    //     date:{beginDate},
    //     shop:{shopNumber}
    // })
    // alert('url- '+ url)
    // fetch(url)
//}

// function printWeeklyMonitorNotes(beginDate,shopNumber) {
//     // SEND DATE AND SHOPNUMBER TO SERVER
//     var httpRequest = new XMLHttpRequest(); 
//     httpRequest.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//             document.write(httpRequest.responseText)
//         }
//     };
//     httpRequest.open('GET', '/printWeeklyMonitorNotes?date=' + beginDate + '&shop=' + shopNumber, true);
//     httpRequest.send();
//     // END httpRequest FUNCTION    
// }


// function alertContents() {
//     if (httpRequest.readyStte === XMLHttpRequest.DONE) {
//         if (httpRequest.status === 200) {
//             alert(httpRequest.responseText);
//         } else {
//             alert('There was a problem with the request.');
//         }
//     }
// }


// function printWeeklyMonitorContacts(beginDate,shopNumber) {
//     // SEND DATE AND SHOPNUMBER TO SERVER
//     var httpRequest = new XMLHttpRequest(); 
//     httpRequest.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//             document.write(httpRequest.responseText)
//         }
//     }; 
//     httpRequest.open("GET", "/printWeeklyMonitorContacts?date=" + beginDate + "&shop=" + shopNumber , true);
//     httpRequest.send();
//     return
// }
// function printWeeklyMonitorSubs() {
//     alert('Routine has not been implemented.')
//     return
// }