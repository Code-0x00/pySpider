import requests
import json
import re
import os


def pdf_links_get(code, years_limit):
    datas = {
        'stock': code,
        'category': "category_ndbg_szsh",
        'pageNum': '1',
        'pageSize': '50',
        'column': 'szse_sme',
        'tabName': 'fulltext'
    }
    request_url = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'
    request_session = requests.session()
    s = request_session.post(request_url, data=datas).text

    data = json.loads(s)['announcements']
    ret = []
    for item in data:
        title = item['announcementTitle'].split("年年度报告")
        if len(title) < 2:
            continue
        if len(title[1]) == 0:
            title_sp = re.findall("\d\d\d\d", title[0])
            if len(title_sp) > 0 and title_sp[0] in years_limit:
                tmp = {'year': title_sp[0], 'link': item['adjunctUrl']}
                ret.append(tmp.copy())
    return ret


def pdfs_links_get(codes_path, save_path, list_years):
    year_limit = [str(i) for i in range(list_years[0], list_years[1] + 1)]
    db_data = []
    data = json.load(open(codes_path, 'r'))
    count_num = 0
    total_num = len(data)
    for item in data:
        count_num += 1
        print("获取年报链接 共%s个公司 第%s个" % (total_num, count_num))
        tmp = {'code': item['Col00']}
        tmp['pdf'] = pdf_links_get(tmp['code'], year_limit)
        db_data.append(tmp.copy())
    json.dump(db_data, open(save_path, 'w'), ensure_ascii=False)


def code_get(save_path):
    request_url = 'http://www.cninfo.com.cn/cninfo-new/select/selectStock'
    params = {
        'area': '',
        'index': '',
        'industry': '',
        'market': '',
        'pagenum': 0
    }
    request_session = requests.session()
    has_next_page = True
    pagenum = 0
    page_total_num = "???"
    codes = []
    while has_next_page:
        pagenum += 1
        print('获取股票代码 共%s页 第%s页' % (page_total_num, pagenum))
        params['pagenum'] = pagenum
        text = request_session.get(url=request_url, params=params).text
        data = json.loads(text)
        codes += data['items']
        has_next_page = data['hasNextPage']
        page_total_num = data['totalPages']
    json.dump(codes, open(save_path, 'w'), ensure_ascii=False)


def file_download(url, filename):
    pdf = requests.get(url)
    pf = open(filename, 'wb')
    pdf.raise_for_status()
    for buff in pdf.iter_content():
        pf.write(buff)
    pf.close()


def down_load(link_path, save_path_base):
    if not os.path.exists(save_path_base):
        os.mkdir(save_path_base)
    base_url = 'http://www.cninfo.com.cn/'
    datas = json.load(open(link_path, 'r'))
    pdf_count = 0
    total_num = 0
    for data in datas:
        total_num += len(data['pdf'])
    for data in datas:
        code = data['code']
        for pdf in data['pdf']:
            pdf_count += 1
            save_path = save_path_base + '/' + code + '_' + pdf['year'] + '.pdf'
            if os.path.exists(save_path):
                continue
            print("下载年报 共%s份 第%s份" % (total_num, pdf_count))
            url = base_url + pdf['link']
            file_download(url=url, filename=save_path)


if __name__ == '__main__':
    years = [2000, 2018]
    codes_json = 'codes.json'
    pdfs_links_json = 'pdfs_links.json'
    pdf_save_path = 'pdfs'

    if not os.path.isfile(codes_json):
        code_get(codes_json)
    if not os.path.isfile(pdfs_links_json):
        pdfs_links_get(codes_json, pdfs_links_json, years)
    down_load(pdfs_links_json, pdf_save_path)
