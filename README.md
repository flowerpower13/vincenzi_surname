# Retrieve surname's nation of origin 

The routine accesses ancestry.com and forebears.io to extract relevant information.


## Instructions

1. Update ChromeDriver
INSTALL BRAVE
https://brave.com/download/

LOCATE BRAVE APP
right click on Brave app, "Properties", "Open File Location"
/e.g., C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe)
set location in variable "location" (already done below)

CHECK BRAVE'S CHROME VERSION
open Brave, go to Address Bar, type "brave://version"
search "Chrome/", see code (e.g., Chrome/103.0.5060.114)
 
DOWNLOAD PROPER CHROMEDRIVER
https://chromedriver.chromium.org/downloads
choose version close to current (e.g., 103)

2. Load Data
Create a file named `_surname.csv`, with column `_surname` filled with surnames to retrieve. 
Make sure to put file in the folder `_surname0`.

3. Run `main.py` by specifying the OS as an additional argument. 
Available options are `windows` for Windows OS and `mac` for macOS. 

4. Collect results in the folder `_surname1`.

5. (Optional) Re-run Code: copypaste `_surname.csv` in `_surname0` and run the code again (to update missing values).
