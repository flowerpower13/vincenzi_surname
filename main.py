import time
import unicodedata
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver

#SET SPECIFICATION
os_specification="windows"
#os_specification="mac"

#PRELIMINARY
"""
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
"""

# this allows to pass an argument to select the OS
# it is still a dirty workaround which gives us what we want
if os_specification=="windows":
    location="C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
elif os_specification=="mac":
    location="/Applications/Brave Browser.app"

#SELENIUM
#set driver options
options=webdriver.ChromeOptions()
options.binary_location=(location)

#add arguments
args=[
    "--incognito", 
    "--headless", 
    "--disable-notifications",
    "--log-level=3"
    ]
for i, arg in enumerate(args):
    options.add_argument(arg)
    
#start driver
driver=webdriver.Chrome(executable_path="chromedriver", options=options)

#from html to soup
def _html_to_soup(html):
    driver.get(html)
    text=driver.page_source
    soup=BeautifulSoup(text, 'html.parser')
    return soup

#https://www.ancestry.com/name-origin?surname=fiore
def _ancestry(surname):
    base="https://www.ancestry.com/name-origin?surname="

    html=f"{base}{surname}"
    soup=_html_to_soup(html)
    nation=pd.NA

    desc=soup.find_all("div", {"class": "description"})
    
    if len(desc)>0:
        full_desc = desc[0].text

        if "American Family Names" in full_desc:
            double_dots=full_desc.find(":")

            if double_dots>=0:
                nation=full_desc[0:double_dots].replace(":","").strip()

    return nation, html
      
#https://forebears.io/surnames/fiore
def _forebears(surname):
    base="https://forebears.io/surnames/"

    html=f"{base}{surname}"
    soup=_html_to_soup(html)
    nation=pd.NA
    
    desc = soup.find_all("div", {"class": "statistic-single"})

    if len(desc)>1:
        nation_tag = desc[0].find_all("div", {"class": "detail"})

        if len(nation_tag)>0:
            nation=nation_tag[0].text

    return nation, html

def _ascii(row):
    row=unicodedata.normalize('NFKD', row).encode('ASCII', 'ignore').decode()
    return row

def _first_name(row):
    char="."
    if char in row:
        row=row.split(".")
        row=row[1]
    return row

def _clean_col(col):
    #uppercase
    col=col.str.lower()

    #encoding
    _function=_ascii
    col=col.apply(_function)

    #remove first names
    _function=_first_name
    col=col.apply(_function)

    #remove text within parentheses
    pat=r"\(.*?\)"
    col=col.str.replace(pat, "", regex=True)

    #remove text within slashes \
    pat=r"\\.*?\\"
    col=col.str.replace(pat, "", regex=True)

    #remove text within slashes /
    pat=r"\/.*?\/"
    col=col.str.replace(pat, "", regex=True)

    #remove text within quote marks "
    pat=r'\".*?\"'
    col=col.str.replace(pat, "", regex=True)

    #remove text within quote marks "
    pat=r'\"".*?\""'
    col=col.str.replace(pat, "", regex=True)

    #remove punctuation
    pat=r"[^\w\s]"
    col=col.str.replace(pat, "", regex=True)

    #remove whitespaces
    col=col.str.strip()
    pat=r"\s+"
    col=col.str.replace(pat, " ", regex=True)

    return col

def _clean_df(df, label):
    col=df[label]
    df[label]=_clean_col(col)
    col=df[label]
    df[label]=_clean_col(col)

    df=df.drop_duplicates(subset=[label])
    df=df.dropna(subset=[label])
    df=df.sort_values(by=[label])
    df=df[df[label]!=""]

    return df

def _create_df(file_stem, surname, _functions):
    df=pd.DataFrame()
    df[file_stem]=[surname]

    for i, _function in enumerate(_functions):
        col=_function.__name__.replace("_", "")
        col_link=f"{col}_link"

        try:
            new_val, new_link=_function(surname)

        except Exception as e:
            new_val, new_link= pd.NA, pd.NA

            print(e)

        df[col]=[new_val]
        df[col_link]=[new_link]

    return df

#retrieve surname origin
def _surname(folders, item_names, time_sleep, _functions):
    resources=folders[0]
    results=folders[1]

    file_stem=item_names[0]
    file_path=f"{resources}/{file_stem}.csv"
    df=pd.read_csv(file_path, dtype=str)

    n_obs=len(df.index)
    tot=n_obs-1

    label=file_stem
    df=_clean_df(df, label)

    surnames=df[file_stem].tolist()

    frames=[None]*n_obs
    converteds=[None]*n_obs

    for i, surname in enumerate(surnames):
        output=Path(f"{results}/{surname}.csv")

        if output.is_file():
            df=pd.read_csv(output, dtype="string")
            df=df.set_index(file_stem)
            converted=True
            print(f"{i}/{tot} - {surname} - already done")

        elif not output.is_file():

            try:
                df=_create_df(file_stem, surname, _functions)
                df=df.set_index(file_stem)
                df.to_csv(output)
                converted=True

                print(f"{i}/{tot} - {surname} - done")

            except Exception as e:
                df=pd.DataFrame()
                converted=False

                print(f"{i}/{tot} - {surname} - exception")
                print(e)
            
            time.sleep(time_sleep)

        frames[i]=df
        converteds[i]=converted

    df=pd.concat(frames)
    df=df.reindex(index=surnames)
    df.insert(0, "converted", converteds)  

    file_path=f"{results}/{file_stem}.csv"
    df.to_csv(file_path)

def _concat(folders, item_names):
    resources=folders[0]
    results=folders[1]

    file_stem=item_names[0]

    p=Path(resources).glob('**/*')
    files=[x for x in p if x.is_file()]
    files=[x.stem for x in files]
    files=[x for x in files if not x==file_stem]

    n_obs=len(files)
    tot=n_obs-1

    frames=[None]*n_obs
    converteds=[None]*n_obs

    for i, file in enumerate(files):
        output=Path(f"{resources}/{file}.csv")

        df=pd.read_csv(output, dtype="string")
        df=df.set_index(file_stem)
        converted=True
        
        print(f"{i}/{tot} - {file} - done")
            
        frames[i]=df
        converteds[i]=converted

    df=pd.concat(frames)
    df=df.reindex(index=files)
    df.insert(0, "converted", converteds)  

    file_path=f"{results}/{file_stem}.csv"
    df.to_csv(file_path)


#RETRIEVE SURNAME ORIGIN
folders=["_surname0", "_surname1"]
item_names=["_surname"]
time_sleep=0
_functions=[_ancestry, _forebears]
#_surname(folders, item_names, time_sleep, _functions)

#CONCAT EXISTING RESULTS
folders=["_surname1", "_concat"]
item_names=["_surname"]
_concat(folders, item_names)

print("done")


