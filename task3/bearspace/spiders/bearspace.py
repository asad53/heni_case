# -*- coding: utf-8 -*-
import logging
import pdb
import regex as re
import traceback
import scrapy.spiders
from scrapy.loader import ItemLoader
import json

logger = logging.getLogger(__name__)

class PlayboardSpider(scrapy.Spider):
    name = "bearspace"
    lmt_enabled = False
    proxymesh_enabled = False

    custom_settings = {
        'DOWNLOAD_DELAY': 0.02,
        'RETRY_HTTP_CODES' : [418, 50, 500, 512,429],
        'RETRY_TIMES': 100,
        'HTTPERROR_ALLOWED_CODES': []
    }

    def __init__(self):

        logger = logging.getLogger('scrapy.spidermiddlewares.httperror')
        logger.setLevel(logging.WARNING)

        #PASTE CODE HERE PLEASE

        self.lpv_url = 'https://www.bearspace.co.uk/purchase?page={page}'
        # self.regex_pattern_1 = '\d+\,?.?\d*\s*\c?m?s?\s*x+\s*\d*\,?.?\d*\s*\c?m?s?'
        self.regex_pattern_1 = '\d+\,?.?\d*\s*\c?m?s?w?\s*x+\s*\w?i?d?t?h?\s*\d*\,?.?\d*\s*\c?m?s?'
        self.regex_pattern_2 = '\d+\,?.?\d*\s*\c?m?\s*diam'
        #self.regex_pattern = '\d+\,?.?\d*\s*x?×?b?y?\s*\d*'
        self.lpv_headers = {
            'authority': 'www.bearspace.co.uk',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'Cookie': 'XSRF-TOKEN=1667247137|YflXgbARi8PV'
        }

    def dimension_finder(self, raw, u_rl):
        # print("RAW DATA: ",raw)
        # print("URL: ",u_rl)
        if raw != None:
            all_chars = re.findall(self.regex_pattern_1, raw.lower())
            all_chars = re.findall(self.regex_pattern_2, raw.lower()) if len(all_chars) == 0 else all_chars
            # print("ALL CHARS: ",all_chars)
            val = None
            for ac in all_chars:
                val = ac if 'cm' in ac else val
                prev = ac
                val = prev if val == None else val
            if val != None:
                if 'diam' in raw:
                    height = re.findall("\d*",val.strip())[0]
                    width = re.findall("\d*",val.strip())[0]
                else:
                    val = val.replace("cm", "").replace("in", "").replace(",", ".").replace("width","").replace("s","").replace("w","").replace("h","").strip()
                    try:
                        height = float(val.split("x")[0].strip()) if 'x' in val else (
                            float(val.split("×")[0].strip()) if '×' in val else (
                                float(val.split("by")[0].strip()) * 2.54 if 'by' in val else
                                re.findall("\d*", val.strip())[0]))
                    except Exception:
                        height = None
                        pass
                    try:
                        width = float(val.split("x")[1].strip()) if 'x' in val else (
                            float(val.split("×")[1].strip()) if '×' in val else (
                                float(val.split("by")[1].strip()) * 2.54 if 'by' in val else
                                re.findall("\d*", val.strip())[1]))
                    except Exception:
                        width = None
                        pass
                return height, width
            else:
                return None, None
        else:
            return None, None

    def start_requests(self):
        yield scrapy.Request(self.lpv_url.format(page=20), method="GET", headers=self.lpv_headers,
                             meta={'pageno': 20}, callback=self.lpv_parse, dont_filter=True)

    def lpv_parse(self, response):
        if response.status in self.settings.get('RETRY_HTTP_CODES'):
            yield scrapy.Request(response.url, method="GET", headers=self.lpv_headers,
                                 meta=response.meta, callback=self.lpv_parse, dont_filter=True)
            return
        if response.body:
            try:
                products = response.xpath('//a[@data-hook="product-item-container"]')
                for product in products:
                    listing = {
                        'url': product.xpath('@href').get()
                    }
                    yield scrapy.Request(product.xpath('@href').get(), method="GET", headers=self.lpv_headers,
                                         meta={'listing': listing}, dont_filter=True,
                                         callback=self.dpv_parse)
            except Exception as e:
                logger.error(
                    f'{e} on crawling: {response.url} \n  LPV content: \n {traceback.format_exc()} \n--------\n')
                self.crawler.stats.inc_value('num_exceptions')
        else:
            print("EMPTYyyyyyyy RESPONSE")
            print(response.body)

    def dpv_parse(self, response):
        if response.status in self.settings.get('RETRY_HTTP_CODES'):
            yield scrapy.Request(response.url, method="GET", headers=self.lpv_headers,
                                 meta=response.meta, callback=self.dpv_parse, dont_filter=True)
            return
        if response.body:
            try:
                listing = response.meta.get('listing')
                height = None
                width = None
                media = None
                descriptions = response.xpath('//pre[@data-hook="description"]/p')
                if len(descriptions) > 0:
                    for de in range(len(descriptions)):
                        inner_text = descriptions[de].xpath('text()').get()
                        inner_text = descriptions[de].xpath(
                            './/span/text()').get() if inner_text == None else inner_text
                        height, width = self.dimension_finder(inner_text, response.url)
                        if height != None or width != None:
                            media_lst = []
                            for i in range(0, de):
                                media_m = descriptions[i].xpath('text()').get()
                                media_m = descriptions[i].xpath('.//span/text()').get() if media_m == None else media_m
                                media_lst.append(media_m)
                            media = ', '.join(media_lst)
                            media = (descriptions[de + 1].xpath('.//span/text()').get() if descriptions[de + 1].xpath('text()').get() == None else descriptions[de + 1].xpath('text()').get()) if media == '' else media
                            break
                else:
                    descriptions = response.xpath('//pre[@data-hook="description"]/text()').extract()
                    if len(descriptions) > 0:
                        for de in range(len(descriptions)):
                            inner_text = descriptions[de]
                            height, width = self.dimension_finder(inner_text, response.url)
                            if height != None or width != None:
                                media_lst = []
                                for i in range(0, de):
                                    media_m = descriptions[i]
                                    media_lst.append(media_m)
                                media = ', '.join(media_lst)
                                try:
                                    media = descriptions[de + 1] if media == '' else media
                                except Exception:
                                    pass
                                break
                    else:
                        descriptions = response.xpath('//pre[@data-hook="description"]/div/div/p')
                        if len(descriptions) > 0:
                            for de in range(len(descriptions)):
                                inner_text = descriptions[de].xpath('text()').get()
                                inner_text = descriptions[de].xpath(
                                    './/span/text()').get() if inner_text == None else inner_text
                                height, width = self.dimension_finder(inner_text, response.url)
                                if height != None or width != None:
                                    media_lst = []
                                    for i in range(0, de):
                                        media_m = descriptions[i].xpath('text()').get()
                                        media_m = descriptions[i].xpath(
                                            './/span/text()').get() if media_m == None else media_m
                                        media_lst.append(media_m)
                                    media = ', '.join(media_lst)
                                    media = (descriptions[de + 1].xpath('.//span/text()').get() if descriptions[
                                                                                                       de + 1].xpath(
                                        'text()').get() == None else descriptions[de + 1].xpath(
                                        'text()').get()) if media == '' else media
                                    break
                # print("Height: ", height, "Width: ", width,"Media: ",media)
                listing.update({
                    'title': response.xpath('//h1[@data-hook="product-title"]/text()').get().strip(),
                    'price': float(response.xpath('//span[@data-hook="formatted-primary-price"]/text()').get().strip().replace("£","").replace(",","")),
                    'height': height,
                    'width': width,
                    'media': media
                })
                yield listing
            except Exception as e:
                logger.error(
                    f'{e} on crawling: {response.url} \n  DPV content: \n {traceback.format_exc()} \n--------\n')
                self.crawler.stats.inc_value('num_exceptions')
        else:
            print("EMPTYyyyyyyy RESPONSE")
            print(response.body)