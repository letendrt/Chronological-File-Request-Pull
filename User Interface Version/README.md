# User Interface Version -- Guide 🌱🐇

1) Start by downloading the [Chrono_Pull_GUI_Version.py](https://github.com/letendrt/Chronological-File-Request-Pull/blob/main/User%20Interface%20Version/Chrono_Pull_GUI_Version.py) attached in this repository folder.
2) Open the file in an IDE of your choice. Note that given Borealis restrictions, the IDE must be held locally on the user's device (no web-based IDEs like Google Colab and web-based Jupyter Notebook - API calls will not work).
3) Run the Script. There, users w3ill be met by the tool window:

  <kbd><img width="1021" height="749" alt="image" src="https://github.com/user-attachments/assets/5122328d-4769-4a00-8c77-ed90a5536fc8" /></kbd>

4) Enter your API key and the dataset DOI in fields 1 and 2 respectively. 

5) Next, you will need to think about which task you want the script to run. Only one of the tasks can be run at the time (this is for purely pragmatic reasons). There are 2 tasks that can be initiated from the user interface - both necessitate an API key and the dataset DOI:

   1) Pull restricted file access requests (pulls all datafile requests for a given dataset, as well as the date at which the request was submitted - formats the whole in a curated CSV file). Or;
   2) Process requests after script user has classified them as "Granted" or "Rejected" in the output CSV file (from the above task). For instructions on how to format grant or reject access via the CSV file, consult the [main repository page](https://github.com/letendrt/Chronological-File-Request-Pull/tree/main) instructions (under README).

    If running the populated request pull CSV file, leave the Granting/Rejecting Access checkbox unchecked as depicted below:
   
   <kbd><img width="946" height="146" alt="image" src="https://github.com/user-attachments/assets/03e75045-fd26-4cb9-b313-ad8f9f84153b" /></kbd>

   If Granting/Rejecting Access, check the box. This will prompt a new field on the window. Make sure to select the populated CSV file to process access requests (as explained above in point ii).

    <kbd><img width="710" height="233" alt="image" src="https://github.com/user-attachments/assets/e59e7345-c1e6-4ad4-89b5-07cdecc57dc3" /></kbd>

6) Press the RUN SCRIPT button to start the process (same button regardless of performed task - which task is run depends on whether the Granting/Rejecting Access checkbox is checked). Pressing the button will close the window and start the requested task. Task processing will and output directory for the CSV sheet will be visible in the python shell. 

## Optional Step

Users can select in which borealis environment they want to run the script (Demo or Production environment) by checking the box in the bottom left corner of the window. By default, the script is set to run in production. Demo is really just for testing and tool development. 

<kbd><img width="1016" height="744" alt="edited screenshot" src="https://github.com/user-attachments/assets/0f16e5bc-16b2-4255-bbab-e97f5bdbd6c5" /></kbd>
