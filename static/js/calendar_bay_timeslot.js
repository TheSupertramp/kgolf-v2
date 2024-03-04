document.addEventListener('DOMContentLoaded', function(){
    /* My test events with testButton at the bottom of calendar_carousel.html */
    // var testbutton = document.getElementById("testbutton");
    // testbutton.addEventListener('htmx:configRequest', (event) => {
    //     var selectedBays = document.querySelectorAll('[id^=listGroupRadioGrid]:checked');        
    //     if(selectedBays.length > 0) {            
    //         var bayNumber = selectedBays[0].value;            
    //         //alert(event.detail.path);
    //         event.detail.path += "/" + bayNumber;
    //         //alert(event.detail.path);
    //     }
    // })

    //check the first bay by default when page load
    // var firstBay = document.getElementById('listGroupRadioGrid1');
    // firstBay.checked = true;

    //////////////
    // Calendar //
    //////////////
    var selectedDateCells = document.querySelectorAll('td[hx-post]');    
    selectedDateCells.forEach(td => td.addEventListener('htmx:configRequest', (event) => {        
        var selectedBays = document.querySelectorAll('[id^=listGroupRadioGrid]:checked');        
        if(selectedBays.length > 0) {            
            var bayNumber = selectedBays[0].value;     
            //alert(event.constructor);
            //alert(event.detail.elt.attributes[1].value);
            event.detail.path += "" + bayNumber;            
        }        
    }))

    /////////
    // Bay //
    /////////
    var selectedBayElements = document.querySelectorAll('input[hx-post]');    
    selectedBayElements.forEach(i => i.addEventListener('htmx:configRequest', (event) => {     
        // Get selected bay number
        var bayNumber = i.value;  //which is itself the caller 
        event.detail.path = event.detail.path.replace("[[bayNumber]]", bayNumber);

        // Get selected date
        var selectedDateCells = document.querySelectorAll('td.selected');
        //selectedDateCells.forEach(d => alert(d.innerHTML));
        if(selectedDateCells.length > 0) {                           
            var selectedDate = selectedDateCells[0].id;
            event.detail.path = event.detail.path.replace("[[date]]", selectedDate);  
        }        
    }))    

    //////////////
    // Timeslot //
    //////////////    
    // let timeslotElements = document.querySelectorAll('div.timeslots div[hx-post][id^=timeslot]');    
    // timeslotElements.forEach(ts => ts.addEventListener('htmx:configRequest', (event) => {        
    //     let hxVals= JSON.parse(ts.getAttribute('hx-vals'))
    //     let timeslotID = hxVals.timeslotID;
    //     alert(timeslotID);
    //     event.detail.path = event.detail.path.replace("[[timeslotID]]", timeslotID);
    // }))
}, false);


function selectNewDate(e) {
    //Remove existing selection info
    var currentSelection = document.querySelector('td.selected');
    if(currentSelection!=null){
        currentSelection.classList.remove('selected');
    }    
        
    //Assign to the new one.
    e.classList.add('selected');


    // htmx.trigger("#d" + month.toString() +o.innerHTML, "once");
    // htmx.process(o);   
}


