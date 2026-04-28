# Mass access request pull and data organisation + accept/reject access requests

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

dataset_doi = 'https://doi.org/THIS.IS/MY/DOI'                                     # Enter DOI link here in https or doi: format
api_token_origin = 'INSERT_API_KEY_HERE'                                           # Fetch your API token and paste it here



# Only one of these can can be selected at a time (comment out the unused one)
run_access_processor = False                                                       # Runs function stream that creates request CSV sheet
#run_access_processor = True                                                       # Runs access Granting/Rejecting function stream



csv_granter_file = r'C:THIS/IS/MY/DIRECTORY/TO/FILE.csv'                           # Enter CSV file directory here - keep 'r' before string if on Windows




################################################################################
#-------------------------------------API INFO----------------------------------
################################################################################

url_base_origin = 'https://borealisdata.ca'                                        # Provide initial link for the dataverse in question
#url_base_origin = 'https://demo.borealisdata.ca'                                  # Demo URL for developer testing

headers_origin = {'X-Dataverse-key': api_token_origin}                             # Setting requests headers (for URL based API calls to pull notifications)
api_access = DataAccessApi(url_base_origin, api_token_origin)                      # Set up data access API (to fetch file access requests)
api_origin = NativeApi(url_base_origin, api_token_origin)                          # Set up NativeAPI (to fetch dataset file IDs)


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
# all list values are the same. This is the only part of the script that was vibe coded
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


# Function that fetches datafile requests and notifications.
# Outputs a CSV file by harmonizing both API calls - takes 5 arguments.
# All of which are defined above in the config section
def fetch_dataset_requests(dataset_doi, api_access, api_origin, url_base_origin, headers_origin):
    print('STARTING EXTRACTION PROCESS')
    
    files_metadata = api_origin.get_datafiles_metadata(dataset_doi)                # Use DOI to pull datafiles metadata
    files = files_metadata.json()['data']                                          # Extract data from the JSON file
    
    master_dictionary = {}                                                         # Create empty master dictionary
    for file in files:                                                             # For all files in the dataset
        file_dictionary = {}                                                       # Create file specific dictionary
        if file['restricted'] == True:                                             # If the file is restricted
            file_dictionary['File Name'] = file['label']                           # Fetch its label
            master_dictionary[file['dataFile']['id']] = file_dictionary            # Assign the datafile label to the datafile ID 
    

    
    list_for_df = []                                                               # Create an empty list
    for k, v in master_dictionary.items():                                         # For keys and items in the dictionary
        request = (api_access.list_file_access_requests(k, auth = True)).json()    # Fetch access requests for each restricted file

        try:                                                                       # Attempt the following operation
            requesters = request['data']                                           # Fetch all individuals that have requested the files
            for individual in requesters:                                          # For all individuals that have requested the files
                list_for_df.append(individual)                                     # Add the individual to a list of requestees
        
        except:                                                                    # If the operation above cannot be performed (no requests)
            print(request['message'])                                              # Print the failed request message
            pass                                                                   # Pass and continue
    
    data = pd.DataFrame(list_for_df)                                               # Create a dataframe with all requestor information
    org_data = data.groupby('email').agg(list).reset_index()                       # Merge requests by user email, list all other col values
    
    try:                                                                           # Try (not all users have validated their emails)
        org_data.drop('emailLastConfirmed', axis = 1, inplace = True)              # Attempt to drop that column
    except:                                                                        # In the event that there is no such column
        print('No "Email Last Confirmed" Field')                                   # Print error message in shell
    
    org_data.drop(['displayName', 'superuser', 'deactivated', 'createdTime', 'lastLoginTime'],
                  axis = 1, inplace= True)                                                                  # Drop redundent columns
    cleaned_org_data = extract_first_list_element_df(org_data)                                              # Assess lists to see if interlist items differ.
    print()
    
    listed_notifs = pd.DataFrame(pull_notifications(url_base_origin, headers_origin))                       # Pull all user notifications using above function
    listed_notifs.drop(['displayAsRead', 'type', 'requestorFirstName', 'requestorLastName', 'id'],          # Drop redundent columns
                       axis = 1, inplace = True)
    
    list_val = []                                                                   # Create empty list
    for date in listed_notifs['sentTimestamp']:                                     # Extract the time stamps of the notification
        d = date.split('T')                                                         # Split time string at T
        list_val.append(d[0])                                                       # Use only the request day, month, and year
    listed_notifs['sentTimestamp'] = list_val                                       # Edit the time value to reflect modifications
    
    li_notifs = listed_notifs.groupby('requestorEmail').agg(list).reset_index()     # Group notifications by requestor email
    cleaned_notifs = extract_first_list_element_df(li_notifs)                       # Assess cell value lists using function defined above
    
    cleaned_notifs.rename(columns = {'requestorEmail': 'email',
                                     'sentTimestamp': 'Request Date'}, inplace = True)      # Rename columns of interest of increased clarity and harmonisation
    
    
    merged_request = pd.merge(cleaned_org_data, cleaned_notifs, on = 'email')               # Merge both dataframes on user email
    merged_request.rename(columns = {'dataFileDisplayName': 'File Names',                   # Rename columns of interest of increased clarity
                                     'dataFileId': 'File ID', 
                                     'authenticationProviderId': 'Authentificator'}, 
                          inplace = True)
    
    valz = merged_request.pop('Request Date')                                    # Remove and assign request time column to a variable
    merged_request.insert(0, 'Request Date', valz)                               # Place this variable at the start of the dataframe
    merged_request['Granted Access?'] = 'Pending'                                # Enter 'Pending' as column values for CSV file creation
    merged_request.drop('id', axis = 1, inplace = True)                          # Drop the dataframe index column
    
    if 'https:/' in dataset_doi:
        dataset_doi = dataset_doi.replace('https://doi.org/', 'doi:')
    
    merged_request.to_csv(f'Requestor File for {dataset_doi}.csv', index = False)           # Export CSV file in the same directory as this python file.

    print()
    print(f'CSV Sheet Created in {os.getcwd()}')


################################################################################
#--------------------------------ACCESS GRANTING--------------------------------
################################################################################

# Function that formats dictionaries for subsequent API push
# returns a list of dictionaries - takes 1 argument
# Argument is a dataframe cut defined in access_processor
def formatter(sub_dataframe):
    access_status = pd.DataFrame()                                               # Create empty dataframe
    access_status['identifier'] = sub_dataframe['identifier']                    # Create analog column for user IDs
    access_status['File ID'] = sub_dataframe['File ID']                          # Create analog column for File IDs
    
    listed_push = access_status.set_index(access_status.columns[0])[access_status.columns[1]].to_dict()        # Create a dictionary where K is the identifier and V the file ID
    
    entry_list = []                                                              # Create empty list in which to append dictionaries
    for k, v in listed_push.items():                                             # For keys and values in access dictionary
        
        if isinstance(eval(v), list):                                            # If the value is a list (meaning several access requests for a same user)
            listed_i = eval(v)                                                   # Convert string to list and assign to a variable
            for vals in listed_i:                                                # For datafile IDs in the list
                novel_dictionary = {}                                            # Create an empty dictionary
                novel_dictionary[k] = vals                                       # Assign each list item to user ID as key
                entry_list.append(novel_dictionary)                              # Add the dictionary to the list
        else:                                                                    # If the value is not a list
            novel_dictionary = {}                                                # Create an empty dictionary
            novel_dictionary[k] = eval(v)                                        # Assign v as integer to user ID
            entry_list.append(novel_dictionary)                                  # Add to dictionary
    print(entry_list)                                                            # Print the created dictionary
    print()                                                                      # Print empty space for shell legibility
    
    return entry_list                                                            # Return list of dictionary


# Function that automatically grants/rejects access as a function of CSV column value
# Iterates through dataframe to grant/reject access - takes 4 arguments
# All of which are identified above
def access_processor(csv_granter_file, api_access, url_base_origin, headers_origin):
    
    frame = pd.read_csv(csv_granter_file)                                        # Load CSV file as a dataframe
    access_vetting = frame.loc[frame['Granted Access?'] == 'Granted']            # Creates a secondary dataframe for access granted
    access_rejector = frame.loc[frame['Granted Access?'] == 'Rejected']          # Creates a secondary dataframe for access rejected
    #access_revoker = frame.loc[frame['Granted Access?'] == 'Revoked']
    
    
    ############################################################################
    #------------------------------GRANTING ACCESS------------------------------
    ############################################################################
    print('STARTING APPROVAL GRANTING')
    
    entry_list = formatter(access_vetting)
    
    for demands in entry_list:
        for k, v in demands.items():
            url = f'{url_base_origin}/api/access/datafile/{v}/grantAccess/{k}'       # Create URL for API call
            resp = requests.put(url, headers = headers_origin)
            print(url)
            print(resp.json())
            print()

    print('COMPLETED APPROVAL GRANTING PROCESS')
    print()
    
    
    ############################################################################
    #------------------------------REJECTING ACCESS-----------------------------
    ############################################################################
    print('STARTING REJECTION PROCESS')
    
    rejected_list = formatter(access_rejector)
    
    for demands in rejected_list:
        for k, v in demands.items():
            url = f'{url_base_origin}/api/access/datafile/{v}/rejectAccess/{k}'       # Create URL for API call
            resp = requests.put(url, headers = headers_origin)
            print(url)
            print(resp.json())
            print()
    
    print('COMPLETED REJECTION PROCESS')
    print()
    
    
    ############################################################################
    #------------------------------REVOKING ACCESS------------------------------
    ############################################################################    
    
    # This functionality has yet to be developed. 



################################################################################
#--------------------------------FUNCTION RUNNING-------------------------------
################################################################################


if run_access_processor == False:
    fetch_dataset_requests(dataset_doi, api_access, api_origin, url_base_origin, headers_origin)

if run_access_processor == True:
    access_processor(csv_granter_file, api_access, url_base_origin, headers_origin)

print('PROCESS DONE')

