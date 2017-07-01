## 同步有道云笔记中的 markdown 笔记到 hexo 博客
![](./assets/ynote2hexo_3.png)
![](./assets/ynote2hexo_1.png)
![](./assets/ynote2hexo_2.png)

## Install

```python
pip install requests

# 修改 start.py 中的 HEXO_DIR 为你的 Hexo 目录
# 修改 start.py 中的 USERNAME 为你的有道云笔记账号
# 修改 start.py 中的 PASSWORD 为你的有道云笔记密码
python start.py
```

## 操作流程
1. 模拟登陆, 获取访问其他接口的权限, 需要 `YNOTE_PERS`、`YNOTE_SESS`、`YNOTE_LOGIN`、`YNOTE_CSTK` 这四个存在 `Cookie` 里的值;
1. 读取笔记本, 忽略 `_` 开头的笔记本;
1. 读取笔记本里的笔记, 忽略 `_` 开头的笔记;
1. 读取笔记并存储为 `.md` 格式的文件到 `_posts` 中;
1. 替换 `_posts` 文件夹到 `hexo/source/_posts`;
1. 部署 Hexo;
1. 部署到服务器以后, 可以添加定时任务, 比如每天凌晨同步一次;

## 注意
+ 频繁退出/登录, 会触发验证码, 代码不做处理;
+ 忽略富文本笔记, 只读取 markdown 格式的笔记;
+ `_` 开头的笔记本和笔记认为是私密的, 不会读取;
+ 笔记本不支持嵌套;
+ 由于 Hexo 标题限制, 将移除标题里的特殊字符和空格, 仅允许中文/英文/数字组合;
+ 由于 Hexo 内容限制, 笔记中不能出现类似于 `{{}}` 或者 `{%%}` 的片段, 这将导致 `hexo generate` 失败;

## TODO
+ [ ] 模拟登陆;
+ [x] 部署 Hexo;
+ [ ] 定时任务;
+ [ ] 代码太挫了, 需要改改;

**欢迎 Fork 和 Start ! 🤓**