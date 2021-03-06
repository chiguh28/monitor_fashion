import scrapy
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pandas
from ..selenium_middlewares import close_driver
from monitor.items import MonitorItem
from setting import get_url_list




class NordstormSpider(scrapy.Spider):
    name = 'nordstorm'
    allowed_domains = ['www.nordstrom.com']
    
    

    def start_requests(self):
        '''
        @概要
            spider開始時のみ読み込まれる

        @param
            self
        
        @yield
            scrapy.Request(url=url,callback=self.parse)
            scrapyのParseメソッドをコールバックする

        @備考
            商品URLのリストをforで回し、yieldして解析するようにする
        '''
        file_path = get_url_list()
        df = pandas.read_csv(file_path)

        urls = df['商品URL'].values

        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse)    
        


    def parse(self, response):
        
        def get_item(soup):
            '''
            商品名取得

            @param
                soup:Beautifulで解析した結果
            @returns
                item:商品名
            '''
            item_box = soup.find('h1',class_='_6YOLH _1JtW7 _2VF_A _2OMMP')

            if item_box is not None:
                item = item_box.text
            else:
                item = 'None'

            return item

        def judge_stock(soup):
            '''
            在庫判定

            @param
                soup:Beautifulで解析した結果
            @returns
                is_stock:在庫結果
            '''
            is_stock = soup.find('div',class_='iv2E3') is not None

            return is_stock
        def get_price(soup):
            '''
            価格取得

            @param
                soup:Beautifulで解析した結果
            @returns
                price:価格(int)
            '''
            price_box = soup.find('span',id='current-price-string')

            if price_box is not None:
                price = int(price_box.text)
            else:
                price = 999999999999

            return price

        soup = BeautifulSoup(response.body,"html.parser")
        
        yield MonitorItem(
            item = get_item(soup),
            is_stock = judge_stock(soup),
            price = get_price(soup),
            url = response.url
        )
        

             
    def close(self,reason):
        close_driver()


