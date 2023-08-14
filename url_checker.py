import requests
import pandas as pd
import sqlalchemy as db

# Setting my API key
api_key = "AIzaSyBzRNE9NegrNTaZlgTjHVDYzranvqeIBBY"

# Prompt the user to enter the URL they want to check
user_url = input("Enter a URL to check its safety: ")

# Construct the request payload
payload = {
    "client": {
        "clientId": "969300417709-p0it24usbl1qbbf09gpv1ed9fm765qaq.apps.googleusercontent.com",
        "clientVersion": "1.0"
    },
    "threatInfo": {
        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
        "platformTypes": ["ANY_PLATFORM"],
        "threatEntryTypes": ["URL"],
        "threatEntries": [{"url": user_url}]
    }
}

# Send the request using a post request
response = requests.post(
    "https://safebrowsing.googleapis.com/v4/threatMatches:find", 
    headers={"Content-Type": "application/json"},
    params={"key": api_key},
    json=payload
)

# Check the response and return the output based on the response
if response.status_code == 200:
    data = response.json()
    print(data)
    # Process the data returned from the API
    if not data:  # If the URL returns an empty JSON response, no threat has been detected
        print("This site looks safe. No Malware/Social Engineering detected.")
        safety_status = "Safe"
    else:
        print(data)
        safety_status = "Unsafe"       
else:
    print("Request failed with status code:", response.status_code)
    safety_status = "Failed"

# Creating the database
if data:
    # convert the dictionary (data) into a pandas dataframe, check if it is empty first
    pdf = pd.DataFrame(data) 
    print(pdf)

    # Check if the DataFrame is empty
    if not pdf.empty:
        # Extract the required fields from the "matches" column
        if "matches" in pdf.columns:
            matches_data = pdf["matches"].apply(lambda x: {"url": x["threat"]["url"], "threatType": x["threatType"]})
            matches_df = pd.DataFrame(matches_data.tolist()) #since a dictionary cannot be directly inserted

            # create an engine object
            engine = db.create_engine('sqlite:///urls_collection.db')

            # create and send SQL table from the matches DataFrame
            matches_df.to_sql('unsafe_urls', con=engine, if_exists='replace', index=False)

            # write a query and print out the results:
            with engine.connect() as connection:
                query_result = connection.execute(db.text("SELECT * FROM unsafe_urls;")).fetchall()

                print("Data in unsafe_urls table:")
                print(pd.DataFrame(query_result))

def check_url_with_apivoid(api_key, url):
    endpoint = f"https://endpoint.apivoid.com/urlrep/v1/pay-as-you-go/?key={api_key}&url={url}"
    response = requests.get(endpoint)

    if response.status_code == 200:
        json_data = response.json()

        # convert the dictionary (json_data) into a JSON string
        json_string = json.dumps(json_data)

        # create an engine object
        engine = db.create_engine('sqlite:///urls_collection.db')

        # create and send SQL table from the JSON string
        pd.DataFrame({'data': [json_string]}).to_sql('url_report', con=engine, if_exists='replace', index=False)

        # write a query and print out the results:
        with engine.connect() as connection:
            query_result = connection.execute(db.text("SELECT * FROM url_report;")).fetchall()
            print(pd.DataFrame(query_result))

        return json_data
    else:
        return None

def main():
    api_key = "bdfbbcf720e69d4c5ce551963db1dee8a29a9923"

    while True:
        user_url = input("Enter the URL you want to check (or 'exit' to quit): ")

        if user_url.lower() == "exit":
            break

        result = check_url_with_apivoid(api_key, user_url)
        if result:
            formatted_json = json.dumps(result, indent=2)  # Format the JSON data
            print(formatted_json)
        else:
            print("Error occurred. Please check your API key or URL and try again.")

if __name__ == "__main__":
    main()
