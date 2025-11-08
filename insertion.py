import pandas as pd
import requests
import json

# configurations
API_URL = "http://127.0.0.1:5000/students"   # Your running Flask API endpoint
CSV_FILE = "sample_students_bulk.csv"         # Path to your CSV file

#  READ CSV FILE 
try:
    df = pd.read_csv(CSV_FILE)
    print(f"✅ Loaded {len(df)} students from CSV file.")
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    exit()

# CONVERT TO JSON
students_json = df.to_dict(orient='records')
print("🧾 Sample record:\n", json.dumps(students_json[0], indent=2))

#  SEND POST REQUEST TO API 
try:
    response = requests.post(API_URL, json=students_json)

    if response.status_code in [200, 201]:
        print(f"✅ Successfully inserted {len(students_json)} students!")
    else:
        print(f"⚠️ Failed to insert. Status Code: {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.ConnectionError:
    print("❌ Could not connect to the API. Make sure Flask is running.")
except Exception as e:
    print(f"❌ Error sending request: {e}")
