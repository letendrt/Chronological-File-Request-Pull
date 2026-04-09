# Mass access request pull and data organisation

################################################################################
#-------------------------------------LIBRARIES---------------------------------
################################################################################

import json
import ast
import pandas as pd
import requests
import pyDataverse.utils as utils
from pyDataverse.api import NativeApi, DataAccessApi


################################################################################
#------------------------------------PARAMETERS---------------------------------
################################################################################

# YOU ONLY NEED TO EDIT THE PARAMETERS HERE
# THE REST WILL BE COMPLETED AUTOMATICALLY ON YOUR BEHALF

dataset_doi = 'ENTER_DOI_HERE'                                          # Enter DOI link here in https or doi: format
api_token_origin = 'ENTER_API_KEY_HERE'                                 # Fetch your API token and paste it here


################################################################################
#-------------------------------------API INFO----------------------------------
################################################################################

url_base_origin = 'https://borealisdata.ca'                            # Provide initial link for the dataverse in question
#url_base_origin = 'https://demo.borealisdata.ca'                      # Demo URL for developer testing
headers_origin = {'X-Dataverse-key': api_token_origin}                 # Setting requests headers (for URL based API calls to pull notifications)
api_access = DataAccessApi(url_base_origin, api_token_origin)          # Set up data access API (to fetch file access requests)
api_origin = NativeApi(url_base_origin, api_token_origin)              # Set up NativeAPI (to fetch dataset file IDs)


################################################################################
#-----------------------------------CODE PROPER---------------------------------
################################################################################

# Function that fetches all user notifications
# Takes 2 arguments: the URL base origin for the dataverse, and the requests headers
# This function is mandatory to fetch the precise file access request time
# Since they're not retrieved with file access request API calls
def pull_notifications(url_base_origin, headers_origin):
    
    request_notif_list = []                                                             # Create empty list
    url = f'{url_base_origin}/api/notifications/all?inAppNotificationFormat=true'       # Create URL for API call
    notif_pull = (requests.get(url, headers = headers_origin)).json()                   # Pull and convert to JSON the notification requests
    
    for notifs in notif_pull['data']['notifications']:                                  # From the JSON file, fetch the notification child
        if notifs['type'] == 'REQUESTFILEACCESS':                                       # If it is a file access request notification
            request_notif_list.append(notifs)                                           # Add it to the previously created list
    
    return request_notif_list                                                           # Return the list


# Function that fetches the first entry of listed items, if and only if
# all list values are the same. 
# Takes a singular argument, which is a df built from a file access request API call
def extract_first_list_element_df(df):                                              
    processed_df = df.copy()                                                     # Create a copy of the dataframe

    def _extract_element(value):                                                 # Function through which all cell values are passed
        try:                                                                     # Try the following task
            evaluated_value = ast.literal_eval(str(value))                       # Convert string value to python assessed class type
            if isinstance(evaluated_value, list) and evaluated_value:            # If the string is indeed a list
                
                if all(x == evaluated_value[0] for x in evaluated_value):        # Check if all elements in the list are the same
                    return evaluated_value[0]                                    # return item in first list index
                
                else:                                                            # If not all elements are the same
                    return value                                                 # return the original value (list string)
            
            else:                                                                # If value not a list
                return value                                                     # return original value
        
        except (ValueError, SyntaxError):                                        # If an error is encountered in the process
            return value                                                         # Return original value

    for col in processed_df.columns:                                             # For each column in the dataframe
        processed_df[col] = processed_df[col].apply(_extract_element)            # Apply the above function for each value
        
    return processed_df                                                          # Return the newly edited (and created) dataframe



def fetch_dataset_requests(dataset_doi, api_access, api_origin, url_base_origin, headers_origin):
    print('STARTING PROCESS')
    
    files_metadata = api_origin.get_datafiles_metadata(dataset_doi)              # Use DOI to pull datafiles metadata
    files = files_metadata.json()['data']                                        # Extract data from the JSON file
    
    master_dictionary = {}                                                       # Create empty master dictionary
    for file in files:                                                           # For all files in the dataset
        file_dictionary = {}                                                     # Create file specific dictionary
        if file['restricted'] == True:                                           # If the file is restricted
            file_dictionary['File Name'] = file['label']                         # Fetch its label
            master_dictionary[file['dataFile']['id']] = file_dictionary          # Assign the datafile label to the datafile ID 
    
    list_for_df = []                                                               # Create an empty list
    for k, v in master_dictionary.items():                                         # For keys and items in the dictionary
        request = (api_access.list_file_access_requests(k, auth = True)).json()    # Fetch access requests for each restricted file

        try:                                                        # Attempt the following operation
            requesters = request['data']                            # Fetch all individuals that have requested the files
            for individual in requesters:                           # For all individuals that have requested the files
                list_for_df.append(individual)                      # Add the individual to a list of requestees
        
        except:                                            # If the operation above cannot be performed (no requests)
            print(request['message'])                      # Print the failed request message
            pass                                           # Pass and continue
    
    data = pd.DataFrame(list_for_df)                                                                                        # Create a dataframe with all requestor information
    org_data = data.groupby('email').agg(list).reset_index()                                                                # Merge requests by user email, list all other col values
    org_data.drop(['displayName', 'superuser', 'deactivated', 'emailLastConfirmed', 'createdTime', 'lastLoginTime'],        # Drop redundent columns
                  axis = 1, inplace= True)
    cleaned_org_data = extract_first_list_element_df(org_data)                                                              # Assess lists to see if interlist items differ.
    print()
    
    
    listed_notifs = pd.DataFrame(pull_notifications(url_base_origin, headers_origin))                        # Pull all user notifications using above function
    listed_notifs.drop(['displayAsRead', 'type', 'requestorFirstName', 'requestorLastName', 'id'],           # Drop redundent columns
                       axis = 1, inplace = True)
    
    list_val = []                                                                # Create empty list
    for date in listed_notifs['sentTimestamp']:                                  # Extract the time stamps of the notification
        d = date.split('T')                                                      # Split time string at T
        list_val.append(d[0])                                                    # Use only the request day, month, and year
    listed_notifs['sentTimestamp'] = list_val                                    # Edit the time value to reflect modifications
    
    li_notifs = listed_notifs.groupby('requestorEmail').agg(list).reset_index()    # Group notifications by requestor email
    cleaned_notifs = extract_first_list_element_df(li_notifs)                      # Assess cell value lists using function defined above
    
    cleaned_notifs.rename(columns = {'requestorEmail': 'email', 
                                     'sentTimestamp': 'Request Date'}, inplace = True)      # Rename columns of interest of increased clarity and harmonisation
    
    
    merged_request = pd.merge(cleaned_org_data, cleaned_notifs, on = 'email')               # Merge both dataframes on user email
    merged_request.rename(columns = {'dataFileDisplayName': 'File Names', 
                                     'dataFileId': 'File ID', 
                                     'authenticationProviderId': 'Authentificator'}, 
                          inplace = True)                                                   # Rename columns of interest of increased clarity
    
    valz = merged_request.pop('Request Date')                                    # Remove and assign request time column to a variable
    merged_request.insert(0, 'Request Date', valz)                               # Place this variable at the start of the dataframe
    merged_request.drop('id', axis = 1, inplace = True)                          # Drop the dataframe index column
    
    merged_request.to_csv('Requestor File.csv', index = False)                   # Export CSV file in the same directory as this python file.


    
################################################################################
#--------------------------------FUNCTION RUNNING-------------------------------
################################################################################

fetch_dataset_requests(dataset_doi, api_access, api_origin, url_base_origin, headers_origin)
print('PROCESS DONE')


