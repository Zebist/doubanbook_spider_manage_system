![image](https://github.com/Zebist/scrapy_manage_system/assets/31758228/94076116-98b0-4aa7-9aa7-829cb80eb6be)# scrapy_manage_system 爬虫管理系统
## 用于爬取DOUBAN图书 TOP250列表
## 一、 环境安装
### 1. Python版本： 3.10.12   
### 2. 安装postgresql数据库，并创建数据库
### 3. 安装依赖
      apt-get install libpq-dev
### 3. python依赖包，用根目录下requirement.txt安装python依赖
      pip install -r requirement.txt
### 4. 需要安装redis
      apt-get install redis
## 二、 文件配置
### 1. 数据库设置
#### a. 在根目录的db_info.ini文件中设置数据库信息，参考如下
        [database]
        name = crawl_system
        user = crawl_1
        password = 123456789cq
        host = localhost
        port = 5432
### 2. 爬虫设置
      在scrapy_manage_system/crawl_douban_top250/目录下的settings.py进行设置
### A. 两个可用的中间件（默认已开启，下述顺序为执行顺序）
#### 1.  代理中间件ProxyMiddleware（继承自RetryMiddleware）
      i. 实现了自动识别重定向和代理切换
      ii. 代理可重复使用，直至无法连接或被禁用
      iii. 如需切换其他代理，在settings.py文件中设置PROXY_URL，中间件会从该URL获取代理池
            1. 重写修改ProxyMiddleware的req_new_proxy方法，可以支持不同返回格式的代理，只要在该方法内将返回结果处理到和期望的JSON格式一致，即可正常和其他功能对接```json{'code': 1, 'info': '获取成功', 'data': [{'ip': 0.0.0.0, 'port': 8080}]}```
      iiii. 如无需启用代理，关闭中间件，或将settings.py文件中的PROXY_URL值删除即可
#### 2.  记录中间件CrawlRecordMiddleware
      i. 用于记录每次爬取的页面地址和爬取结果
      ii. 只记录TOP250页面，不记录图片页面
      iii. 在初始化url时，将未爬取成功的记录导入到初始url，补爬遗漏的数据
### B. 三个管道 （默认已开启）
      1. 去重管道：根据目标网站获取到的ID，进行去重处理
      2. 图片管道：用于下载图片
            i. 数据存在media文件夹中，正式环境可迁移对接到文件系统
      3. PostgreSQL管道： 将数据插入到PostgreSQL
## 三、 运行项目
### 1. 在根目录下执行迁移
      python manage.py makemigrations
      python manage.py migrate
### 2. 启动web服务
      在根目录运行 
      python manage.py runserver 0.0.0.0:8080
### 3. 启动Celery队列
      在根目录运行
      celery -A scrapy_management_system worker --loglevel=info
### 4. 启动爬虫
      使用IP访问页面，在首页可以看到【开始爬取】按钮，单击启动爬虫
      也可在根目录运行
      scrapy crawl douban_book
#### a. 页面默认每10秒刷新1次数据
## 四、 技术说明
      1. 使用Scrapy作为爬虫框架，通过请求头、代理切换，重定向文件识别，解决了目标网站的反爬
      2. 使用Django、DRF作为后端，使用视图集实现CRUD
      3. 使用JQ、Bootstrap及Datatables插件搭建了前端页面
## 五、 功能说明
### 1. 爬虫按钮
![image](https://github.com/Zebist/scrapy_manage_system/assets/31758228/ac856e6f-0ea1-4d09-8d35-ecfa027ed234)
### 2. CRUD
![image](https://github.com/Zebist/scrapy_manage_system/assets/31758228/1b1e3749-1cd0-41e2-9d93-20fcc3ea66bd)
### 可以在页面底部添加数据，豆瓣书籍ID和书名、图片是必填字段（由于爬取时可以获取到ID，所以选择书籍ID进行去重）
![image](https://github.com/Zebist/scrapy_manage_system/assets/31758228/25236ca7-836f-4ee8-b6d7-5a231639cd12)
### 3. 其他： 页面支持搜索、排序、分页
![image](https://github.com/Zebist/scrapy_manage_system/assets/31758228/e901c385-fd39-43da-b564-9d50e308b5e9)


        
       
