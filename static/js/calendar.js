document.addEventListener('DOMContentLoaded', function(){
    var today = new Date(),
        year = today.getFullYear(),
        month = today.getMonth(),
        monthTag =["January","February","March","April","May","June","July","August","September","October","November","December"],
        day = today.getDate(),
        days = document.getElementsByTagName('td'),
        selectedDay,
        setDate,
        daysLen = days.length;
// options should like '2014-01-01'
    function Calendar(selector, options) {
        this.options = options;
        this.draw();
    }
    
    Calendar.prototype.draw  = function() {
        this.getCookie('selected_day');
        this.getOptions();
        this.drawDays();
        var that = this,
            reset = document.getElementById('reset'),
            pre = document.getElementsByClassName('pre-button'),
            next = document.getElementsByClassName('next-button');
            
            pre[0].addEventListener('click', function(){that.preMonth(); });
            next[0].addEventListener('click', function(){that.nextMonth(); });
            reset.addEventListener('click', function(){that.reset(); });
        while(daysLen--) {
            days[daysLen].addEventListener('click', function(){that.clickDay(this); });
        }
    };
    
    Calendar.prototype.drawHeader = function(e) {
        var headDay = document.getElementsByClassName('head-day'),
            headMonth = document.getElementsByClassName('head-month');

            e?headDay[0].innerHTML = e : headDay[0].innerHTML = day;
            headMonth[0].innerHTML = monthTag[month] +" - " + year;        
     };
    
    Calendar.prototype.drawDays = function() {
        var startDay = new Date(year, month, 1).getDay(),
            nDays = new Date(year, month + 1, 0).getDate(),    
            n = startDay;        

        for(var k = 0; k <42; k++) {
            days[k].innerHTML = '';
            days[k].id = '';
            days[k].className = ''; 
            days[k].outerHTML = '<td id="" class=""></td>';
        }
        
        for(var i  = 1; i <= nDays ; i++) {
            days[n].innerHTML = i;
            
            var iDrawingDate = new Date(year, month, i);
            var todayDate = new Date(today.toDateString());
            
            if(iDrawingDate >= todayDate) {
                //lets add HTMX stuff                
                var fullDateStr = year + "-" + (month+1).toString().padStart(2, '0') + "-" + i.toString().padStart(2, '0');            
                days[n].outerHTML = days[n].outerHTML.replace('class=""', 'class="" hx-get="/timesheet/' + fullDateStr + '/1" hx-target="#timesheet" hx-indicator=".htmx-indicator"');
                days[n].setAttribute("id", "d" + (month+1).toString() + i.toString());
                htmx.process(days[n]);       
            }
            n++;
        }
        
        for(var j = 0; j < 42; j++) {
            var drawingDate = new Date(year, month, (j-startDay+1));
            
            // const attr = document.createAttribute("hx-get");
            // attr.value = "/timesheet/" + drawingDate.toISOString().split('T')[0] + "/1";
            // days[j].setAttributeNode(attr)

            if(days[j].innerHTML === ""){
                
                days[j].id = "disabled";
                
            }else if(month === today.getMonth() && j === day + startDay - 1){
                if((this.options && (month === setDate.getMonth()) && (year === setDate.getFullYear())) || (!this.options && (month === today.getMonth())&&(year===today.getFullYear()))){
                    this.drawHeader(day);
                    days[j].id = "today";
                }
            }else{
                var jDrawingDate = new Date(year, month, i);
                var jtodayDate = new Date(today.toDateString());
                //alert(drawingDate);
                if(drawingDate.getTime() < today.getTime()){
                    days[j].id = "disabled";
                    //days[j].innerHTML = ''; //i am not deleting this to keep past date
                    days[j].className = 'past-date';
                }

            }
            if(selectedDay){
                if((j === selectedDay.getDate() + startDay - 1)&&(month === selectedDay.getMonth())&&(year === selectedDay.getFullYear())){
                days[j].className = "selected";
                this.drawHeader(selectedDay.getDate());
                }
            }
        }
    };
    
    Calendar.prototype.clickDay = function(o) {                
        selectedDay = new Date(year, month, o.innerHTML);                
        var todayDateOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        //alert(selectedDay + "/" + todayDateOnly);
        if(selectedDay >= todayDateOnly) {
            var selected = document.getElementsByClassName("selected"),
            len = selected.length;
            if(len !== 0){
                selected[0].className = "";
            }
            o.className = "selected";            
            this.drawHeader(o.innerHTML);
            this.setCookie('selected_day', 1);                            

            //document.getElementById("timesheet").style="display:none;";
            //document.getElementById("timesheet").className = "visually-hidden";
            document.getElementById("timesheet").innerHTML=""; //clear the currently visible timesheet contents
            //htmx.addClass(htmx.find("#timesheet"), "visually-hidden");
            //htmx.remove(htmx.find)
            //document.getElementById("timesheet").style="opacity:0";

            //let's trigger HTMX event
            var originalID = o.id;
            o.setAttribute("id", "d" + month.toString() + o.innerHTML);
            htmx.trigger("#d" + month.toString() +o.innerHTML, "once");
            htmx.process(o);   
            o.setAttribute("id", originalID);         
            
            
            //htmx.removeClass(htmx.find("#timesheet"), "visually-hidden", 1000);
        }


        
    };
    
    Calendar.prototype.preMonth = function() {        
        var currentPageFOM = new Date(year, month, 1);
        var thisMonthFOM = new Date(today.getFullYear(), today.getMonth(), 1);
        if(currentPageFOM > thisMonthFOM) {
            if(month < 1){ 
                month = 11;
                year = year - 1; 
            }else{
                month = month - 1;
            }
            this.drawHeader(1);
            this.drawDays();
        }
    };
    
    Calendar.prototype.nextMonth = function() {
        if(month >= 11){
            month = 0;
            year =  year + 1; 
        }else{
            month = month + 1;
        }
        this.drawHeader(1);
        this.drawDays();
    };
    
    Calendar.prototype.getOptions = function() {
        if(this.options){
            var sets = this.options.split('-');
                setDate = new Date(sets[0], sets[1]-1, sets[2]);
                day = setDate.getDate();
                year = setDate.getFullYear();
                month = setDate.getMonth();
        }
    };
    
     Calendar.prototype.reset = function() {
         month = today.getMonth();
         year = today.getFullYear();
         day = today.getDate();
         selectedDay = today;        
         this.options = undefined;
         this.drawDays();
     };
    
    Calendar.prototype.setCookie = function(name, expiredays){
        if(expiredays) {
            var date = new Date();
            date.setTime(date.getTime() + (expiredays*24*60*60*1000));
            var expires = "; expires=" +date.toGMTString();
        }else{
            var expires = "";
        }
        document.cookie = name + "=" + selectedDay + expires + "; path=/";
    };
    
    Calendar.prototype.getCookie = function(name) {
        if(document.cookie.length){
            var arrCookie  = document.cookie.split(';'),
                nameEQ = name + "=";
            for(var i = 0, cLen = arrCookie.length; i < cLen; i++) {
                var c = arrCookie[i];
                while (c.charAt(0)==' ') {
                    c = c.substring(1,c.length);
                    
                }
                if (c.indexOf(nameEQ) === 0) {
                    selectedDay =  new Date(c.substring(nameEQ.length, c.length));
                }
            }
        }
    };
    var calendar = new Calendar();
    
        
}, false);