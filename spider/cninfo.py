from spider.spider import Spider
import requests
import json
import re
import os


class Cninfo(Spider):
    def __init__(self, year_limit, save_dir):
        super(Cninfo, self).__init__()
        self.year_limit = year_limit
        self.codes_json = 'codes.json'
        self.pdfs_links_json = 'pdfs_links.json'
        self.save_dir = save_dir

    def crawler(self):
        if not os.path.isfile(self.codes_json):
            self.code_get()
        if not os.path.isfile(self.pdfs_links_json):
            self.pdfs_links_get()
        self.down_load()

    def pdf_links_get(self, code, years_limit):
        datas = {
            'stock': code,
            'category': "category_ndbg_szsh",
            'pageNum': '1',
            'pageSize': '50',
            'column': 'szse_sme',
            'tabName': 'fulltext'
        }
        request_url = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'

        s = self.request_session.post(request_url, data=datas).text

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

    def pdfs_links_get(self):
        year_limit = [str(i) for i in self.year_limit]
        db_data = []
        data = json.load(open(self.codes_json, 'r'))
        count_num = 0
        total_num = len(data)
        for item in data:
            count_num += 1
            print("获取年报链接 共%s个公司 第%s个" % (total_num, count_num))
            tmp = {'code': item['Col00']}
            tmp['pdf'] = self.pdf_links_get(tmp['code'], year_limit)
            db_data.append(tmp.copy())
        json.dump(db_data, open(self.pdfs_links_json, 'w'), ensure_ascii=False)

    def code_get(self):
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
        json.dump(codes, open(self.codes_json, 'w'), ensure_ascii=False)

    def down_load(self):
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
        base_url = 'http://www.cninfo.com.cn/'
        datas = json.load(open(self.pdfs_links_json, 'r'))
        pdf_count = 0
        total_num = 0
        for data in datas:
            total_num += len(data['pdf'])
        for data in datas:
            code = data['code']
            for pdf in data['pdf']:
                pdf_count += 1
                save_path = self.save_dir + '/' + code + '_' + pdf['year'] + '.pdf'
                if os.path.exists(save_path):
                    continue
                print("下载年报 共%s份 第%s份" % (total_num, pdf_count))
                url = base_url + pdf['link']
                self.file_download(url=url, filename=save_path)


if __name__ == '__main__':
    years = [2000, 2018]
    pdf_save_path = 'pdfs'

    cninfo = Cninfo(range(years[0], years[1] + 1), pdf_save_path)
