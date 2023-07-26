let directionsService;
let directionsRenderer1;
let directionsRenderer2;

function initMap() {
    directionsService = new google.maps.DirectionsService();
    directionsRenderer1 = new google.maps.DirectionsRenderer();
    directionsRenderer2 = new google.maps.DirectionsRenderer();

    const map1 = new google.maps.Map(document.getElementById("map1"), {
        zoom: 7,
        center: { lat: 49.2827, lng: -123.1207 },
    });
    directionsRenderer1.setMap(map1);

    const map2 = new google.maps.Map(document.getElementById("map2"), {
        zoom: 7,
        center: { lat: 49.2827, lng: -123.1207 },
    });
    directionsRenderer2.setMap(map2);

    // Trigger a resize event on the map when the window size changes
    google.maps.event.addDomListener(window, "resize", function() {
        const center1 = map1.getCenter();
        google.maps.event.trigger(map1, "resize");
        map1.setCenter(center1);

        const center2 = map2.getCenter();
        google.maps.event.trigger(map2, "resize");
        map2.setCenter(center2);
    });

    calculateAndDisplayRoute("8430 Fraser St, Vancouver, BC", directionsRenderer1, 'directions1');
    calculateAndDisplayRoute("8888 University Dr W, Burnaby, BC", directionsRenderer2, 'directions2');
}

function calculateAndDisplayRoute(end, renderer, elementId) {
    const start = "5411 Rowling Pl. Richmond, BC";
    directionsService.route({
        origin: start,
        destination: end,
        travelMode: 'DRIVING'
    }, function(response, status) {
        if (status === 'OK') {
            renderer.setDirections(response);
            const directionsData = response.routes[0].legs[0];
            if (!directionsData) {
                window.alert('Directions request failed');
                return;
            }
            const { duration, steps } = directionsData;
            document.getElementById(elementId).innerHTML = `
                <strong>From:</strong> ${start} 
                <br>
                <strong>To:</strong> ${end} 
                <br>
                <strong>Duration:</strong> ${duration.text}
                <br>
                <strong>Steps:</strong> 
                <ul>
                    ${steps.map(step => `<li>${step.instructions}</li>`).join("")}
                </ul>
            `;
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}

