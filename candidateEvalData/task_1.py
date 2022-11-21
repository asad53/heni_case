#import modules
from lxml import html
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

#get html and tree
html_page_link = 'candidateEvalData/webpage.html'

with open(html_page_link, 'r') as f:
    contents = f.read()
response = requests.get(html_page_link)
soup = BeautifulSoup(response.text, features="html.parser")

# parse artist name
artist_names = [name.text for name in soup.findAll('h1', class_='lotName')]
print(artist_names)
#parse painting name

#parse price GBP

#parse price US

#parse price GBP est

#parse price US est

#image link