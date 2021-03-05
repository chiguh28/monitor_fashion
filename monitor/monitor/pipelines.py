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

DOWN = 0
UP = 1
IS_STOCK = 2
NO_STOCK = 3
CART = 4

class LineNotify:

    def create_message(self,item,flag):
        '''メッセージ作成
        LINE送信用メッセージを作成

        Args:
            item(dict):スクレイピング取得アイテム
                item(str)
                is_stock(bool)
                price(int)
                url(str)
            flag
                DOWN:価格値下げ
                UP:価格値上げ
                IS_STOCK:在庫復活
                NO_STOCK:在庫消失
                CART:カート追加
        Returns:
            message:メッセージ
        '''

        last_message = '商品名:' + item['item'] + '\n価格:' + str(item['price']) + '円\n' + item['url']

        if flag == DOWN:
            message = '価格が値下げしました!\n'
        elif flag == UP:
            message = '価格が値上げしました!\n'
        elif flag == IS_STOCK:
            message = '在庫が復活しました!\n'
        elif flag == NO_STOCK:
            message = '在庫が消失しました!\n'
        elif message == CART:
            message = 'カートに追加しました!\n'
        
        message = message + last_message

        self.send_messages(message)

    
    def send_messages(self,message):
        '''メッセージ送信
        Lineにメッセージを送信する
        
        Args:
            message:送信するメッセージ

        Returns:
            None
        '''

        payload = {'message':message}
        r = requests.post(url,headers=request_headers,params=payload,)
    
    def send_messages_cart(self,item):
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
            notify.send_messages_cart(item)
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
                url TEXT UNIQUE NOT NULL\
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
            # 既に同じURLのデータが存在する場合はDBと変化しているか確認
            self.check_chg_post(item)
            return

        # sqlite3はBooleanがないため1,0で判別
        is_stock = self.convert_is_stock(item['is_stock'])

        db = self.get_database()
        db.execute(
            'INSERT INTO post (item,price,is_stock,url) VALUES (?, ?, ?,?)', (
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
            'SELECT id,price,is_stock FROM post WHERE url=?',
            (item['url'],)
        )

        notify = LineNotify()
        data = cursor.fetchone()
        id = data[0]
        old_price = data[1]
        old_is_stock = data[2]

        is_stock = self.convert_is_stock(item['is_stock'])

        # DB値と変化確認
        if old_price > item['price']:
            # LINE通知(値引き)
            notify.create_message(item,DOWN)
            # レコード更新
            self.update_post_price(id,item['price'])
        elif old_price < item['price']:
            # LINE通知(値上げ)
            notify.create_message(item,UP)
            # レコード更新
            self.update_post_price(id,item['price'])
        
        if old_is_stock > is_stock:
            # LINE通知(在庫消失通知)
            notify.create_message(NO_STOCK)
            # True → False のため在庫が無くなる
            # レコード更新
            self.update_post_is_stock(id,is_stock)

        elif old_is_stock < is_stock:
            # LINE通知(在庫復活通知)
            notify.create_message(IS_STOCK)
            # False → True のため在庫が復活
            # レコード更新
            self.update_post_is_stock(id,is_stock)


    def update_post_price(self,id,price):
        '''
        priceレコードを更新

        Parameters:
            id:レコード特定に使用
            price:更新値
        '''

        db = self.get_database()
        db.execute(
            'UPDATE post SET price=? WHERE id=?',
            (price,id,)
        )

    def update_post_is_stock(self,id,is_stock):
        '''
        is_stockレコードを更新

        Parameters:
            id:レコード特定に使用
            is_stock:更新値
        '''

        db = self.get_database()
        db.execute(
            'UPDATE post SET is_stock=? WHERE id=?',
            (is_stock,id,)
        )

    def convert_is_stock(self,is_stock_bool):
        # sqlite3はBooleanがないため1,0で判別
        if is_stock_bool:
            is_stock = int(1)
        else:
            is_stock = int(0)

        return is_stock
