import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter } from 'k6/metrics';

// Define custom metrics
const errorRate = new Counter('errors');

// k6 configuration
export const options = {
    thresholds: {
        http_req_duration: ['p(95)<500'],  // 95% of requests must complete within 500ms
        errors: ['count<10'],  // No more than 10 errors allowed
    },
    scenarios: {
        get_plants: {
            executor: 'constant-vus',
            exec: 'getPlants',  // Function for GET requests
            vus: 5,
            duration: '20m',    // Test duration
        },
        create_plant: {
            executor: 'constant-vus',
            exec: 'createPlant',  // Function for POST requests
            vus: 5,
            duration: '20m',
        },
        update_plant: {
            executor: 'constant-vus',
            exec: 'updatePlant',  // Function for PUT requests
            vus: 5,
            duration: '20m',
        },
        delete_plant: {
            executor: 'constant-vus',
            exec: 'deletePlant',  // Function for DELETE requests
            vus: 5,
            duration: '20m',
        },
    },
};

// Base URL of the FastAPI application
const BASE_URL = 'https://fpi-dev.devops.local';

// Shared plant ID variable for create, update, and delete operations
let plantId;

// Scenario 1: GET /plants/ endpoint
export function getPlants() {
    let getResponse = http.get(`${BASE_URL}/plants/`);
    check(getResponse, {
        'GET /plants/ status is 200': (r) => r.status === 200,
        'GET /plants/ is array': (r) => Array.isArray(r.json()),
    });

    if (getResponse.status !== 200) {
        errorRate.add(1);
    }

    sleep(1);  // Simulate user wait time
}

// Scenario 2: POST /plants/ endpoint for creating new plants
export function createPlant() {
    let newPlant = JSON.stringify({
        name: `Plant-${__VU}-${__ITER}`,  // Unique plant name based on VU and iteration
        latin_name: `LatinName-${__VU}-${__ITER}`,
    });

    let postResponse = http.post(`${BASE_URL}/plants/`, newPlant, {
        headers: { 'Content-Type': 'application/json' },
    });

    check(postResponse, {
        'POST /plants/ status is 200': (r) => r.status === 200,
    });

    if (postResponse.status === 200) {
        plantId = postResponse.json().id;  // Store the created plant ID for updating and deleting
    } else {
        errorRate.add(1);
    }

    sleep(1);  // Simulate user wait time
}

// Scenario 3: PUT /plants/{id} endpoint for updating plants
export function updatePlant() {
    if (!plantId) return;  // Skip if no plant was created

    let updateData = JSON.stringify({
        name: `Updated-Plant-${__VU}-${__ITER}`,
        latin_name: `Updated-LatinName-${__VU}-${__ITER}`,
    });

    let putResponse = http.put(`${BASE_URL}/plants/${plantId}`, updateData, {
        headers: { 'Content-Type': 'application/json' },
    });

    check(putResponse, {
        'PUT /plants/ status is 200': (r) => r.status === 200,
        'PUT /plants/ returns updated name': (r) => r.json().name.includes('Updated-Plant'),
    });

    if (putResponse.status !== 200) {
        errorRate.add(1);
    }

    sleep(1);  // Simulate user wait time
}

// Scenario 4: DELETE /plants/{id} endpoint for deleting plants
export function deletePlant() {
    if (!plantId) return;  // Skip if no plant was created

    let deleteResponse = http.del(`${BASE_URL}/plants/${plantId}`);

    check(deleteResponse, {
        'DELETE /plants/ status is 200': (r) => r.status === 200,
    });

    if (deleteResponse.status !== 200) {
        errorRate.add(1);
    }

    sleep(1);  // Simulate user wait time
}
