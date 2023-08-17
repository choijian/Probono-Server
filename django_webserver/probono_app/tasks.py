import requests
from celery import shared_task
from config import settings, utils

'''
서버 구동 후, 반드시 터미널 창 두개 열어서 실행해야 함.
celery -A your_project worker -l info
celery -A your_project beat -l info
'''

db_handle = utils.db_handle
get_collection = utils.get_collection_handle

@shared_task
def get_subway_elvtr_task():
    base_url = 'http://openapi.seoul.go.kr:8088/4f6a5a74796c696d3534425a686562/json/tbTraficElvtr'
    start_index = 1
    end_index = 100

    all_data = []
    while True:
        url = f"{base_url}/{start_index}/{end_index}/"
        response = requests.get(url)
        data = response.json()
        if 'tbTraficElvtr' in data and 'row' in data['tbTraficElvtr']:
            all_data.extend(data['tbTraficElvtr']['row'])
        start_index += 100
        end_index += 100
        if len(data['tbTraficElvtr']['row']) < 100:
            break

    # save to Mongo DB
    # Right here
    collection_elevtr = get_collection(db_handle, 'subway_elevator')
    collection_elevtr.delete_many({})
    for data in all_data:
        sw_nm = data.get('SW_NM', '')
        node_wkt = data.get('NODE_WKT', '')
        coordinates = node_wkt.replace("POINT(", "").replace(")", "").split()
        x = coordinates[0]
        y = coordinates[1]
        subway_elevator = {
            'sw_nm' : sw_nm,
            'x'     : x,
            'y'     : y
        }
        collection_elevtr.insert_one(subway_elevator)
    return