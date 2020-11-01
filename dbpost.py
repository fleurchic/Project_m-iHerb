import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbsparta

# DB에 저장할 영양 출처 url을 가져옵니다.

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(
    'https://kr.iherb.com/pr/Mason-Natural-Healthy-Kids-Cod-Liver-Oil-Chewable-with-Vitamin-D-Artificial-Orange-Flavor-100-Chewables/50059',
    headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

title = soup.select_one('meta[property="og:title"]')['content']
brand = soup.select_one('meta[property="og:brand"]')['content']
img = soup.select_one('#iherb-product-image')['src']

a12 = soup.select_one('#breadCrumbs > a:nth-child(12)')
a7 = soup.select_one('#breadCrumbs > a:nth-child(7)')
if a12 is not None:
    category = a12.text
elif a7 is not None:
    category = a7.text
else:
    category = soup.select_one('#breadCrumbs > a:nth-child(11)').text

direction = soup.select_one(
    'body > div.product-grouping-wrapper.defer-block > article > div.container.product-overview > div > section > div.inner-content > div > div > div.col-xs-24.col-md-14 > div:nth-child(2) > div > div').text


# print(brand, '/', title, '/', img, '/', category, '/', direction)
print(category)