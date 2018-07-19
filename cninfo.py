from urllib import parse
import requests
import json
import re
import os


def pdf_link(code):
    datas = {
        'stock': code,
        'category': "category_ndbg_szsh",
        'pageNum': '1',
        'pageSize': '50',
        'column': 'szse_sme',
        'tabName': 'fulltext'
    }

    Request_URL = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'

    requestSession = requests.session()
    r = requestSession.post(Request_URL, data=datas)

    s = r.text
    data = json.loads(s)['announcements']
    ret = []
    for item in data:
        title = item['announcementTitle'].split("年年度报告")
        if len(title) < 2:
            continue
        if len(title[1]) == 0:
            tmp = {'year': title[0], 'link': item['adjunctUrl']}
            ret.append(tmp.copy())
    return ret


def code_get():
    Request_URL = 'http://www.cninfo.com.cn/cninfo-new/select/selectStock'
    params = {
        'area': '',
        'index': '',
        'industry': '',
        'market': '',
        'pagenum': 0
    }
    requestSession = requests.session()
    hasNextPage = True
    pagenum = 0
    all_codes = []
    while hasNextPage:
        pagenum += 1
        print('pagenum: %s' % pagenum)
        params['pagenum'] = pagenum
        text = requestSession.get(url=Request_URL, params=params).text
        data = json.loads(text)
        all_codes.append(data['items'])
        hasNextPage = data['hasNextPage']
    json.dump(all_codes, open('all_codes.json', 'w'), ensure_ascii=False)


def data_json_create():
    data = json.load(open('all_codes.json', 'r'))
    codes = []
    for page in data:
        codes += page
    json.dump(codes, open('codes.json', 'w'), ensure_ascii=False)


def pdf_link_save():
    db_data = []
    data = json.load(open('codes.json', 'r'))
    count_num = 0
    for item in data:
        print(count_num)
        count_num += 1
        tmp = {}
        tmp['code'] = item['Col00']
        tmp['pdf'] = pdf_link(tmp['code'])
        db_data.append(tmp.copy())
    json.dump(db_data, open('pdf_link.json', 'w'), ensure_ascii=False)


def tmp():
    requestSession = requests.session()

    Request_URL = "http://www.cninfo.com.cn/cninfo-new/disclosure/fund_listed_latest"
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    requestSession.headers.update({'User-Agent': UA})
    mainResponse = requestSession.get(Request_URL)
    print(mainResponse.cookies.get_dict())

    'sortName=&sortType=&limit=&showTitle=&exchange=&fundtype=&'

    'stock=&searchkey=&plate=&category=&trade=&'
    params = {
        'column': 'fund_listed',
        'columnTitle': '%E5%9F%BA%E9%87%91%E5%85%AC%E5%91%8A',
        'pageNum': '2',
        'pageSize': '30',
        'tabName': 'latest',
        'seDate': '%E8%AF%B7%E9%80%89%E6%8B%A9%E6%97%A5%E6%9C%9F'}
    r = requestSession.post(Request_URL, data=params)
    print(r.cookies.get_dict())
    with open('debug.html', 'wb') as f:
        s = r.text.encode('utf-8')
        print(type(s))
        f.write(s)

    # print(parse.quote('上海'))
    print(parse.unquote('%E8%AF%B7%E9%80%89%E6%8B%A9%E6%97%A5%E6%9C%9F'))


def pdf_link_recode():
    years = [str(i) for i in range(2000, 2019)]
    datas = json.load(open('pdf_link.json', 'r'))
    for i in range(len(datas)):
        for j in range(len(datas[i]['pdf'])):
            if datas[i]['pdf'][j]['year'] not in years:
                tmp = re.findall("\d\d\d\d", datas[i]['pdf'][j]['year'])
                if len(tmp) > 0:
                    datas[i]['pdf'][j]['year'] = tmp[0]
    json.dump(datas, open('pdf_link_recode.json', 'w'))


def file_download(url, filename):
    pdf = requests.get(url)
    pf = open(filename, 'wb')
    pdf.raise_for_status()  # 函数查看下载文件是否出错，如果加载出错就抛出异常，否则就什么都不做。
    for buff in pdf.iter_content():
        pf.write(buff)
    pf.close()


def down_load():
    baseUrl = 'http://www.cninfo.com.cn/'
    datas = json.load(open('pdf_link_recode.json', 'r'))
    code_count = 0
    for data in datas:
        code_count += 1
        pdf_count = 0
        code = data['code']
        for pdf in data['pdf']:
            pdf_count += 1
            save_path = 'pdfs/' + code + '_' + pdf['year'] + '.pdf'
            if os.path.exists(save_path):
                continue
            url = baseUrl + pdf['link']
            file_download(url=url, filename=save_path)
            print(code_count, pdf_count)


if __name__ == '__main__':
    down_load()
