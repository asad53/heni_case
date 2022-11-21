#import modules
from lxml import html
import re
import requests
import pandas as pd
from datetime import datetime

#get html and tree
html_page_link = 'candidateEvalData/webpage.html'

#open the html file
with open(html_page_link, 'r') as f:
    contents = f.read()

#ingest the data using html fromstring
byte_data = contents
source_code = html.fromstring(byte_data)

#declare final dictionary
listing = {}


# parse artist name
#parse using class xpath & cleaning extra brackets from data
artist_name = source_code.xpath('//h1[@class="lotName"]')[0].text_content().split("(")[0].strip()
listing['artist_name'] = artist_name
#parse painting name
#parse using class xpath & stripping to remove trailing & leading spaces
painting_name = source_code.xpath('//h2[@class="itemName"]')[0].text_content().strip()
listing['painting_name'] = painting_name
#parse price GBP
#parse using id xpath & remove extra characters, converting to int
price_real_gbp = int(source_code.xpath('//span[@id="main_center_0_lblPriceRealizedPrimary"]')[0].text_content().
                     replace("GBP","").replace(",","").strip())
listing['price_real_gbp'] = price_real_gbp

#parse price US
#parse using id xpath & remove extra characters, converting to int
price_real_usd = int(source_code.xpath('//div[@id="main_center_0_lblPriceRealizedSecondary"]')[0].text_content().
                     replace("USD","").replace(",","").strip())
listing['price_real_usd'] = price_real_usd

#parse price GBP est
#parse using id xpath & remove extra characters, converting to int, splitting by '-' and storing the result in list - then converting to tuple so it is immutable
price_est_gbp = tuple([int(pc.strip()) for pc in source_code.xpath('//span[@id="main_center_0_lblPriceEstimatedPrimary"]')[0].text_content().
                      replace("GBP","").replace(",","").strip().split("-")])
listing['price_est_gbp'] = price_est_gbp

#parse price US est
#parse using id xpath & remove extra characters, converting to int, splitting by '-' and storing the result in list - then converting to tuple so it is immutable
price_est_usd = tuple([int(pc.strip()) for pc in source_code.xpath('//span[@id="main_center_0_lblPriceEstimatedSecondary"]')[0]
                      .text_content().replace("USD","").replace(",","").replace(")","").replace("(","").strip()
                      .split("-")])
listing['price_est_usd'] = price_est_usd

#image link
#parse using id xpath & getting src attribute value
image_url = source_code.xpath('//img[@id="imgLotImage"]')[0].get('src')
listing['image_url'] = image_url

#sale_date
#parse using id xpath & converting string to date
sale_date = datetime.strptime(source_code.xpath('//span[@id="main_center_0_lblSaleDate"]')[0].text_content().
                              replace(',','').strip(), '%d %B %Y').date()
listing['sale_date'] = sale_date


#showing final dictionary we have been updating
print(listing)