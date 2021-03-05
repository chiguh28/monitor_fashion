from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from scrapy.http import HtmlResponse
from setting import get_usr_dir

option = Options()
usr_dir = get_usr_dir()
option.add_argument('--user-data-dir=' + usr_dir)
option.add_argument('--profile-directory=Profile 2')
driver = webdriver.Chrome(options=option)


def get_html_dospara(url):
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
    
    html = driver.page_source

    return html

def get_html_nordstorm(url):
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


class SeleniumMiddleware(object):

    def process_request(self, request, spider):

        return HtmlResponse(request.url,
            body = get_html_nordstorm(request.url),
            encoding = 'utf-8',
            request = request)


class SeleniumDosparaMiddleware(object):

    def process_request(self, request, spider):

        return HtmlResponse(request.url,
            body = get_html_dospara(request.url),
            encoding = 'utf-8',
            request = request)


def click_cart():
    button_block = driver.find_elements_by_id('cartButtonImage')
    if len(button_block) > 0:
        button_block[0].click()

def close_driver():
    driver.close()
