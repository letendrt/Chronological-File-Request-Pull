# User Interface Version -- Guide 🌱🐇

1) Start by downloading the [Chrono_Pull_GUI_Version.py](https://github.com/letendrt/Chronological-File-Request-Pull/blob/main/User%20Interface%20Version/Chrono_Pull_GUI_Version.py) attached in this repository folder.
2) Open the file in an IDE of your choice. Note that given Borealis restrictions, the IDE must be held locally on the user's device (no web-based IDEs like Google Colab and web-based Jupyter Notebook - API calls will not work).
3) Run the Script. There, users w3ill be met by the tool window:

  <kbd><img width="1021" height="749" alt="image" src="https://github.com/user-attachments/assets/5122328d-4769-4a00-8c77-ed90a5536fc8" /></kbd>


5) Next, you will need to think about which task you want the script to run. Only one of the tasks can be run at the time (this is for purely pragmatic reasons). There are 2 tasks that can be initiated from the user interface:

   1) Pull restricted file access requests (pulls all datafile requests for a given dataset, as well as the date at which the request was submitted - formats the whole in a curated CSV file). Or;
   2) Process requests after script user has classified them as "Granted" or "Rejected" in the output CSV file (from the above task). For instructions on how to format grant or reject access via the CSV file, consult the [main repository page](https://github.com/letendrt/Chronological-File-Request-Pull/tree/main) instructions (under README).

