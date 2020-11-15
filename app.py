from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient('mongodb://test:test@52.79.208.17',27017)
db = client.dbsparta


# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('index03.html')


# API 역할을 하는 부분
# db 만들기 API
@app.route('/data', methods=['POST'])
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

    a7 = soup.select_one('#breadCrumbs > a:nth-child(7)')
    a12 = soup.select_one('#breadCrumbs > a:nth-child(12)')

    if a12 is not None:
        iherb_category = a12.text
    elif a7 is not None:
        iherb_category = a7.text
    else:
        iherb_category = soup.select_one('#breadCrumbs > a:nth-child(11)').text

    iherb_direction = soup.select_one(
        'body > div.product-grouping-wrapper.defer-block > article > div.container.product-overview > div > section > div.inner-content > div > div > div.col-xs-24.col-md-14 > div:nth-child(2) > div > div').text
    iherb_checked = 0

    list = {'url': url_receive, 'title': iherb_title, 'brand': iherb_brand, 'image': iherb_img,
            'category': iherb_category, 'direction': iherb_direction, 'checked': iherb_checked}

    # 3. mongoDB에 데이터를 넣기
    db.supplements.insert_one(list)
    return jsonify({'result': 'success', 'msg': '등록했습니다!'})


@app.route('/list', methods=['GET'])
def read_list():
    # 1. mongoDB에서 모든 데이터를 리스트로 조회하기 (Read)
    read_result = list(db.supplements.find({}))

    # 2. 조회해 온 리스트에서 _id값을 string 값으로 바꾸기
    def id_decoder(list):
        results = []
        for document in list:
            document['_id'] = str(document['_id'])
            results.append(document)
        return results

    result = id_decoder(read_result)

    # 2. 불러온 정보들을 json 형식으로 보내주기
    return jsonify({'result': 'success', 'msg': 'get 연결됨', 'lists': result})


@app.route('/update', methods=['POST'])
def update_list():
    # 1. 클라이언트가 전달한 id_give를 id_receive 변수에 넣습니다.
    check_receive = request.form['check_give']
    id_receive = request.form['id_give']

    # 2. supplements 목록에서 _id이 id_received인 문서의 checked 를 check_received로 변경합니다.
    # 참고: '$set' 활용하기!
    db.supplements.update_one({"_id": ObjectId(id_receive)}, {'$set': {'checked': check_receive}})

    # 3. 성공하면 success 메시지를 반환합니다.
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
