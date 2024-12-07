from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

# Database connection setup
db_connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=tcp:chittitu.database.windows.net,1433;"
    "Database=chittitu_ssms;"
    "Uid=chittitu;"
    "Pwd=tulasi_2001;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

@app.route('/insert-energy-usage', methods=['POST'])
def insert_energy_usage():
    # Read JSON data from the request
    data = request.json

    # Define valid options
    valid_appliances = ["HVAC", "Lighting", "Dishwasher", "Electronics", "Washing Machine", "Refrigerator"]
    valid_occupancy_statuses = ["Occupied", "Unoccupied"]
    valid_seasons = ["Summer", "Winter", "Autumn", "Spring"]
    valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Input validation
    try:
        if data['appliance'] not in valid_appliances:
            return jsonify({"error": "Invalid appliance. Allowed values are: HVAC, Lighting, Dishwasher, Electronics, Washing Machine, Refrigerator"}), 400
        if data['occupancy_status'] not in valid_occupancy_statuses:
            return jsonify({"error": "Invalid occupancy status. Allowed values are: Occupied, Unoccupied"}), 400
        if data['season'] not in valid_seasons:
            return jsonify({"error": "Invalid season. Allowed values are: Summer, Winter, Autumn, Spring"}), 400
        if data['day_of_week'] not in valid_days:
            return jsonify({"error": "Invalid day of the week. Allowed values are: Monday to Sunday"}), 400
        if data['home_id'] < 0 or data['usage_duration_minutes'] < 0 or data['energy_consumption_kWh'] < 0 or data['temperature_setting_C'] < 0:
            return jsonify({"error": "Numeric values (home_id, energy_consumption_kWh, temperature_setting_C, usage_duration_minutes) must be non-negative"}), 400
        if data['holiday'] not in [0, 1]:
            return jsonify({"error": "Holiday must be either 0 (no) or 1 (yes)"}), 400
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400

    try:
        # Connect to the database
        conn = pyodbc.connect(db_connection_string)
        cursor = conn.cursor()

        # Insert query
        insert_query = """
        INSERT INTO EnergyUsage (
            timestamp, home_id, energy_consumption_kWh, temperature_setting_C, 
            occupancy_status, appliance, usage_duration_minutes, season, 
            day_of_week, holiday
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # Execute the query
        cursor.execute(insert_query, (
            data['timestamp'], 
            data['home_id'], 
            data['energy_consumption_kWh'], 
            data['temperature_setting_C'], 
            data['occupancy_status'], 
            data['appliance'], 
            data['usage_duration_minutes'], 
            data['season'], 
            data['day_of_week'], 
            data['holiday']
        ))
        conn.commit()

        return jsonify({"message": "Data inserted successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
