from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta


# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('index.html')


# API 역할을 하는 부분
# db 만들기 API
@app.route('/api/list', methods=['POST'])
def post_list():
    # 1. 클라이언트로부터 데이터를 받기
    url_receive = request.form['url_give']

    # 2. meta tag를 스크래핑하기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    iherb_title = soup.select_one('meta[property="og:title"]')['content']
    iherb_brand = soup.select_one('meta[property="og:brand"]')['content']
    iherb_img = soup.select_one('#iherb-product-image')['src']

    a12 = soup.select_one('#breadCrumbs > a:nth-child(12)')
    a7 = soup.select_one('#breadCrumbs > a:nth-child(7)')
    if a12 is not None:
        iherb_category = a12.text
    elif a7 is not None:
        iherb_category = a7.text
    else:
        iherb_category = soup.select_one('#breadCrumbs > a:nth-child(11)').text

    iherb_direction = soup.select_one(
        'body > div.product-grouping-wrapper.defer-block > article > div.container.product-overview > div > section > div.inner-content > div > div > div.col-xs-24.col-md-14 > div:nth-child(2) > div > div').text

    list = {'url': url_receive, 'title': iherb_title, 'brand': iherb_brand, 'image': iherb_img,
            'category': iherb_category, 'direction': iherb_direction}

    # 3. mongoDB에 데이터를 넣기
    db.supplements.insert_one(list)
    return jsonify({'result': 'success', 'msg': '등록했습니다!'})


@app.route('/api/list', methods=['GET'])
def read_list():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    result = list(db.supplements.find({}, {'_id': 0}))
    # 2. lists라는 키 값으로 list 정보 보내주기
    return jsonify({'result': 'success', 'msg': 'get 연결됨', 'lists': result})


@app.route('/api/delete', methods=['POST'])
def delete_star():
    # 1. 클라이언트가 전달한 name_give를 name_receive 변수에 넣습니다.
    # 2. mystar 목록에서 delete_one으로 name이 name_receive와 일치하는 star를 제거합니다.
    # 3. 성공하면 success 메시지를 반환합니다.
    return jsonify({'result': 'success', 'msg': 'delete 연결되었습니다!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
