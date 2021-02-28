import scrapy
from bs4 import BeautifulSoup
from monitor.items import MonitorItem
import pandas
from ..selenium_middlewares import close_driver
from setting import get_url_list


class DosparaSpider(scrapy.Spider):
    name = 'dospara'
    allowed_domains = ['www.dospara.co.jp']


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

        urls = df.values

        for url in urls:
            yield scrapy.Request(url=url[0],callback=self.parse)    

    def parse(self, response):
        
        def get_item(soup):
            '''
            商品名取得

            @param
                soup:Beautifulで解析した結果
            @returns
                item:商品名
            '''
            item_box = soup.find('p',class_='productName')

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
            is_stock = soup.find('input',{'id':'cartButtonImage'}) is not None

            return is_stock
        def get_price(soup):
            '''
            価格取得

            @param
                soup:Beautifulで解析した結果
            @returns
                price:価格(int)
            '''
            price_box = soup.find('span',itemprop='price')

            if price_box is not None:
                price = int(price_box.text.replace(',',''))
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


