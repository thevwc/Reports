// classLists.js
// $("#offeringsDetail").on("change", function() {
//     alert('something changed')
// })

// EVENT LISTENTERS
document.getElementById('prtClassListBtn').addEventListener('click',prtClassList)
document.getElementById('eMailClassListBtn').addEventListener('click',eMailClassList)
//document.getElementById('closeClassListBtn').addEventListener('click',closeClassList)

$(".sectionBtn").click(function(e) {
    sectionNumber = e.target.id
    document.getElementById('selectedSectionNumber').value = sectionNumber
    //parentTD = e.target.parentElement
    //titleTD = parentTD.nextElementSibling
    
    // AJAX
    // BUILD TABLE OF ENROLLEES

    $.ajax({
        url : "/getCourseMembers",
        type: "GET",
        data : {
            sectionNumber:sectionNumber,
            },

        success: function(data, textStatus, jqXHR)
        {
            // CLEAR TABLE
            // DEFINE PARENT AS 'TABLE'
            detailParent = document.getElementById('enrolleesDetail')
            while (detailParent.firstChild) {
                detailParent.removeChild(detailParent.lastChild);
            }

            classList = data.classListDict
            for (i=0; i<classList.length; i++) {
               
                var tableRow = document.createElement('div')
                tableRow.classList.add('row')
                detailParent.appendChild(tableRow)

                var col0 = document.createElement('div')
                col0.classList.add('col-1')
                tableRow.appendChild(col0)

                var col1 = document.createElement('div')
                col1.classList.add('col-3')
                col1.innerHTML = classList[i]['memberName']
                tableRow.appendChild(col1)

                var col2 = document.createElement('div')
                col2.classList.add('col-1')
                col2.innerHTML = classList[i]['dateEnrolled']
                tableRow.appendChild(col2)

                var col3 = document.createElement('div')
                col3.classList.add('col-3')
                col3.innerHTML = classList[i]['eMail']
                tableRow.appendChild(col3)

                var col4 = document.createElement('div')
                col4.classList.add('col-2')
                col4.innerHTML = classList[i]['homePhone']
                tableRow.appendChild(col4)

                var col5 = document.createElement('div')
                col5.classList.add('col-2')
                col5.innerHTML = classList[i]['cellPhone']
                tableRow.appendChild(col5)
               
            }

                
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert("Error getting course members.\n"+errorThrown + '\n'+textStatus)
        }
    })     
   
});

function prtClassList() {
    sectionNumber= document.getElementById('selectedSectionNumber').value
    window.location.href = '/prtClassList/' + sectionNumber
}
function eMailClassList() {
    alert('Routine not implemented.')
}
function closeClassList() {
    window.history.back()
}
// END OF FUNCTIONS
