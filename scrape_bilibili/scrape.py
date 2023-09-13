import warnings
import requests
import json
import re
import xlwings
import wordcloud
import imageio
from collections import Counter


_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.1.4031 SLBChan/30',
        'cookie': "buvid3=F4CF005D-3661-2933-2C20-8BACB2076D2204287infoc; "
                  "buvid4=340B1103-BF89-C761-C38C-EACC5D82F44C08366-022020418-ytR2gTyIVaYIbHk7uUmljg%3D%3D; "
                  "i-wanna-go-back=-1; buvid_fp_plain=undefined; "
                  "DedeUserID=1634225630; DedeUserID__ckMd5=3b8f8e6647446875; "
                  "b_nut=100; _uuid=578748A10-7963-2F13-10383-10B5A47A22B5124002infoc; hit-dyn-v2=1; "
                  "rpdid=|(u))kkYu|l~0J'uYY)lmJmRl; header_theme_version=CLOSE; nostalgia_conf=-1; "
                  "CURRENT_PID=b925c810-ce2b-11ed-a72d-63d92ec03751; FEED_LIVE_VERSION=V8; is-2022-channel=1; "
                  "CURRENT_FNVAL=4048; fingerprint=9bd6aaff721b364241f57a8d31c9017d; b_ut=5; "
                  "CURRENT_QUALITY=80; "
                  "SESSDATA=70855e4a%2C1709464733%2Cf148a%2A91OEBR4o2zOPMK5Zl0LkiwfR7iqAUrmTJPaqBiQpawQBYo_ExC8xWiVXS"
                  "L5jjvW7u1R8x_zgAAHgA; bili_jct=2dd8f53b1aa1b8c705283d646a5b3675; hit-new-style-dyn=1; "
                  "bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTQxNzM0OTg"
                  "sImlhdCI6MTY5MzkxNDI5OCwicGx0IjotMX0.QA1nQejs7DW7BOjGqah_Xmmr-dojC8vUmoR4aQYqD74; "
                  "bili_ticket_expires=1694173498; PVID=1; buvid_fp=9bd6aaff721b364241f57a8d31c9017d; "
                  "bp_video_offset_1634225630=838820380079554560; browser_resolution=1536-758; home_feed_column=5; "
                  "sid=6e9sark0; b_lsid=DC2119DC_18A73F7989F"
    }


def get_bvid(_page, _pos):
    # 获取视频的bvid
    # 通过搜索api“https://api.bilibili.com/x/web-interface/search/all/v2?page=1-15&keyword=”获取前300个视频的bvid
    _url = 'https://api.bilibili.com/x/web-interface/search/all/v2?page='+str(_page)+'&keyword=日本核污染水排海'
    res = requests.get(url=_url, headers=_headers, verify=False).text
    json_dict = json.loads(res)
    return json_dict["data"]["result"][11]["data"][_pos]["bvid"]


def get_cid(_bvid):
    # 根据bvid请求得到cid
    # 视频地址：https://www.bilibili.com/video/BV1PK4y1b7dt?t=1
    url = f'https://api.bilibili.com/x/player/pagelist?bvid={_bvid}&jsonp=jsonp'
    res = requests.get(url).text
    # 将获取的网页json编码字符串转换为python对象
    json_dict = json.loads(res)
    # print(json_dict)
    return json_dict["data"][0]["cid"]


def get_danmu(_cid):
    # https://api.bilibili.com/x/v1/dm/list.so?oid=1253529510
    # 获取弹幕并保存在'弹幕.txt'中
    url = "https://api.bilibili.com/x/v1/dm/list.so?oid=" + str(_cid)
    # print(url)
    response = requests.get(url=url, headers=_headers)
    response.encoding = response.apparent_encoding
    # print(response.text)
    data_list = re.findall('<d p=".*?">(.*?)</d>', response.text)
    for data in data_list:
        with open('弹幕.txt', 'a', encoding='utf-8') as _f:
            _f.write(data)
            _f.write('\n')
            print(data)


def count_danmu():
    # 统计弹幕数量排名前20的弹幕输出,并排序弹幕于'弹幕top.txt'中
    # 在存入之前，先清空'弹幕top.txt'中的内容
    _f = open('弹幕top.txt', 'w', encoding='utf-8')
    _f.close()
    _file = '弹幕.txt'
    lists = []
    with open(_file, 'r', encoding='utf-8') as _f:
        for line in _f:
            lists.append(line.strip())
    d_counter = Counter(lists)
    # print(d_counter)
    # top_20 = d_counter.most_common(20)
    wb = xlwings.Book('弹幕.xlsx')
    sht = wb.sheets('sheet1')
    sht.range('A1').value = '序号'
    sht.range('B1').value = '弹幕'
    sht.range('C1').value = '出现次数'
    # 将所有数据(d_counter)存到excel表'弹幕.xlsx'中
    top_66975 = d_counter.most_common(66975)
    for idx, (danmu, count) in enumerate(top_66975, 1):
        if count > 2:
            sht.range(f'A{int(idx) + 1}').value = idx
            sht.range(f'B{int(idx) + 1}').value = danmu
            sht.range(f'C{int(idx) + 1}').value = count
    # 将top_20中的数据存入'弹幕top.txt'中
    for idx, (danmu, count) in enumerate(top_66975, 1):
        if int(idx) <= 20:
            print(f'排名：{idx:>3}    弹幕：{danmu:15}    出现次数：{count}')
        with open('弹幕top.txt', 'a', encoding='utf-8') as _f:
            _f.write(danmu)
            _f.write('\n')
    wb.save()


def make_cloud():
    # 生成词云
    _f = open('弹幕top.txt', 'r', encoding='utf-8')
    txt = _f.read()
    img = imageio.imread('1.png')
    wc = wordcloud.WordCloud(
        width=800,
        height=500,
        min_font_size=6,
        background_color='white',
        mask=img,
        font_path='STSONG',
    )
    wc.generate(txt)
    wc.to_file('弹幕词云.png')
    _f.close()


warnings.filterwarnings("ignore")
# 忽略不安全警告

if __name__ == '__main__':
    # 通过以'w'打开文件将文件中的内容删掉
    f = open('弹幕.txt', 'w', encoding='utf-8')
    f.close()
    for page in range(1, 16):
        for pos in range(20):
            bvid = get_bvid(page, pos)
            cid = get_cid(bvid)
            get_danmu(cid)
    count_danmu()  # 整理弹幕数据
    make_cloud()
