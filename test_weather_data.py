import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from weather_data import fetch_json, parse_records, init_db, upsert

DB_FILE = "test_data.db"

@pytest.fixture
def db_connection():
    # Setup: Create an in-memory SQLite database for testing
    conn = sqlite3.connect(DB_FILE)
    yield conn
    # Teardown: Close the database connection
    conn.close()

@patch("weather_data.requests.get")
def test_fetch_json(mock_get):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"cwaopendata": {"resources": {"resource": {"data": {"agrWeatherForecasts": {"weatherForecasts": {"location": []}}}}}}}
    mock_get.return_value = mock_response

    # Call the function
    result = fetch_json()

    # Assertions
    mock_get.assert_called_once()
    assert result == mock_response.json.return_value

@patch("weather_data.fetch_json")
def test_parse_records(mock_fetch_json):
    # Mock the JSON data
    mock_fetch_json.return_value = {
        "cwaopendata": {
            "resources": {
                "resource": {
                    "data": {
                        "agrWeatherForecasts": {
                            "weatherForecasts": {
                                "location": [
                                    {
                                        "locationName": "北部地區",
                                        "weatherElements": {
                                            "MaxT": {"daily": [{"dataDate": "2025-05-12", "temperature": "30"}]},
                                            "MinT": {"daily": [{"dataDate": "2025-05-12", "temperature": "20"}]}
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    }

    # Call the function
    records = parse_records(mock_fetch_json.return_value)

    # Assertions
    assert len(records) == 1
    assert records[0] == {
        "regionName": "北部地區",
        "dataDate": "2025-05-12",
        "maxt": 30.0,
        "mint": 20.0
    }

def test_init_db(db_connection):
    # Call the function
    init_db(db_connection)

    # Assertions
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TemperatureForecasts';")
    assert cursor.fetchone() is not None

def test_upsert(db_connection):
    # Setup: Initialize the database
    init_db(db_connection)

    # Test data
    rows = [
        {"regionName": "北部地區", "dataDate": "2025-05-12", "mint": 20.0, "maxt": 30.0},
        {"regionName": "北部地區", "dataDate": "2025-05-13", "mint": 21.0, "maxt": 31.0}
    ]

    # Call the function
    upsert(db_connection, rows)

    # Assertions
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM TemperatureForecasts;")
    results = cursor.fetchall()
    assert len(results) == 2
    assert results[0][1:] == ("北部地區", "2025-05-12", 20.0, 30.0)
    assert results[1][1:] == ("北部地區", "2025-05-13", 21.0, 31.0)
