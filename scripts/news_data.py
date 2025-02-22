# Load libraries
from bs4 import BeautifulSoup
import requests
import json
import time
from random import randrange

# HTML scrapper
from selenium import webdriver

# Basic text cleaning
import re

# Data wrangling
import pandas as pd
import numpy as np
from os import listdir
from datetime import datetime

# Define folder
data_folder = r'/home/zmaznevegor/PycharmProjects/defi_uncertainty/data'

# Data collection
def collect_data_decrypt(wp):
    date = []
    content_text = []

    # same range as posts per page
    for j in range(0, len(wp)):
        date.append(wp[j]['date'])
        content_text.append(wp[j]['custom_fields']['content_text'])

    df = pd.DataFrame(columns=['date', 'text'])

    df['date'] = date
    df['text'] = content_text

    return df


# step equals to the results per page
offsets = np.arange(0, 8125, 25).tolist()
frames = []

# Loop that goes through all the available news by shifting the offset
for i in offsets:
    time.sleep(randrange(1))
    print(i)
    cmc = requests.get(
        f'https://api.decrypt.co/content/posts?_minimal=true&category=news&lang=en-US&offset={i}&order=desc&orderby=date&per_page=25')
    time.sleep(1)
    webpage = cmc.json()
    df = collect_data_decrypt(webpage)
    frames.append(df)

# Combining and exporting all the results
result = pd.concat(frames, ignore_index=True)

# for the data update: check duplicates and combine data
# old_data = pd.read_csv(data_folder + '/news/decrypt.csv')
# result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
# result = result.append(old_data)
# result.drop_duplicates(subset=['text'], keep=False,inplace=True)
# result.to_csv(data_folder + '/news/decrypt.csv', index=False)

# Coindesk website data
def collect_data_cd(wp):
    date = []
    text = []

    # same range as posts per page
    for j in range(0, len(wp['posts'])):
        date.append(wp['posts'][j]['date'])

        cmc1 = requests.get('https://www.coindesk.com/' + wp['posts'][j]['slug'])
        soup = BeautifulSoup(cmc1.content, 'html.parser')

        data = soup.find('script',
                         id="__NEXT_DATA__",
                         type="application/json")

        news_data = json.loads(data.contents[0])

        if 'data' in news_data['props']['initialProps']['pageProps']:
            if 'body' in news_data['props']['initialProps']['pageProps']['data']:
                body = news_data['props']['initialProps']['pageProps']['data']['body']

                post = []

                if isinstance(body, list):
                    for item in body:
                        if 'content' in item:
                            post.append(item['content'])
                        elif 'data' in item:
                            if 'items' in item['data']:
                                data_text = ''.join(item['data']['items'])
                                post.append(data_text)
                            elif 'caption' in item['data']:
                                post.append(item['data']['caption'])
                            elif 'content' in item['data']:
                                post.append(item['data']['content'])
                            else:
                                continue
                        else:
                            continue

                    post = ''.join(post)
                    post = re.sub('\<.+?\>|\<\/.+?\>', ' ', post)  # clean code snippets
                    text.append(post)

                elif isinstance(body, str):
                    body = re.sub('\<.+?\>|\<\/.+?\>', ' ', body)  # clean code snippets
                    text.append(body)
            else:
                text.append('Deleted')
        else:
            text.append('Deleted')

    df = pd.DataFrame(columns=['date', 'text'])

    df['date'] = date
    df['text'] = text

    return df


# Page count is limited by news until 2016
offsets = range(0, 210)
frames = []

# Loop that goes through all the available pages
for i in offsets:
    time.sleep(randrange(5))
    print(i)
    cmc = requests.get(f'https://www.coindesk.com/wp-json/v1/articles/format/news/{i}?mode=list')
    time.sleep(3)
    webpage = cmc.json()
    df = collect_data_cd(webpage)
    frames.append(df)

# Combining and exporting all the results
result = pd.concat(frames, ignore_index=True)
result.to_csv(data_folder + '/news/coindesk.csv', index=False)

# for the data update: check duplicates and combine data
# old_data = pd.read_csv(data_folder + '/news/coindesk.csv')
# result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
# result = result.append(old_data)
# result.drop_duplicates(subset=['text'], keep=False,inplace=True)
# result.to_csv(data_folder + '/news/coindesk.csv', index=False)

# The Block scrapper
def collect_data_block(wp):
    date = []
    content_text = []

    # same range as posts per page
    for j in webpage['posts']:
        date.append(j['published'])
        content_text.append(j['body'])

    df = pd.DataFrame(columns=['date', 'text'])

    df['date'] = date
    df['text'] = content_text

    return df


# Starts from page 1 and not 0 (!) to 359
offsets = range(1, 140)
frames = []

# Loop that goes through all the available pages
for i in offsets:
    time.sleep(randrange(3))
    print(i)
    cmc = requests.get(f'https://www.theblockcrypto.com/wp-json/v1/posts/?post_type=&page={i}&posts_per_page=20')
    time.sleep(1)
    webpage = cmc.json()
    df = collect_data_block(webpage)
    frames.append(df)

# Combining and exporting all the results
result = pd.concat(frames, ignore_index=True)
result.to_csv(data_folder + '/news/block.csv', index=False)

# for the data update: check duplicates and combine data
old_data = pd.read_csv(data_folder + '/news/block.csv')
result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
result = result.append(old_data)
result.drop_duplicates(subset=['text'], keep=False,inplace=True)
result.to_csv(data_folder + '/news/block.csv', index=False)

# JSON scrapper with rendered content
def collect_data_json(wp):
    date = []
    content_text = []

    # same range as posts per page
    for j in wp:
        date.append(j['date'])
        content = re.sub('\<.+?\>|\<\/.+?\>', ' ', j['content']['rendered'])  # clean code snippets
        content_text.append(content)

    df = pd.DataFrame(columns=['date', 'text'])

    df['date'] = date
    df['text'] = content_text

    return df


# 1 to total of 163
offsets = range(1, 172)
frames = []

# Go through all the pages
for i in offsets:
    time.sleep(randrange(2))
    print(i)
    cmc = requests.get(f'https://blockonomi.com/wp-json/wp/v2/posts?page={i}&order=desc&orderby=date&per_page=25')
    time.sleep(1)
    webpage = cmc.json()
    df = collect_data_json(webpage)
    frames.append(df)

# Combining and exporting all the results
result = pd.concat(frames, ignore_index=True)
result.to_csv(data_folder + '/news/blockonomi.csv', index=False)

# for the data update: check duplicates and combine data
old_data = pd.read_csv(data_folder + '/news/blockonomi.csv')
result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
result = result.append(old_data)
result.drop_duplicates(subset=['text'], inplace=True)
result.to_csv(data_folder + '/news/blockonomi.csv', index=False)

# Crypto News Flash scrapper
# 1 to 150
offsets = range(1, 150)
frames = []

# Go through all the pages
for i in offsets:
    time.sleep(randrange(2))
    print(i)
    cmc = requests.get(f'https://www.crypto-news-flash.com/wp-json/wp/v2/posts?order=desc&orderby=date&per_page=25&page={i}')
    time.sleep(1)
    webpage = cmc.json()
    df = collect_data_json(webpage)
    frames.append(df)

# Combining and exporting all the results
result = pd.concat(frames, ignore_index=True)
result.to_csv(data_folder + '/news/cnf.csv', index=False)

# for the data update: check duplicates and combine data
old_data = pd.read_csv(data_folder + '/news/cnf.csv')
result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
result = result.append(old_data)
result.drop_duplicates(subset=['text'], inplace=True)
result.to_csv(data_folder + '/news/cnf.csv', index=False)

# News btc sraper
# 1 to 975
offsets = range(1, 60)
frames = []

# Go through all the pages
for i in offsets:
    time.sleep(randrange(3))
    print(i)
    cmc = requests.get(f'https://www.newsbtc.com/wp-json/wp/v2/posts?order=desc&orderby=date&per_page=25&page={i}')
    time.sleep(3)
    webpage = cmc.json()
    df = collect_data_json(webpage)
    frames.append(df)

# Combining and exporting all the results
result = pd.concat(frames, ignore_index=True)
result.to_csv(data_folder + '/news/newsbtc.csv', index=False)

# for the data update: check duplicates and combine data
old_data = pd.read_csv(data_folder + '/news/newsbtc.csv')
result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
result = result.append(old_data)
result.drop_duplicates(subset=['text'], inplace=True)
result.to_csv(data_folder + '/news/newsbtc.csv', index=False)

# Cryptoslate srapper
# 1 to 206
offsets = range(1, 233)
frames = []

# Go through all the pages
for i in offsets:
    time.sleep(randrange(2))
    print(i)
    cmc = requests.get(f'https://cryptoslate.com/wp-json/wp/v2/posts?order=desc&orderby=date&per_page=25&page={i}')
    time.sleep(1)
    webpage = cmc.json()
    df = collect_data_json(webpage)
    frames.append(df)

# Combining and exporting all the results
result = pd.concat(frames, ignore_index=True)
result.to_csv(data_folder + '/news/slate.csv', index=False)

# for the data update: check duplicates and combine data
old_data = pd.read_csv(data_folder + '/news/slate.csv')
result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
result = result.append(old_data)
result.drop_duplicates(subset=['text'], keep=False,inplace=True)
result.to_csv(data_folder + '/news/slate.csv', index=False)

# Cryptonews HTML srapper
driver = webdriver.Firefox()

# Load more articles from the general news page
driver.get('https://cryptonews.com/news/')

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    driver.find_element_by_link_text("Load more news...").click()

# Collect all the links
list = driver.find_elements_by_xpath('//*[@id="body-news"]//div[contains(@class, "app")]//section[contains(@class, "cn-articles-list")]//div[contains(@id, "newsContainer")]//div[contains(@class, "cn-tile article")]//div[contains(@class, "props")]/h4/a')

links=[]
for i in list:
    links.append(i.get_attribute('href'))

# Get text from the article
texts = []
date = []
for i in links:
    driver.get(i)
    article = driver.find_element_by_xpath('//*[@id="body-news"]//div[contains(@class, "app")]/article//div[contains(@class, "content")]//div[contains(@class, "cn-content")]').text
    time_published = driver.find_element_by_xpath('//*[@id="body-news"]//div[contains(@class, "app")]/article//div[contains(@class, "content")]//div[contains(@class, "cn-props-panel")]//div[contains(@class, "time")]/time').get_attribute("datetime")
    texts.append(article)
    date.append(time_published)

# Combine as dataframe
result = pd.DataFrame(columns=['date', 'text'])
result['date'] = date
result['text'] = texts

# for the data update: check duplicates and combine data
old_data = pd.read_csv(data_folder + '/news/cryptonews.csv')
result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
result = result.append(old_data)
result.drop_duplicates(subset=['text'], inplace=True)
result.to_csv(data_folder + '/news/cryptonews.csv', index=False)

# News Bitcoin HTML srapper
# Collect all the article links
links = []
for i in range(1, 135):
    driver.get(f'https://news.bitcoin.com/page/{i}/')
    list = driver.find_elements_by_xpath('//body//div[contains(@id, "td-outer-wrap")]//div[contains(@class, "td-main-content-wrap")]//div[contains(@class, "td-pb-article-list")]//div[contains(@class, "td-pb-row")]//div[contains(@class, "td-main-content")]//div[contains(@class, "td-ss-main-content")]//div[contains(@class, "standard__article standard__article__grid")]//div[contains(@class, "story story--medium")]//div[contains(@class, "story--medium__info")]/a')

    for j in list:
        links.append(j.get_attribute('href'))

# Get text from the article
texts = []
date = []
for i in links:
    driver.get(i)
    time.sleep(0.5)
    article = driver.find_elements_by_xpath('//body//div[contains(@id, "td-outer-wrap")]//div[contains(@id, "bn-ajax-load-more")]//div[contains(@id, "ajax-load-more")]//div[contains(@class, "alm-listing alm-ajax")]//div[contains(@class, "alm-single-post")]//main[contains(@class, "article full-grid")]//article[contains(@class, "article__body")]')[0].text
    time_published = driver.find_elements_by_xpath('//div[contains(@class, "article__info__right")]//time')[0].text
    texts.append(article)
    date.append(time_published)

# Combine as dataframe
result = pd.DataFrame(columns=['date', 'text'])
result['date'] = date
result['text'] = texts

# for the data update: check duplicates and combine data
old_data = pd.read_csv(data_folder + '/news/newsbitcoin.csv')
result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
result = result.append(old_data)
result.drop_duplicates(subset=['text'] ,inplace=True)
result.to_csv(data_folder + '/news/newsbitcoin.csv', index=False)

# Cointelegraph html srapper
# Load the page all the way through
driver.get('https://cointelegraph.com/')

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    driver.find_elements_by_xpath('//button[contains(@class, "posts-listing__more-btn")]')[0].click()

# Collect all the links
list = driver.find_elements_by_xpath('//a[contains(@class, "post-card__title-link")]')
links=[]
for i in list:
    links.append(i.get_attribute('href'))
news= [x for x in links if "https://cointelegraph.com/news/" in x]

# Collect texts and dates
texts = []
date = []

for i in news[len(date):11636]:
    driver.get(i)
    time.sleep(randrange(2))
    article = driver.find_elements_by_xpath('//div[contains(@class, "post-content")]')[0].text
    time_published = driver.find_elements_by_xpath('//div[contains(@class, "post-meta__publish-date")]/time')[0].get_attribute("datetime")
    texts.append(article)
    date.append(time_published)

# Combine as dataframe
result = pd.DataFrame(columns=['date', 'text'])
result['date'] = date
result['text'] = texts

result.to_csv(data_folder + '/news/cointelegraph.csv', index=False)

# for the data update: check duplicates and combine data
old_data = pd.read_csv(data_folder + '/news/cointelegraph.csv')
result[~result.apply(tuple,1).isin(old_data.apply(tuple,1))]
result = result.append(old_data)
result.drop_duplicates(subset=['text'], inplace=True)
result.to_csv(data_folder + '/news/cointelegraph.csv', index=False)

# Stop webdriver
driver.quit()

# Fix newsbitcoin data
df = pd.read_csv(f'data/news/newsbitcoin.csv')
df['date'][0:7] = 'Mar 19, 2021'
df['date'][7:17] = 'Mar 18, 2021'
df['date'][17:29] = 'Mar 17, 2021'
df['date'][29:37] = 'Mar 16, 2021'
df['date'][37:43] = 'Mar 15, 2021'
df['date'][43:44] = 'Mar 14, 2021'

df['date'][1206:1211] = 'Nov 4, 2020'
df['date'][1211:1216] = 'Nov 3, 2020'
df['date'][1216:1221] = 'Nov 2, 2020'
df['date'][1221:1227] = 'Nov 1, 2020'
df['date'][1227:1230] = 'Oct 31, 2020'

df.to_csv(data_folder + '/news/newsbitcoin.csv', index = False)

# Combine all dataframes into one
frames = []
for i in listdir(data_folder + '/news/'):
    df = pd.read_csv(f'data/news/{i}')
    source = ''.join(i.split())[:-4]
    df['source'] = source
    df.date = pd.to_datetime(df.date, infer_datetime_format=True, utc = True)
    frames.append(df)

# Sort data and clean for duplicates and deleted news
result = pd.concat(frames, ignore_index=True)
result['date'] = result['date'].dt.date
result = result.sort_values("date", ascending=False)
result = result.dropna(subset=['text'])
result.drop_duplicates(subset=['text'],inplace=True)

result.to_csv(data_folder + '/all_articles.csv', index=False)

# Number of articles per source per day
result.groupby(result.date).source.value_counts()


# TVL data collection
def collect_tvl(wp):
    time = []
    tvlusd = []
    tvleth = []

    for i in wp:
        time.append(datetime.fromtimestamp(int(i['timestamp'])))
        tvlusd.append(i['tvlUSD'])
        tvleth.append(i['tvlETH'])

    result = pd.DataFrame(columns=['time', 'tvlusd', 'tvleth'])
    result['time'] = time
    result['tvlusd'] = tvlusd
    result['tvleth'] = tvleth

    return result


# Get all the DeFi listed
api_key = 'INSERT YOUR API KEY HERE'
cmc = requests.get(f'https://data-api.defipulse.com/api/v1/defipulse/api/GetHistory?api-key={api_key}&project=all&resolution=history')
webpage = cmc.json()
result = collect_tvl(webpage)

result.time = pd.to_datetime(result.time, infer_datetime_format=True, utc=True)
result.time = result.time.dt.date
result.to_csv(data_folder + '/defi/tvl_all.csv', index=False)

# Collect TVL data for the categories
category = ['lending', 'dexes', 'derivatives', 'payments', 'assets']
frames = []

for i in category:
    cmc = requests.get(f'https://data-api.defipulse.com/api/v1/defipulse/api/GetHistory?api-key={api_key}&project=all&category={i}')
    webpage = cmc.json()
    result = collect_tvl(webpage)
    result['category'] = i
    frames.append(result)

result = pd.concat(frames, ignore_index=True)
result.time = pd.to_datetime(result.time, infer_datetime_format=True, utc=True)
result.time = result.time.dt.date
result.to_csv(data_folder + '/defi/tvl_categories.csv', index=False)

# Collect lending history for Maker
cmc = requests.get(f'https://data-api.defipulse.com/api/v1/defipulse/api/getLendingHistory?api-key={api_key}&project=all&resolution=history&period=all')
webpage = cmc.json()

time = []
borrow_rate =[]
lend_rate = []

for i in webpage:
    time.append(datetime.fromtimestamp(int(i['timestamp'])))
    borrow_rate.append(i['borrow_rates']['maker'])
    lend_rate.append(i['lend_rates']['maker'])

result_maker = pd.DataFrame(columns=['time', 'borrow_rate', 'lend_rate'])
result_maker['time'] = time
result_maker['borrow_rate'] = borrow_rate
result_maker['lend_rate'] = lend_rate

result_maker.time = pd.to_datetime(result_maker.time, infer_datetime_format=True, utc=True)
result_maker.time = result_maker.time.dt.date
result_maker.to_csv(data_folder + '/defi/lending/maker_rates.csv', index=False)

# Collect lending history for Compound
time = []
borrow_rate =[]
lend_rate = []

for i in webpage:
    time.append(datetime.fromtimestamp(int(i['timestamp'])))
    borrow_rate.append(i['borrow_rates']['compound'])
    lend_rate.append(i['lend_rates']['compound'])

result_compound = pd.DataFrame(columns=['time', 'borrow_rate', 'lend_rate'])
result_compound['time'] = time
result_compound['borrow_rate'] = borrow_rate
result_compound['lend_rate'] = lend_rate

result_compound.time = pd.to_datetime(result_compound.time, infer_datetime_format=True, utc=True)
result_compound.time = result_compound.time.dt.date
result_compound.to_csv(data_folder + '/defi/lending/compound_rates.csv', index=False)