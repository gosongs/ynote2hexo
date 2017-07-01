#coding=utf-8
import sys
import requests
import time
import re
import os
import shutil

reload(sys)
sys.setdefaultencoding('utf8')

# Hexo 文件夹
HEXO_DIR = '/Users/go_songs/Documents/fuckblog/source/_posts'
USERNAME = 'by_openwater@163.com'
PASSWORD = ''
GITHUB_DIR = ''

# 登录以后存储在 Cookie 里的值
YNOTE_PERS = 'v2|urstoken||YNOTE||web||-1||1498743714357||116.226.216.207||by_openwater@163.com||z5O4UWk4OG0646MQun4lG0lGk4wLk4zGR6BhMQ4RHpFRJy0fYEhMYm0OEPLeBRL6S0lE6LgFRLOf0JunLgZ0LJZ0'
YNOTE_SESS = 'v2|WpBK_0t4FWpB6LkfRMJ40PyOfUfn4pS0kWhMlWnMeS0UGP4OERfP40YGkfUY0MYE06FkMwShHw4RJzOMp4hLTyRqy0MQyRHYA0'
YNOTE_LOGIN = '5||1498785862022'
CSTK = 'oTTw4KcR'

HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
    'Cookie':
    'YNOTE_PERS={YNOTE_PERS}; YNOTE_SESS={YNOTE_SESS}; YNOTE_LOGIN={YNOTE_LOGIN}; YNOTE_CSTK={YNOTE_CSTK}'.
    format(
        YNOTE_PERS=YNOTE_PERS,
        YNOTE_SESS=YNOTE_SESS,
        YNOTE_LOGIN=YNOTE_LOGIN,
        YNOTE_CSTK=CSTK),
    'Accept':
    'application/json, text/plain, */*',
    'Host':
    'note.youdao.com',
    'Origin':
    'https://note.youdao.com',
    'Referer':
    'https://note.youdao.com/web/',
    'Content-Type':
    'application/x-www-form-urlencoded;charset=UTF-8'
}


# 模拟登陆
def mockLogin(username, password):
    # 我需要这四个Cookie的值
    # YNOTE_PERS  https://note.youdao.com/login/acc/login
    # YNOTE_SESS  https://note.youdao.com/login/acc/login
    # YNOTE_LOGIN https://note.youdao.com/login/acc/login
    # YNOTE_CSTK  http://note.youdao.com/yws/mapi/user
    pass


# 获取所有的笔记本
def getAllBooks():
    data = {'path': '/', 'dirOnly': True, 'f': True, 'cstk': CSTK}
    url = 'https://note.youdao.com/yws/api/personal/file?method=listEntireByParentPath&cstk=${CSTK}&keyfrom=web'.format(
        CSTK=CSTK)
    res = requests.post(url, data=data, headers=HEADERS)
    resJson = res.json()
    print(resJson)
    books = []
    for i in resJson:
        # _私密, _开头的笔记本认为是私密笔记, 跳过
        if i['fileEntry']['name'][0] != '_':
            books.append({
                'name': i['fileEntry']['name'],
                'id': i['fileEntry']['id']
            })
    return books


# 根据笔记本下的笔记
def getAllNotes(book):
    url = 'https://note.youdao.com/yws/api/personal/file/{id}?all=true&cstk={CSTK}&f=true&isReverse=false&keyfrom=web&len=30&method=listPageByParentId&sort=1'.format(
        id=book['id'], CSTK=CSTK)
    res = requests.get(url, headers=HEADERS)
    resJson = res.json()
    notes = []
    for i in resJson['entries']:

        # 选出后缀名为md的文件
        if i['fileEntry']['name'][-2:] == 'md' and i['fileEntry']['name'][0] != '_':
            notes.append({
                'name': i['fileEntry']['name'],
                'id': i['fileEntry']['id'],
                'createTime': i['fileEntry']['createTimeForSort'],
                'modifyTime': i['fileEntry']['modifyTimeForSort'],
                'tag': book['name']
            })
    return notes


# 根据笔记信息获取笔记内容
def getNoteDetail(note):
    url = 'https://note.youdao.com/yws/api/personal/file/{id}?method=download&read=true&cstk={CSTK}'.format(
        id=note['id'], CSTK=CSTK)
    res = requests.get(url, headers=HEADERS)
    resCon = res.content

    time = ''
    if note['modifyTime']:  # 优先选用修改时间
        time = parseTS(note['modifyTime'])
    else:
        time = parseTS(note['createTime'])

    detail = {
        'name': filterMark(note['name']),
        'time': time,
        'content': resCon,
        'tag': note['tag']
    }
    return detail


# 写入文档
def writeMd(detail):
    print('写入: {name}'.format(name=detail['name']))
    with open('_posts/' + detail['name'], 'w') as f:
        f.write('---\n')
        f.write('title: {title}\n'.format(title=detail['name']))
        f.write('date: {data}\n'.format(data=detail['time']))
        f.write('tags: {tag}\n'.format(tag=detail['tag']))
        f.write('---\n\n\n')
        f.write(detail['content'])
        f.write('\n')


# 将10位时间戳转为 2017-06-29 10:00:00 的格式
def parseTS(ts):
    timeArr = time.localtime(ts)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArr)


# 过滤特殊字符, 移除原有后缀后重新添加.md
def filterMark(s):
    # s = s.decode("utf8")
    res = re.sub(
        "[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）()]+".decode("utf8"),
        "".decode("utf8"), s)
    res = res.replace(' ', '')
    return res[:-2] + '.md'


# 将 _posts 目录替换到 hexo/source/_posts, 并部署提交
# 注意: 这将删除原有 _posts 目录, 请事先备份
def deployHexo():
    shutil.rmtree(HEXO_DIR)
    shutil.copytree('_posts', HEXO_DIR)
    print('拷贝结束')


# 入口
def start():
    if os.path.exists('_posts'):
        shutil.rmtree(r'_posts')
    os.mkdir(r'_posts')

    books = getAllBooks()
    for i in books:
        notes = getAllNotes(i)
        for j in notes:
            detail = getNoteDetail(j)
            writeMd(detail)
    deployHexo()


if __name__ == '__main__':
    start()
    time.sleep(24 * 60 * 60)