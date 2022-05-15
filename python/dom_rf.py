import requests as rq
import pandas as pd
from tqdm.auto import tqdm
import re, os

objid = []
objects_data = {'OBJ': []}

def insert_reg():
    reg = input("Введите регион (all - все регионы): ")
    if reg == 'all':
        reg = None
    return reg

def insert_img():
    q = input("Скачать фото строящегося объекта? (Да/Нет): ")
    if q == "Нет":
        print("Работа завершена")
    elif q == "Да":
        id_obj = int(input("Введите id объекта:"))
    return id_obj

def objids(reg):
    offset = 0
    print('Собираю ID строящихся объектов:')
    while True:
        url = 'https://наш.дом.рф/сервисы/api/kn/object'
        params = {'offset': offset,
                  'limit': 100,
                  'sortField': "devId.devShortCleanNm",
                  'sortType': 'asc',
                  'objStatus': 0,
                  'place': reg}
        res = rq.get(url, params=params)
        obj_data = res.json()
        obj = obj_data.get('data').get('list')
        total_obj = obj_data.get('data').get('total')
        for objs in obj:
            objid.append(objs.get('objId'))
        if not obj:
            break
        offset += 100
        print('Всего:', len(objid), 'объектов собрано из', total_obj)
    with open('obj_id.txt', 'w') as filehandle:
        filehandle.writelines("%s\n" % obj_id for obj_id in objid)

def download_img(id_obj):
    pattern = r'src":"(https://[^"]*file/[^"]{36})"'
    pattern_1 = r'"filename":"(obj[^"]*_[^"]{12}).'
    url_obj = f'https://наш.дом.рф/сервисы/каталог-новостроек/объект/{id_obj}'
    obj = rq.get(url_obj).text
    url_img = re.findall(pattern, obj)
    name_img = re.findall(pattern_1, obj)
    if not os.path.exists(f'images/{id_obj}'):
        os.makedirs(f'images/{id_obj}')
        for idx, img in enumerate(url_img):
            img_data = rq.get(img).content
            with open(f'images/{id_obj}/{id_obj}_{name_img[idx]}_{idx}.jpg', 'wb') as f:
                f.write(img_data)
        print(f"Фото объекта {id_obj} скачаны в кол-ве {len(url_img)} шт.")
    else:
        print(f"Папка для объекта {id_obj} уже создана")
def main ():
    objids(insert_reg())
    url_obj = 'https://наш.дом.рф/сервисы/api/object/{}'
    print('Собираем все данные по каждому объекту: ')
    for i in tqdm(objid):
        res = rq.get(url_obj.format(i))
        objects_list = res.json()
        objects_data['OBJ'].append(objects_list['data'])
    print("Записываем в файл 'domrf.xlsx'")
    df = pd.json_normalize(objects_data.get('OBJ'))
    df.to_excel('domrf.xlsx', index=False)
    download_img(insert_img())

if __name__ == '__main__':
    main()

