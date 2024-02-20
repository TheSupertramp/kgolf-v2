// Select all the timeslots
let timeslots = document.querySelectorAll('.bay li');

// Loop through the timeslots and add an event listener to each of them
for (let timeslot of timeslots) {
    timeslot.addEventListener('click', function() {
        // Get the time, booked status, and button of the clicked timeslot
        let time = timeslot.dataset.time;
        let booked = timeslot.dataset.booked;
        let button = timeslot.querySelector('button');

        // If the timeslot is not booked, check the previous and next timeslots
        if (booked === 'false') {
            // Get the index of the clicked timeslot
            let index = Array.from(timeslots).indexOf(timeslot);

            // Get the previous and next timeslots if they exist
            let prev = timeslots[index - 1];
            let next = timeslots[index + 1];

            // If the previous timeslot is booked, unbook it and change its button text and color
            if (prev && prev.dataset.booked === 'true') {
                prev.dataset.booked = 'false';
                prev.querySelector('button').textContent = 'Book Now';
                prev.querySelector('button').style.backgroundColor = 'green';
            }

            // If the next timeslot is booked, unbook it and change its button text and color
            if (next && next.dataset.booked === 'true') {
                next.dataset.booked = 'false';
                next.querySelector('button').textContent = 'Book Now';
                next.querySelector('button').style.backgroundColor = 'green';
            }

            // Book the clicked timeslot and change its button text and color
            timeslot.dataset.booked = 'true';
            button.textContent = 'Booked';
            button.style.backgroundColor = 'gray';
        }

        // If the timeslot is booked, unbook it and change its button text and color
        else {
            timeslot.dataset.booked = 'false';
            button.textContent = 'Book Now';
            button.style.backgroundColor = 'green';
        }
    });
}
