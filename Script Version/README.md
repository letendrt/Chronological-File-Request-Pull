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

    Selecting which task to run is easy. If run_access_processor is set to False, the script will create a CSV sheet template pulling all requests for the dataset. If run_access_processor is set to True, the script will process access requests. Simply comment out the unused one (and uncomment the used one).

    <kbd><img width="766" height="103" alt="image" src="https://github.com/user-attachments/assets/65ff55c1-2f6b-4b4b-a258-0c681e59d7b1" /></kbd>

6) If processing reviewed access requests, users will also need to fetch the CSV file directory and paste it as the value for csv_granter_file variable. Note that if the script is being run on windows, users should keep the 'r' before the directory string.

    <kbd><img width="764" height="62" alt="image" src="https://github.com/user-attachments/assets/b5e2663c-66b8-4dfa-aff3-345ca381dc04" /></kbd>
