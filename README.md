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

Running the CSV creation function (see Script Version links above for instructions on how to get the sheet) outputs a CSV file that holds the following information about the requestee (an example output file loaded into excel can be found in this repository):
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

The CSV file also holds the 'Granted Access?' column - all values in the column are set to 'Pending'. This is the only column that script runners need to edit prior to granting/rejecting access.


