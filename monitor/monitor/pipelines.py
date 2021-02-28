# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .selenium_middlewares import click_cart
import requests
from setting import get_access_token

url = "https://notify-api.line.me/api/notify"
access_token = get_access_token()
request_headers = {'Authorization':'Bearer ' + access_token}

class LineNotify:
    
    def send_messages(self,item):
        '''メッセージ送信
        Lineにメッセージを送信する
        
        Args:
            item(dict):スクレイピング取得アイテム
                item(str)
                is_stock(bool)
                price(int)
                url(str)

        Returns:
            None
        '''

        message = 'カートに追加しました!\n' + '商品名:' + item['item'] + '\n価格:' + str(item['price']) + '円\n' + item['url']
        payload = {'message':message}
        r = requests.post(url,headers=request_headers,params=payload,)


class MonitorPipeline:
    def process_item(self, item, spider):
        return item

class MonitorDosparaPipeline:
    def process_item(self, item, spider):
        
        notify = LineNotify()
        if item['is_stock']:
            click_cart()
            notify.send_messages(item)
        return item
