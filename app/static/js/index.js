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
    
    document.getElementById('getMemberContactInfoID').removeAttribute('disabled')
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

function ContactInfo() {
    villageID = currentMemberID
    var dataToSend = {
        villageID: villageID
    };
    fetch(`${window.origin}/getMemberContactInfo`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dataToSend),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(function (response) {
        if (response.status != 200) {
            console.log(`Response status was not 200: ${response.status}`);
            return ;
        }
        response.json().then(function (data) {
            // Was the member found in the lightspeed database?
            if (data.hasOwnProperty('msg')){
                modalAlert('ERROR',data.msg)
                return
            }
           
            
            msg = `
                <ul class="list-group mb=3">
                    <li class="list-group-item"style=text-align:left>Village ID - ${data.memberID}</li>
                    <li class="list-group-item"style=text-align:left>Lightspeed ID - ${data.lightspeedID}</li>
                    <li class="list-group-item"style=text-align:left>Home phone - ${data.homePhone}</li>
                    <li class="list-group-item"style=text-align:left>Mobile phone - ${data.cellPhone}</li>
                    <li class="list-group-item"style=text-align:left>Email - ${data.eMail}</li>
                </ul>   
            `   
            modalAlert(data.memberName,msg)
            
        })
    })
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

$('#beginDateID').change(function(){
	document.getElementById('endDateID').value = document.getElementById('beginDateID').value
})



$('#printTrainingClassID').click(function(){
	beginDate = document.getElementById('beginDateID').value
	endDate = document.getElementById('endDateID').value
	if (beginDate == ''){
		alert("Please enter a beginning date.")
	return 
	}
	if (endDate == ''){
		alert("Please enter an ending date.")
	return 
	}
    shopChoice = document.getElementById('shopChoice').value 
    switch (shopChoice) {
        case 'RA':
            shopNumber = '1'
            break
        case 'BW':
            shopNumber = '2'
    }
	link = '/printTrainingClass?beginDate=' + beginDate + '&endDate=' + endDate + '&shop=' + shopNumber 
	window.location.href = link
})


function modalAlert(title,msg) {
	document.getElementById("modalTitle").innerHTML = title
	document.getElementById("modalBody").innerHTML= msg
	$('#myModalMsg').modal('show')
}


function closeModal() {
	$('#myModalMsg').modal('hide')
}

// END OF FUNCTIONS
