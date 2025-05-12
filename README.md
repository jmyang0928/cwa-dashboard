# Weather Forecast Web Application

This project is a weather forecast web application that provides a user-friendly interface for visualizing temperature forecasts for different regions in Taiwan. The application is built using Python and leverages the Streamlit framework for the frontend, SQLite for data storage, and an external API for fetching weather data.

## Features

- **Interactive Web Interface**: Built with Streamlit, the app allows users to select a region and view temperature forecasts for the upcoming week.
- **Data Visualization**: Displays temperature trends using Altair charts.
- **Database Integration**: Stores weather data in an SQLite database for efficient querying and caching.
- **Command-Line Utility**: Includes a script for fetching, listing, and dumping weather data.

## Project Structure

- `app.py`: The main Streamlit application file for the web interface.
- `weather_data.py`: A command-line utility script for fetching weather data, initializing the database, and managing records.
- `data.db`: SQLite database file for storing weather data.
- `requirements.txt`: Python dependencies required for the project.
- `Pipfile`: Specifies the Python version and additional package management details.

## Installation

1. Clone the repository and navigate to the project directory.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure you have Python 3.11 installed, as specified in the `Pipfile`.

## Usage

### 1. Setting Up the Environment

- Create a `.env` file in the project directory based on the provided `.env.example` file:

  ```bash
  cp .env.example .env
  ```

- Add your API token to the `.env` file:

  ```bash
  CWA_TOKEN=your_api_token_here
  ```

### 2. Running the Web Application

- Start the Streamlit app:
  ```bash
  streamlit run app.py
  ```

### 3. Command-Line Utility

- Fetch weather data and update the database:
  ```bash
  python weather_data.py fetch
  ```
- List all stored regions:
  ```bash
  python weather_data.py regions
  ```
- Dump all records for a specific region:
  ```bash
  python weather_data.py dump <region_name>
  ```

## Quick Start

### Run the Application

To start the application, use the following command:

```bash
./run.sh
```

### Run Tests

To execute the tests, use the following command:

```bash
./test.sh
```

## Running Tests

To ensure the functionality of the application, you can run the test suite using `pytest`:

```bash
pytest test_weather_data.py
```

This will execute the test cases defined in `test_weather_data.py` to validate the core functionalities, including data fetching, parsing, database initialization, and upserting records.

## Dependencies

- Python 3.11
- Streamlit
- Pandas
- Altair
- Requests
- Python-dotenv
- Pytest

## License

This project is licensed under the MIT License. See the LICENSE file for details.
