import requests
import argparse
import json
import pandas as pd
import os
from datetime import datetime

def get_api_response(monitoring_ref, line_ref=None):
    # URL of the IDFM Stop Monitoring API - unitary request
    url = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring'

    # Parameters to be included in the URL
    params = {'MonitoringRef': monitoring_ref}
    
    # Include LineRef in parameters if it's provided
    if line_ref:
        params['LineRef'] = line_ref

    # The header must contain the API key: apikey, please replace #YOUR API KEY with your API key
    headers = {'Accept': 'application/json', 'apikey': '2oDDJ09Zo5pWhI3z1vKDtqnGVR7Nduk2'}

    # Check if the --All flag is provided
    if line_ref == 'ALL':
        # Modify the URL and remove MonitoringRef parameter for global request
        url = 'https://prim.iledefrance-mobilites.fr/marketplace/estimated-timetable'
        params.pop('MonitoringRef', None)

    # Sending the request to the server with parameters
    req = requests.get(url, headers=headers, params=params)

    # Displaying the response status code
    print('Status:', req)

    # Try to parse the content as JSON and print in a pretty format
    try:
        json_response = json.loads(req.content)
        print(json.dumps(json_response, indent=2))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")

    # Creating a folder to store responses if it doesn't exist
    folder_name = 'api_responses'
    os.makedirs(folder_name, exist_ok=True)

    # Creating a filename based on parameters and current date and time
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{monitoring_ref.replace(':', '_')}_{line_ref.replace(':', '_') if line_ref else ''}_{timestamp}.json"
    file_path = os.path.join(folder_name, filename)

    # Writing the received response to a json file
    with open(file_path, 'w') as file:
        json.dump(json_response, file, indent=2)

    print(f"Response saved to: {file_path}")

    # Calling the function to convert json to csv
    json_to_csv(json_response, file_path)

def json_to_csv(json_data, file_path):
    # Extracting relevant data
    service_delivery = json_data["Siri"]["ServiceDelivery"]
    monitored_stop_visits = service_delivery["StopMonitoringDelivery"][0]["MonitoredStopVisit"]

    # Flattening nested structures
    df = pd.json_normalize(monitored_stop_visits, sep='_')
    # ResponseTimestamp is not included in the dataframe, so we add it manually
    df['ResponseTimestamp'] = service_delivery['ResponseTimestamp']

    # Replace specified strings in column names
    str_replace = ['FramedVehicleJourneyRef_', 'MonitoredVehicleJourney_', 'MonitoredCall_', '_value']

    for i in str_replace: 
        df.columns = df.columns.str.replace(i, '')

    # Drop columns
    columns_to_drop = ['DataFrameRef', 'ArrivalStatus', 'TrainNumbers_TrainNumberRef']
    df = df.drop(columns_to_drop, axis=1)

    # Convert date columns to datetime format
    date_columns = ["RecordedAtTime", "ExpectedArrivalTime", "ExpectedDepartureTime", "ResponseTimestamp"]
    df[date_columns] = df[date_columns].apply(pd.to_datetime)

    # Convert date columns to GMT+1
    gmt_date_columns = ["RecordedAtTime", "ExpectedArrivalTime", "ExpectedDepartureTime"]
    df[gmt_date_columns] = df[gmt_date_columns].apply(lambda x: x.dt.tz_convert('Europe/Paris'))

    # Save dataframe to csv file
    df.to_csv(f"{file_path.replace('.json', '.csv')}", index=False)

if __name__ == "__main__":
    # Setting up command-line argument parsing
    parser = argparse.ArgumentParser(description='Script to query API with MonitoringRef and optional LineRef')
    parser.add_argument('--MonitoringRef', help='Monitoring reference')
    parser.add_argument('--LineRef', help='Line reference (optional)')
    parser.add_argument('--All', action='store_true', help='Global flag for sending a GET request with LineRef=ALL')

    # Parsing the command-line arguments
    args = parser.parse_args()

    # Extracting MonitoringRef and LineRef from the command-line arguments
    monitoring_ref = args.MonitoringRef
    line_ref = args.LineRef

    # Checking if --all flag is provided
    if args.All:
        # If LineRef or MonitoringRef is provided with --all, raise an error
        if line_ref or monitoring_ref:
            raise ValueError("Error: --All flag cannot be used with --LineRef or --MonitoringRef")
        else:
            # Modify the parameters for global request
            line_ref = 'ALL'
            monitoring_ref = ''  # No MonitoringRef parameter for global request

    # Calling the function to make the API request
    get_api_response(monitoring_ref, line_ref)
