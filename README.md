# Chronological Request Pull and Access Granter 🕰️📬
Chrono pull basic functionalities are up and running. Further developments on functionalities to come!

## Code Purpose 🤔❓
1) Pulls restricted file access requests by using dataset DOI;
2) Pulls user notification to extract the precise time at which the request was submitted;
3) Harmonises file access request output and time notification pull into one organised tabular/CSV file.
4) Creates template for bulk access approval, as well as bulk access rejection (CSV output).
5) Processes bulk access approval/rejection from a same submitted file (see instructions).

### ⚠️ Users of this tool must uphold their due diligence and ensure that the restricted file requestee meets the requirements to access said requested data. This tool is NOT a substitution for REB approval verification. This tool is simply to faciliate the ordering of requests, and to bulk accept/reject requests once user applications have been assessed. Always keep track of who has access to your data in a secondary worksheet.⚠️

## Minimum Python Requirements 🐍🔧
1) Local IDE (Jupyter, Wing, PyCharm, etc.)
2) Minimum python version: 3.6+

## Script Versions 💻🐝
There are two versions of the present code:
1) A [user interface version](https://github.com/letendrt/Chronological-File-Request-Pull/tree/main/User%20Interface%20Version) specifically designed for individuals with minimal to no experience programming.
2) A [script version](https://github.com/letendrt/Chronological-File-Request-Pull/tree/main/Script%20Version) designed for individuals more comfortable working with scripts via IDE editors.

Both versions use the same functions and provide the same outputs. The instructions for the different version differ however. Users can follow the version's directory above to find their respective instructions.

It is recommended that users follow at least one of these guides before continuing reading the present guide. Below are instructions on how the approve or reject requests using the tool. 

## Understanding Script Outputs (CSV) 📜🐤

Running the CSV creation function (see Script Version links above for instructions on how to get/create the sheet) outputs a CSV file that holds the following information about the requestee (an example [output file](https://github.com/letendrt/Chronological-File-Request-Pull/blob/main/Mock%20Data%20Access%20Request%20-%20Excel.xlsx) imported into excel can be found above in this repository):
1) Request Date
2) Email
3) Identifier (used to grant/reject access via API)
4) First Name
5) Last Name
6) Affiliation (hosting institution)
7) Position
8) Persistent User ID
9) Authentificator
10) Requested File ID (put between square brackets and separated by commas if more than one)
11) Requested File Names (put between square brackets and separated by commas if more than one)

The CSV file also holds the 'Granted Access?' column - all values in the column are, by default, set to 'Pending'. This is the only column that script runners need to edit prior to granting/rejecting access (see third screenshot below).

  <kbd><img width="928" height="108" alt="image" src="https://github.com/user-attachments/assets/2f1b5f26-f24d-456b-b021-2d14090ff96c" /></kbd><br>
    
  <kbd><img width="940" height="107" alt="image" src="https://github.com/user-attachments/assets/eef7d512-5a7b-4eb7-9757-ca359902ad46" /></kbd><br>
    
  <kbd><img width="798" height="108" alt="image" src="https://github.com/user-attachments/assets/17584fcc-e2c8-4f63-aaae-13b7ce9bcdc9" /></kbd>

## Granting and Rejecting Access Requests --> 💚🐛 vs ⛔🐦
After the sheet creation process (refer to respective script guides) and after carefully reviewing access requests, script runners will have the choice to grant or reject the request. To do so, simply substitute the 'Pending' value from the 'Granted Access?' column with either 'Granted' or 'Rejected'. Deviations from 'Granted' and 'Rejected' will casue the entry to not be picked up by the python script (in other words, the access granting/rejecting will not go through). Users whose requests have yet to be considered can be left on 'Pending' (no action will be taken for these rows). 

In the example below, the first entry is left on 'Pending' (not picked up by script), the second and third are set to 'Rejected' (users will be denied access to the requested datafiles), and the last one is set to 'Granted' (user will be granted access exclusively to the requested datafiles within the dataset). 

Example:<br>
<kbd><img width="363" height="140" alt="image" src="https://github.com/user-attachments/assets/a0bcc635-d978-469f-9b6c-60e5977834aa" /></kbd>

Once column values have been updated to reflect the desired changes in Borealis, can submit the CSV file to the python script. The steps to do so differ depending on the script version being used (script VS user interface). As such, please refer to their respective instructions to familiarise yourself with the submission process. 

## Program Quirks 💫➿🙃
The python script used to create the formatted CSV sheet is, by and large, an API wrapper that includes dataframe manipulation and harmonisation via the pandas library. As it currently stands, there is no singular API that pulls both the access requests and the time at which these requests were submitted. In order to allow users to chronologically order access requests, a secondary API was used to pull user notification of type 'REQUESTFILEACCESS', which includes notification time (an analog for request submission time). As such, I used user notifications to attach the time at which the submission was requested. 

Therein lies the issue: if the user, for some reason, deleted their notifications, the script cannot extract access request times - ultimately resulting in errors (note, however, that 'read' notifications are still picked up by the API and do not cause any issue). This is the most reliable solution that I have found. I welcome community feedback on this.

The script also exclusively works for active requests pending approval/rejection. This means that approved users are removed from the CSV sheet whenever the script is re-run on a same DOI. This is not an issue per se, though it can make the task of tracking who has access to each datafile a tad more challenging. This is only really an 'issue' for revoking access. This is why I also strongly advise users to keep track of users with granted access in a secondary sheet (I am in the future to append approved users in a a perennial secondary sheet). 



