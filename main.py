import requests
import sqlite3
import matplotlib.pyplot as plt
import sys
import pandas as pd
from bidi.algorithm import get_display
from datetime import datetime


# function to log the operation
def log_operation(message):
    log_filename = "script_log.txt"
    log_message = f"{datetime.now()} - {message}\n"
    with open(log_filename, "a") as log_file:
        log_file.write(log_message)
    print(log_message)


# function to get alert history from the api itself
def fetch_alerts_history(api_url):
    log_operation("Starting fetch alerts history...")
    try:
        response = requests.get(api_url)
        # Check for success
        if response.status_code == 200:
            json_data = response.json()
            log_operation(f"Fetching alerts history succeeded - there are {len(json_data)} alerts in last 24 hours")
            return json_data
        else:
            log_operation(f"API call failed with status code: {response.status_code}  "
                          f"... and reponse text: {response.text}... exit script")
            sys.exit(1)
    except Exception as e:
        log_operation(f"An error occurred: {e} ... exit script")
        sys.exit(1)

#function to get the maximum date from DB
def get_max_date_from_database():
    try:
        connection = sqlite3.connect(ALERTS_DB)
        cursor = connection.cursor()
        # Execute a SELECT query to get the maximum date
        cursor.execute("SELECT MAX(alertDate) FROM alerts")
        max_date = cursor.fetchone()[0]
        connection.close()
        return max_date
    except Exception as e:
        log_operation(f"An error occurred while getting the maximum date from the database: {e}")
        return None

#function to save new records to DB
def save_to_database(data):
    log_operation("Starting save alerts to db...")
    try:
        connection = sqlite3.connect(ALERTS_DB)
        cursor = connection.cursor()
        # Create a table if it doesn't exist(first run)
        cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (
                            id INTEGER PRIMARY KEY,
                            alertDate DATE,
                            title TEXT,
                            data TEXT,
                            category TEXT
                        )''')
        # Get the maximum date from the database
        max_date = get_max_date_from_database()
        # If there is no maximum date, means it's the first run
        max_date = max_date or "12/01/2023"
        new_data_written = False
        # Insert only new data into the table
        for item in data:
            alert_date = item.get("alertDate", "")
            if alert_date > max_date:
                cursor.execute("INSERT INTO alerts (alertDate, title, data, category) VALUES (?, ?, ?, ?)",
        (item.get("alertDate",""), item.get("title", ""), item.get("data", ""), item.get("category", "")))
                new_data_written = True
        connection.commit()
        connection.close()
        if new_data_written:
            log_operation("New data saved to the database - there are new alerts since last run")
        else:
            log_operation("Nothing to save! no new alerts since last run")
    except Exception as e:
        log_operation(f"An error occurred while saving to the database: {e}")
#function to get dataframe with the alerts
def prepare_for_dashboards():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(ALERTS_DB)
        # Query data from the database into a DataFrame
        query = "SELECT * FROM alerts"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        log_operation(f"An error occurred while saving to the database: {e}")
# Plotting the number of alerts for each hour
def plot_alerts_per_hour(df):
    try:
        df['alertDate'] = pd.to_datetime(df['alertDate'])

        # Group by the hour of the day and calculate the count of alerts
        df['hour'] = df['alertDate'].dt.hour
        alert_counts_per_hour = df.groupby('hour').size()

        plt.figure(figsize=(12, 6))
        plt.plot(alert_counts_per_hour.index, alert_counts_per_hour.values, marker='o')
        plt.title('Number of alerts per hour of the day')
        plt.xlabel('Hour of the day')
        plt.ylabel('Number of alerts')
        plt.xticks(range(24))  # Display only whole hours on the x-axis
        plt.grid(True)
        plt.show()
        log_operation("plot_alerts_per_hour succeeded")
    except Exception as e:
        log_operation(f"An error occurred while trying to run plot_alerts_per_hour: {e}")

# Plotting the number of alerts for each date
def plot_alerts_per_date(df):
    try:

        df['alertDate'] = pd.to_datetime(df['alertDate'])

        # Group by day and calculate the count of alerts
        alert_counts_per_day = df.groupby(df['alertDate'].dt.date).size()

        alert_counts_per_day.plot(kind='bar', color='orange')
        plt.title('Number of alerts per day')
        plt.xlabel('Date')
        plt.ylabel('Number of alerts')
        plt.figure(figsize=(10, 10))
        plt.show()
        log_operation("plot_alerts_per_date succeeded")
    except Exception as e:
        log_operation(f"An error occurred while trying to run plot_alerts_per_date: {e}")

 # Plotting a pie chart for the top 10 places distribution
def plot_top_10_places(df):
    try:
        place_count = df['data'].value_counts().nlargest(10)
        plt.pie(place_count, labels=[get_display(label) for label in place_count.index], autopct='%1.1f%%',
                startangle=140)
        plt.title('Top 10 places that were alerted since 1.12.23')
        plt.figure(figsize=(10, 10))
        plt.show()
        log_operation("plot_top_10_places succeeded")
    except Exception as e:
        log_operation(f"An error occurred while trying to run plot_top_10_places: {e}")

if __name__ == "__main__":
    log_operation("Starting new run")
    API_URL = "https://www.oref.org.il/WarningMessages/History/AlertsHistory.json"
    ALERTS_DB="alerts_data.db"
    # Fetch data from the API
    alerts_data = fetch_alerts_history(API_URL)

    # Save new data to the database
    save_to_database(alerts_data)

    # manipulation and graphs section
    log_operation("Starting dashboards part")

    df=prepare_for_dashboards()

    plot_alerts_per_hour(df)

    plot_alerts_per_date(df)

    plot_top_10_places(df)


    log_operation("Finished run")
