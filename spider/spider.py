import requests


class Spider:

    def __init__(self):
        self.codeType = 'utf-8'
        self.response = ''

        self.request_session = requests.session()
        self.UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        self.request_session.headers.update({'User-Agent': self.UA})

    def save_text(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.response.encode(self.codeType))

    def content_get(self, url):
        mainResponse = requests.get(url)
        return mainResponse.text

    def file_download(self, url, filename):
        pdf = self.request_session.get(url)
        pdf.raise_for_status()  # 函数查看下载文件是否出错，如果加载出错就抛出异常，否则就什么都不做。
        with open(filename, 'wb') as pf:
            for buff in pdf.iter_content():
                pf.write(buff)


if __name__ == '__main__':
    sp = Spider()
    sp.file_download('http://www.cninfo.com.cn/finalpage/2018-04-24/1204700915.PDF', 'test.pdf')
