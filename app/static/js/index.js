// index.js
//  PAGE LOAD ROUTINES
// Declare global variables)

var todaysDate = new Date();
var shopNames = ['Rolling Acres', 'Brownwood']


// UPDATED ON LOAD AND SHOP CHANGE
var curShopNumber = ''
var curShopName = ''

// LISTENERS
//document.getElementById('offeringsDetail').addEventListener('click',offeringClickRtn)
// SET INITIAL PAGE VALUES

// GET STAFFID THAT WAS STORED BY THE LOGIN ROUTINE
if (!localStorage.getItem('staffID')) {
    staffID = prompt("Staff ID - ")
    localStorage.setItem('staffID',staffID)
}
else {
    staffID = localStorage.getItem('staffID')
}

// PRINT THE REPORTS
//$('#prtPresidentsReportID').click(function(){
    
//})

document.getElementById("selectpicker").addEventListener("change",memberSelectedRtn)

function memberSelectedRtn() {
    selectedMember = this.value
	lastEight = selectedMember.slice(-8)
	currentMemberID= lastEight.slice(1,7)
	//document.getElementById('selectpicker').value=''
    document.getElementById('prtMonitorTransactionsID').removeAttribute('disabled')
}
function PresidentsReport() {
    window.location.href = '/prtPresidentsReport?destination=PRINT' 
}

function Mentors() {
    window.location.href = '/prtMentors?destination=PRINT'
}

function Contacts() {
    window.location.href = '/prtContacts?destination=PRINT'
}

function Transactions() {
    d = new Date();
    curYear = d.getFullYear();
    yr = prompt('Monitor schedule year?',curYear)
    link = '/prtMonitorTransactions?destination=PRINT&memberID=' + currentMemberID + '&year=' + curYear
    window.location.href = link
}

function OpenClasses() {
    window.location.href = '/prtOpenClasses?destination=PRINT' 
}

function AllClasses() {
    window.location.href = '/prtAllClasses?destination=PRINT' 
}

function ClassList() {
    window.location.href = '/ClassLists?destination=PRINT'
}

function offeringClickRtn(e) {
    alert('e.target - '+e.target)
    if (e.target.className.includes('offeringSectionName')) {
        sectionNumber = e.target.innerHTML
        courseNumber = sectionNumber.slice(0,4)
        courseTitle = e.target.nextElementSibling.innerHTML
        document.getElementById('modalCourseDescriptionTitle').innerHTML = courseNumber + ' - ' + courseTitle
    }
}

// $("#offeringsDetail").on("change", function() {
//     alert('something changed')
// })

// $(".sectionBtn").click(function() {
//     alert('sectionBtn clicked')
//     sectionNumber = this.id
//     alert('this.value - ',this.value)
//     courseData = this.value
//     selectedCourse = courseData.slice(0,4)
//     $("#courseOfferingsTable tr").filter(function() {
//         $(this).toggle($(this).text().indexOf(selectedCourse) > -1)
//     })
//  });

//  function offeringBtn() {
//      alert('offeringBtn clicked, this.id - '+this.id)
//  }
// END OF FUNCTIONS
