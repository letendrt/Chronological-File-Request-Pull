# Mass access request pull and data organisation

################################################################################
#-------------------------------------LIBRARIES---------------------------------
################################################################################

import os
import ast
import json
import requests
import pandas as pd
import pyDataverse.utils as utils
from pyDataverse.api import NativeApi, DataAccessApi

# Importing GUI tools
import tkinter as tk
from tkinter import *
from tkinter import filedialog



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
    print()
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
    merged_request.to_csv('Requestor File.csv', index = False)                   # Export CSV file in the same directory as this python file.
    
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
    
    listed_push = access_status.set_index(
        access_status.columns[0])[access_status.columns[1]].to_dict()            # Create a dictionary where K is the identifier and V the file ID
    
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
    
    entry_list = formatter(access_vetting)                                           # Submit the sub-dataframe to the formatter function
    
    for demands in entry_list:                                                       # For demands in returned list
        for k, v in demands.items():                                                 # For keys and values in the dictionary
            url = f'{url_base_origin}/api/access/datafile/{v}/grantAccess/{k}'       # Create URL for API call
            resp = requests.put(url, headers = headers_origin)                       # Push access granting request
            print(url)
            print(resp.json())
            print()

    print('COMPLETED APPROVAL GRANTING PROCESS')
    print()
    
    
    ############################################################################
    #------------------------------REJECTING ACCESS-----------------------------
    ############################################################################
    print('STARTING REJECTION PROCESS')
    
    rejected_list = formatter(access_rejector)                                        # Submit sub-dataframe to the formatter function
    
    for demands in rejected_list:                                                     # For demands in returned list 
        for k, v in demands.items():                                                  # For keys and values in the dictionary
            url = f'{url_base_origin}/api/access/datafile/{v}/rejectAccess/{k}'       # Create URL for API call
            resp = requests.put(url, headers = headers_origin)                        # Push access granting request
            print(url)
            print(resp.json())
            print()
    
    print('COMPLETED REJECTION PROCESS')
    print()
    
    
    print('PROCESS DONE')
    
    ############################################################################
    #------------------------------REVOKING ACCESS------------------------------
    ############################################################################    
    
    # This functionality has yet to be developed. 



################################################################################
#----------------------------------USER INTERFACE-------------------------------
################################################################################


# Background and Font Colours
uni_col = '#FDD44D'
font_col = 'black'
box_col = '#F3F0E6'


# Setting up tkinter window
root = Tk()
root.title('PULLING AND APPROVING REQUESTS')
root.minsize(1000, 700)
root.resizable(False, False)
root.geometry("1000x700+500+300")
root.configure(bg = uni_col)


# Font Setup
font_setting_1 = ('Baskerville', 20, "bold")
font_setting_2 = ('Baskerville', 14, 'bold')
font_setting_3 = ('Baskerville', 15, 'italic')
font_setting_4 = ('Baskerville', 12, 'bold')
font_setting_5 = ('Baskerville', 20, 'bold')
font_setting_6 = ('Baskerville', 12)


#----------------------------TEXT VALUES

# Setting up window text values
text_val_1 = "Welcome to the Request Pull and Approval Processor Tool!"
text_val_2 = "This UI is used to facilitate the usage of the mass request pull script."
text_val_3 = "Please fill in the fields below to successfully create the CSV file or to approve/reject requests!"

text_val_4 = "1) Enter your API key here;"
text_val_5 = "2) Enter the dataset DOI here;"
text_val_6 = "3) Browse for the CSV file you wish to upload;"

text_val_7 = 'Currently: No chosen file!'
text_val_8 = '--Leave unchecked if creating request CSV sheet--'


# Configurating labels with font, text, and background settings
label_1 = Label(root, text = text_val_1, fg = font_col, bg = uni_col, font = font_setting_1)
label_2 = Label(root, text = text_val_2, fg = font_col, bg = uni_col, font = font_setting_2)
label_3 = Label(root, text = text_val_3, fg = font_col, bg = uni_col, font = font_setting_2)

label_4 = Label(root, text = text_val_4, fg = font_col, bg = uni_col, font = font_setting_2)
label_5 = Label(root, text = text_val_5, fg = font_col, bg = uni_col, font = font_setting_2)
label_6 = Label(root, text = text_val_6, fg = font_col, bg = uni_col, font = font_setting_2)

label_7 = Label(root, text = text_val_7, fg = font_col, bg = uni_col, font = font_setting_4)
label_8 = Label(root, text = text_val_8, fg = font_col, bg = uni_col, font = font_setting_6)


# Placing labels on root window
label_1.place(relx = 0.5, rely = 0.01, anchor = "n")
label_2.place(relx = 0.02, rely = 0.13, anchor = 'w')
label_3.place(relx = 0.02, rely = 0.166, anchor = 'w')

label_4.place(relx = 0.09, rely = 0.24, anchor = 'w')
label_5.place(relx = 0.09, rely = 0.39, anchor = 'w')
label_8.place(relx = 0.12, rely = 0.596, anchor = 'w')



#---------------------------------BUTTON RELATED FUNCTIONS

# Checkbox and button activated functions
def click_1():
    if choiceNum_1.get() == 1:
        print(choiceNum_1.get())
        file_button_1.config(state = DISABLED)
        file_button_1.place_forget()
        label_6.place_forget()
        label_7.place_forget()
        
    else:
        print(choiceNum_1.get())
        file_button_1.config(state = NORMAL)
        file_button_1.place(relx = 0.1, rely = 0.75, anchor = 'w', width = 300, height = 40)
        label_6.place(relx = 0.09, rely = 0.69, anchor = 'w')
        label_7.place(relx = 0.1, rely = 0.81, anchor = 'w')


# Demo vs Production selection button
def click_2():
    if choiceNum_2.get() == 0:
        url_base_origin = 'https://borealisdata.ca'
        print(url_base_origin)
    else:
        url_base_origin = 'https://demo.borealisdata.ca'
        print(url_base_origin)
    
    return url_base_origin


# Button that allows for file seeking
def browseFiles_1():
    global filename_1
    filename_1 = filedialog.askopenfilename(initialdir = "/", title = "Select an XML File",
                                            filetypes = [("CSV files", "*.csv")])
     
    # Change label contents
    label_7.configure(text = filename_1)


# Button that launches script
def run_script():
    url_base_origin = click_2()
    api_token_origin = entry_1.get()
    dataset_doi = entry_2.get()
    
    headers_origin = {'X-Dataverse-key': api_token_origin}                          # Setting requests headers (for URL based API calls to pull notifications)
    api_access = DataAccessApi(url_base_origin, api_token_origin)                   # Set up data access API (to fetch file access requests)
    api_origin = NativeApi(url_base_origin, api_token_origin)                       # Set up NativeAPI (to fetch dataset file IDs)        
    
    
    if choiceNum_1.get() == 1:
        fetch_dataset_requests(dataset_doi, api_access, api_origin, url_base_origin, headers_origin)

    else:
        csv_granter_file = filename_1
        access_processor(csv_granter_file, api_access, url_base_origin, headers_origin)
    
    root.destroy()           # Close window upon starting script
    
    


#------------------TEXTBOX, CHECKBOX, AND BUTTON PARAMETERS

entry_1 = Entry(root, font = font_setting_3, fg = font_col, bg = box_col)
entry_1.insert(0, '  e.g.:    caa807d2-c4d3-48fc-a6c3-65f48a1098e9')

entry_2 = Entry(root, font = font_setting_3, fg = font_col, bg = box_col)
entry_2.insert(0, '  e.g.:    doi:10.5683/SP3/MMKTFC    or    https://doi.org/10.5683/SP3/MMKTFC')


# Placing text boxes on root window
entry_1.place(relx = 0.093, rely = 0.29, anchor = 'w', width = 750, height = 40)
entry_2.place(relx = 0.093, rely = 0.44, anchor = 'w', width = 750, height = 40)


# Integer values to assess status of checked vs unchecked boxes
choiceNum_1 = tk.IntVar()
choiceNum_2 = tk.IntVar()


# Create check boxes 
task_selection = tk.Checkbutton(
    root, 
    text = 'Check this box if Granting/Rejecting Access',
    command = click_1,
    onvalue = 0, offvalue = 1, variable = choiceNum_1)

check_box_prod_dem = tk.Checkbutton(
    root, 
    text = 'Check box for Borealis Demo',
    command = click_2,
    onvalue = 1, offvalue = 0, variable = choiceNum_2)


# Setting up checkbox style parameters
check_box_prod_dem.config(bg = uni_col, fg = font_col, font = font_setting_6)
task_selection.config(bg = uni_col, fg = font_col, font = font_setting_2)


# Deselect boxes by default
check_box_prod_dem.deselect()
task_selection.deselect()


# Position Checkboxes in root window
check_box_prod_dem.pack(side = tk.BOTTOM, anchor = tk.E)
task_selection.place(relx = 0.09, rely = 0.56, anchor = 'w')


# Creates run script button
run_backend = Button(root, text = "RUN SCRIPT", font = font_setting_5,
                     bg = 'black', fg = 'white', command = run_script)


file_button_1 = Button(root, text = "Upload CSV File", font = font_setting_3, 
                       bg = box_col, command = browseFiles_1)

file_button_1.config(state = DISABLED)

run_backend.place(relx = 0.093, rely = 0.9, anchor = 'w', width = 400, height = 50)



# GUI window loop
root.mainloop()

