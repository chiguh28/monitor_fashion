from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from scrapy.http import HtmlResponse

option = Options()
usr_dir ='C:\\Users\\chigu\\AppData\\Local\\Google\\Chrome\\User Data'
option.add_argument('--user-data-dir=' + usr_dir)
driver = webdriver.Chrome(options=option)


class SeleniumMiddleware(object):

    def process_request(self, request, spider):

        return HtmlResponse(request.url,
            body = self.get_html(request.url),
            encoding = 'utf-8',
            request = request)


    def get_html(self,url):
        '''
        @概要
            htmlソースを取得する
            htmlを取得するためにはseleniumで広告(?)を閉じる必要がある
        @param
            url:htmlを取得するurl
        @returns
            html:商品URLのhtmlソース
        '''
        driver.get(url)

        time.sleep(3)

        elements = driver.find_elements_by_class_name('frZCJ')
        
        # URLを開いた際のポップアップ画面を閉じる
        # elementsにすることで要素が無かった場合のエラーを回避する
        if len(elements) > 0:
            elements[0].click()
        
        html = driver.page_source

        return html

def close_driver():
    driver.close()