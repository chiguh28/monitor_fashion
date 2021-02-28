import pandas as pd
import monitor.settings as setting

df = pd.read_csv('setting.csv')

def get_url_list():
    return df['商品リストCSV'].values[0]

def get_usr_dir():
    return df['ブラウザユーザ'].values[0]

def get_access_token():
    return df['LINEトークン'].values[0]