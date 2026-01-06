import pytest
from app import app # import app.py file
from flask import url_for

# Define a fixture to set up the test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Simulate user authentication before each test
@pytest.fixture
def authenticated_client(client):
    # Replace these with valid login credentials in your database
    email = 'testingaccount@mail.com'
    password = 'Test1234'

    # Make a POST request to the login route with the credentials
    client.post('/login', data={'email': email, 'password': password})

    # Return the authenticated client
    return client

# Test the protected /home route when the user is authenticated
def test_bookings_route(authenticated_client):
    response = authenticated_client.get('/bookings')
    assert response.status_code == 302
    # Add more assertions as needed

