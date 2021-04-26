// index.js
//  PAGE LOAD ROUTINES
// Declare global variables)

var todaysDate = new Date();
var shopNames = ['Rolling Acres', 'Brownwood']


// UPDATED ON LOAD AND SHOP CHANGE
var curShopNumber = ''
var curShopName = ''

shopChoice = document.getElementById('loginShopID').value
$("#shopChoice").val(shopChoice)
console.log('shopChoice - '+shopChoice)
switch(shopChoice){
    case 'RA':
        document.getElementById("shopChoice").selectedIndex = 0; //Option Rolling Acres
        break;
    case 'BW':
        document.getElementById("shopChoice").selectedIndex = 1; //Option Brownwood
        break;
    default:
    document.getElementById("shopChoice").selectedIndex = 0; //Option Both
    } 
    
    
document.getElementById("selectpicker").addEventListener("change",memberSelectedRtn)

function memberSelectedRtn() {
    selectedMember = this.value
	lastEight = selectedMember.slice(-8)
	currentMemberID= lastEight.slice(1,7)
	//document.getElementById('selectpicker').value=''
    document.getElementById('prtMonitorTransactionsID').removeAttribute('disabled')
    document.getElementById('prtMemberScheduleID').removeAttribute('disabled')

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
    link = '/prtMonitorTransactions?destination=PRINT&memberID=' + currentMemberID + '&year=' + yr
    window.location.href = link
}


function MemberSchedule() {
    link = '/prtMemberSchedule?destination=PRINT&memberID=' + currentMemberID 
    window.location.href = link
}

function OpenClasses() {
    window.location.href = '/prtOpenClasses?destination=PRINT' 
}

function AllClasses() {
    window.location.href = '/prtAllClasses?destination=PRINT' 
}
// function printTrainingClassList() {
//     window.location.href = '/prtTrainingClassList?destination=PRINT'
// }
$('#printTrainingClassID').click(function(){
    classDate = document.getElementById('trainingDateSelected').value
    if (classDate == ''){
        alert("Please select a date.")
        return 
    }
    link = '/printTrainingClass?classDate=' + classDate + '&destination=PRINT' 
    window.location.href = link
})
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

// END OF FUNCTIONS
