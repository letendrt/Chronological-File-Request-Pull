# Script Version -- Guide 🎣🐈‍⬛

1) Start by downloading the [Chrono_Pull_Script_Version.py ](https://github.com/letendrt/Chronological-File-Request-Pull/blob/main/Script%20Version/Chrono%20Pull%20Script%20Version.py) attached in this repository folder.
2) Open the file in an IDE of your choice. Note that given Borealis restrictions, the IDE must be held locally on the user's device (no web-based IDEs like Google Colab and web-based Jupyter Notebook - API calls will not work).
3) Users will have to edit a few parameters to tune the tool to their needs. Navigate to the <b>PARAMETERS</b> section of the script (~line 16).

    <kbd><img width="810" height="106" alt="image" src="https://github.com/user-attachments/assets/d39af5d1-9d71-4b01-97d0-19bca0c401cf" /></kbd>
    
4) You will then need to fetch your dataset DOI as well as your API key. Simply paste them in their respective fields in the script. The DOI can be in https:// fromat (URL) or in standard doi: format. The DOI will be automatically formatted by the script in a later function. Your API token can easily be fetched in your Borealis user drop down menu. 

    <kbd><img width="765" height="146" alt="image" src="https://github.com/user-attachments/assets/fa3add66-f0ac-4142-8af6-784908a05b43" /></kbd>

5) Next, you will need to select which task you want the script to run. Only one of the tasks can be run at the time (this is for purely pragmatic reasons). There are 2 tasks that can be initiated with this script:

   1) Pull restricted file access requests (pulls all datafile requests for a given dataset, as well as the date at which the request was submitted - formats the whole in a curated CSV file). Or;
   2) Process requests after script user has classified them as "Granted" or "Rejected" in the output CSV file (from the above task). For instructions on how to format grant or reject access via the CSV file, consult the [main repository page](https://github.com/letendrt/Chronological-File-Request-Pull/tree/main) instructions (under README).

    Selecting which task to run is easy. 
