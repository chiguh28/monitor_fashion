# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .selenium_middlewares import click_cart
import requests
from setting import get_access_token
import datetime
import os
import sqlite3

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


class MonitorDBPipeline(object):
    _db = None

    @classmethod
    def get_database(cls):
        cls._db = sqlite3.connect(
            os.path.join(os.getcwd(), 'ec_site.db'))

        # テーブル作成
        cursor = cls._db.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS post(\
                id INTEGER PRIMARY KEY AUTOINCREMENT, \
                item TEXT NOT NULL, \
                price INTEGER NOT NULL,\
                is_stock INTEGER NOT NULL,\
                url TEXT UNIQUE NOT NULL, \
            );')

        return cls._db

    def process_item(self, item, spider):
        """
        Pipeline にデータが渡される時に実行される
        item に spider から渡された item がセットされる
        """
        self.save_post(item)
        return item

    def save_post(self, item):
        """
        item を DB に保存する
        
        備考:
            同一URLが存在する場合は値が更新されているか確認し、
            更新されていればUpdateする
        """
        if self.find_post(item['url']):
            # 既に同じURLのデータが存在する場合はスキップ
            return

        # sqlite3はBooleanがないため1,0で判別
        if item['is_stock']:
            is_stock = int(1)
        else:
            is_stock = int(0)

        db = self.get_database()
        db.execute(
            'INSERT INTO post (item,price,is_stock,url) VALUES (?, ?, ?)', (
                item['item'],
                item['price'],
                is_stock,
                item['url']
            )
        )
        db.commit()

    def find_post(self, url):
        db = self.get_database()
        cursor = db.execute(
            'SELECT * FROM post WHERE url=?',
            (url,)
        )
        return cursor.fetchone()

    def check_chg_post(self,item):
        '''
        DBと変化しているかを確認
        
        同一URLが存在した場合にのみ駆動させる
        '''
        db = self.get_database()
        cursor = db.execute(
            'SELECT price,is_stock FROM post WHERE url=?',
            (item['url'],)
        )

        # cursor(price,is_stock)
        old_price = cursor[0]
        old_is_stock = cursor[1]

        # DB値と変化確認
        if old_price > item['price']:
            # LINE通知(値引き)
            # レコード更新
        elif old_price < item['price']:
            # LINE通知(値上げ)
            # レコード更新
        
        if old_is_stock > item['is_stock']:
            # LINE通知(在庫消失通知)
            # True → False のため在庫が無くなる
            # レコード更新

        elif old_is_stock < item['is_stock']:
            # LINE通知(在庫復活通知)
            # False → True のため在庫が復活
            # レコード更新
