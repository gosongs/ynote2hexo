#coding=utf-8
import sys
import requests
import time
import re
import os
import shutil
import hashlib
import commands

reload(sys)
sys.setdefaultencoding('utf8')

# Hexo 文件夹
HEXO_DIR = '/Users/go_songs/Documents/fuckblog/source/_posts'
USERNAME = 'go_songs@163.com'
PASSWORD = ''
GITHUB_DIR = ''

# 登录以后存储在 Cookie 里的值
YNOTE_PERS = 'v2|urstoken||YNOTE||web||-1||1498882067319||116.226.216.207||go_songs@163.com||k5RfzEOMqFRPy0Hq4hLzG0gBnfY5PMgL06ZhMz5nH64RQyOMYWnHqS0YM64eBkM6B0e4nfq4nMUf0QB6LJK6LzWR'
YNOTE_SESS = 'v2|8r8rH29TFWpFhHgZ6MeL0wFPLPS6LgyRwLkfzfOMY50kf0LqFkMzERlEnfzWk4gLRUY0Lwz64pz0qLhLPFP4quRlY6LPz6MU50'
YNOTE_LOGIN = '3||1498882067334'
CSTK = 'Jukb45Yq'

HEADERS = {
    'Accept-Encoding':
    'gzip, deflate, br',
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
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
    ts = int(round(time.time() * 1000))
    url = 'https://note.youdao.com/login/acc/urs/verify/check?app=web&product=YNOTE&tp=urstoken&cf=6&fr=1&systemName=&deviceType=&ru=http%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&er=http%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&vcode=&systemName=mac&deviceType=MacPC&timestamp={ts}'.format(
        ts=ts)

    headers = {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':
        'gzip, deflate, br',
        'Accept-Language':
        'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Cache-Control':
        'no-cache',
        'Connection':
        'keep-alive',
        'Host':
        'note.youdao.com',
        'Origin':
        'http://note.youdao.com',
        'Pragma':
        'no-cache',
        'Referer':
        'http://note.youdao.com/signIn/index.html?&callback=https://note.youdao.com/web&from=web',
        'Upgrade-Insecure-Requests':
        '1',
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Cookie':
        'OUTFOX_SEARCH_USER_ID=-328441891@10.120.182.17; YNOTE_URS_VERIFY=xUmNYQhTFWOGkfU5P4JS0Q4nLeyPMYA0TZ0HUYO4qz0QuhLlmOL6BRTyPLYl0LwFRgz6LTzhfpy0pFhHzMRLkfRTuPMY5RMg4R; JSESSIONID=aaa1f5T-FnvJ25degeTYv',
        'Content-Type':
        'application/x-www-form-urlencoded'
    }
    data = {'username': username, 'password': md5(password)}
    res = requests.post(url, data=data, headers=headers, allow_redirects=False)
    print(res.headers)


# 获取所有的笔记本
def getAllBooks():
    data = {'path': '/', 'dirOnly': True, 'f': True, 'cstk': CSTK}
    url = 'https://note.youdao.com/yws/api/personal/file?method=listEntireByParentPath&cstk={CSTK}&keyfrom=web'.format(
        CSTK=CSTK)
    res = requests.post(url, data=data, headers=HEADERS)
    if res.status_code == 200:
        resJson = res.json()
        books = []
        for i in resJson:
            # _私密, _开头的笔记本认为是私密笔记, 跳过
            if i['fileEntry']['name'][0] != '_':
                books.append({
                    'name': i['fileEntry']['name'],
                    'id': i['fileEntry']['id']
                })
        return books
    else:
        exit('getAllBooks')


# 根据笔记本下的笔记
def getAllNotes(book):
    url = 'https://note.youdao.com/yws/api/personal/file/{id}?all=true&cstk={CSTK}&f=true&isReverse=false&keyfrom=web&len=30&method=listPageByParentId&sort=1'.format(
        id=book['id'], CSTK=CSTK)
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        resJson = res.json()
        notes = []
        for i in resJson['entries']:

            # 选出后缀名为md的文件
            if i['fileEntry']['name'][-2:] == 'md' and i['fileEntry']['name'][0] != '_':
                notes.append({
                    'name':
                    i['fileEntry']['name'],
                    'id':
                    i['fileEntry']['id'],
                    'createTime':
                    i['fileEntry']['createTimeForSort'],
                    'modifyTime':
                    i['fileEntry']['modifyTimeForSort'],
                    'tag':
                    book['name']
                })
        return notes
    else:
        exit('getAllNotes')


# 根据笔记信息获取笔记内容
def getNoteDetail(note):
    url = 'https://note.youdao.com/yws/api/personal/file/{id}?method=download&read=true&cstk={CSTK}'.format(
        id=note['id'], CSTK=CSTK)
    res = requests.get(url, headers=HEADERS)
    if res.status_code:
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
    else:
        exit('getNoteDetail')


# 写入文档
def writeMd(detail):
    print('写入: {name}'.format(name=detail['name']))
    with open('_posts/' + detail['name'], 'w') as f:
        f.write('---\n')
        f.write('title: {title}\n'.format(title=detail['name'][:-3]))
        f.write('date: {data}\n'.format(data=detail['time']))
        f.write('tags: {tag}\n'.format(tag=detail['tag']))
        f.write('---\n\n\n')
        f.write(detail['content'])
        f.write('\n')


# 将 _posts 目录替换到 hexo/source/_posts, 并部署提交
# 注意: 这将删除原有 _posts 目录, 请事先备份
def deployHexo():
    shutil.rmtree(HEXO_DIR)
    shutil.copytree('_posts', HEXO_DIR)
    print('开始部署 hexo ...')
    dep = commands.getstatusoutput(
        'cd {hexo_dir} && hexo clean && hexo g && hexo d'.format(
            hexo_dir=HEXO_DIR))
    if dep[0] == 0:
        print('部署成功')
    else:
        print('部署失败')
        print(dep)


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


# MD5 加密
def md5(str):
    md5 = hashlib.md5()
    md5.update(str)
    return md5.hexdigest()


# 退出程序
def exit(why):
    print('{why} 出错了'.format(why=why))
    os._exit(0)


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
    # time.sleep(24 * 60 * 60)
