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

    calculateAndDisplayRoute("8430 Fraser St, Vancouver, BC", directionsRenderer1, 'directions1');
    calculateAndDisplayRoute("8888 University Dr W, Burnaby, BC", directionsRenderer2, 'directions2');
}

function calculateAndDisplayRoute(destination, directionsRenderer, directionsElementId) {
    directionsService.route(
        {
            origin: "5411 Rowling Pl. Richmond, BC",
            destination: destination,
            travelMode: google.maps.TravelMode.DRIVING,
            drivingOptions: {
                departureTime: new Date(/* future date */),
                trafficModel: 'pessimistic'
            },
        },
        (response, status) => {
            if (status === "OK") {
                directionsRenderer.setDirections(response);
                // Get duration of the journey
                const duration = response.routes[0].legs[0].duration.text;
                // Get steps of the journey
                const steps = response.routes[0].legs[0].steps.map(step => step.instructions).join('<br>');
                // Display journey details in the directions div
                document.getElementById(directionsElementId).innerHTML = `
                    <h2>Route from 5411 Rowling Pl. Richmond, BC to ${destination}</h2>
                    <p>Estimated journey time: ${duration}</p>
                    <p>Steps:<br>${steps}</p>
                `;
            } else {
                window.alert("Directions request failed due to " + status);
            }
        }
    );
}
