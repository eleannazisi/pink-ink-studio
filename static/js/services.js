let buttons = document.querySelectorAll(".servmenu");

console.log(buttons);

buttons.forEach(button=>{
    button.addEventListener("click",event=>{
        event.target.style.backgroundColor = "pink"
    })
})
 

function nailmenu(){

document.getElementById("tattoo_info").style.display = "none";    
document.getElementById("nail_info").style.display = "flex";
document.getElementById("lash_info").style.display = "none";

}

function lashmenu(){

document.getElementById("tattoo_info").style.display = "none";    
document.getElementById("nail_info").style.display = "none";
document.getElementById("lash_info").style.display = "flex";

} 

function tatmenu(){

document.getElementById("tattoo_info").style.display = "flex";
document.getElementById("nail_info").style.display = "none";
document.getElementById("lash_info").style.display = "none";

}

let servitem = document.querySelectorAll(".apointment");
 
console.log(servitem);

function showbookingstep1(){

document.getElementById("bookingstep1").style.display = "flex";
document.getElementById("bookingstep2").style.display = "none";
document.getElementById("bookingstep3").style.display ="none";
}

function showbookingstep2(){

document.getElementById("bookingstep1").style.display = "none";
document.getElementById("bookingstep2").style.display = "flex";
document.getElementById("bookingstep3").style.display ="none";

}

function showbookingstep3(){

document.getElementById("bookingstep1").style.display = "none";
document.getElementById("bookingstep2").style.display = "none";
document.getElementById("bookingstep3").style.display ="flex";

}

function successpopup(){
    document.getElementById("successpopup").style.display = "flex";
}

function closecancellationpopup(){
    document.getElementById("cancellationpopup").style.display = "none";
}

function cancelbooking(){
    const bookingid = document.getElementById("cancelbutton").dataset.bookingid;
    console.log("Booking Id:", bookingid);
    alert("Are you sure you want to cancel your apointment?");
}

function closepopup(){
    document.getElementById("successpopup").style.display = "none";
}

function closebooking(){
    document.getElementById("bookingstep2").style.display = "none";
    document.getElementById("bookingstep1").style.display ="none";
    document.getElementById("bookingstep3").style.display ="none";
}

let currentDate = new Date();

const monthYear = document.getElementById("monthyear");

monthYear.textContent = currentDate.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric"
});


function renderCalendar() {

    const daysContainer = document.getElementById("days");

    daysContainer.innerHTML = "";

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    monthYear.textContent = currentDate.toLocaleDateString("en-US", {
        month: "long",
        year: "numeric"
    });

    const lastDay = new Date(year, month + 1,0);
    const firstDay = new Date(year, month, 1);
    const startDay = firstDay.getDay();
    const emptyDays = (startDay + 6)% 7;


    for (let i = 0; i < emptyDays; i++) {
        const emptyDay = document.createElement("div");
        daysContainer.appendChild(emptyDay);
    }

    for (let day = 1; day <= lastDay.getDate(); day++) {

        const dayButton = document.createElement("button");

        console.log("DAY CLICKED");

        dayButton.type = "button";
        dayButton.textContent = day;

        dayButton.classList.add("buttonday");

        dayButton.addEventListener('click', function() {

            const selectedDay = document.querySelector(".buttonday.selected");

            if (selectedDay) {
                selectedDay.classList.remove("selected");
            }

            dayButton.classList.add("selected");

            const dateValue = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

            document.getElementById("selectedDate").value = dateValue;

            console.log("DATE: ", dateValue);


            selectedDay = `${day}/${month + 1}/${year}`;

            document.getElementById("selectedDate").value = dateValue;

            console.log("SelectedDate: ", selectedDate);
        });

        daysContainer.appendChild(dayButton);
    }
    console.log("Calendar rendered");
}

renderCalendar();

const nextButton = document.getElementById("next");
nextButton.addEventListener("click", function(){
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
});

const prevButton = document.getElementById("prev");
prevButton.addEventListener("click", function(){
    currentDate.setMonth(currentDate.getMonth() - 1)
    renderCalendar();
});

const timeButtons = document.querySelectorAll('input[name="time"]');

timeButtons.forEach(function(timeButton){
    timeButton.addEventListener("change",function(){
        timeButtons.forEach(function(otherTime){
            otherTime.checked = false;
        });
        timeButton.checked = true;
    });
});