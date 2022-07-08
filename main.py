import os
import csv
import time
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def _html_to_soup(html):
    options=webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver=webdriver.Chrome(executable_path="chromedriver", options=options)
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

def _surname(folders, item_names, sleep_sec):
    resources=folders[0]
    results=folders[1]

    file_stem=item_names[0]
    file_path=f"{resources}/{file_stem}.csv"
    df=pd.read_csv(file_path, dtype=str)

    cols=["ancestry", "ancestry_link", "forebears", "forebears_link"]
    for i, col in enumerate(cols):
        if col not in df.columns:
            df[col]=pd.NA 

    n_obs=len(df.index)

    _functions=[_ancestry, _forebears]
    for i, _function in enumerate(_functions):
        col=_function.__name__.replace("_", "")

        old_vals=df[col].tolist()

        new_vals=[None]*n_obs
        new_links=[None]*n_obs

        for j, old_val in enumerate(old_vals):
            if not pd.isna(old_val):
                new_vals[j]=old_val
            elif pd.isna(old_val):
                surname=df.loc[j, "surname"]
                new_val, new_link=_function(surname)
                new_vals[j]=new_val
                new_links[j]=new_link

        df[col]=new_vals
        df[f"{col}_link"]=new_links

    file_path=f"{results}/{file_stem}.csv"
    df=df.set_index("surname")
    df.to_csv(file_path)

#UPDATE CHROMEDRIVER (use brave???)
#chrome://version
#https://chromedriver.chromium.org/downloads

#RETRIEVE SURNAME NATION
folders=["_surname0", "_surname1"]
item_names=["surname"]
sleep_sec=1
_surname(folders, item_names, sleep_sec)

print("done")


