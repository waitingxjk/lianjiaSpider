﻿# -*- coding: utf-8 -*-
"""
@author: ziyubiti
@site: http://ziyubiti.github.io
@date: 20160808
"""

from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from bs4 import BeautifulSoup
import random
import mysql.connector
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
import smtplib

hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},\
    {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},\
    {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},\
    {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},\
    {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]


#=========================setup a database, only execute in 1st running=================================
def database_init(dbflag='local'):
     if dbflag=='local':
         conn = mysql.connector.connect(user='root', password='password', database='lianjiaSpider',host='localhost')
     else:
         conn = mysql.connector.connect(user='qdm', password='password', database='qdm',host='qdm.my3w.com')
     dbc = conn.cursor()

     # 创建houseinfo and hisprice表:
     dbc.execute('create table if not exists houseinfo (id int(10) NOT NULL AUTO_INCREMENT primary key,houseID varchar(50) , Title varchar(200), link varchar(200), cellname varchar(100),\
                years varchar(200),housetype varchar(50),square varchar(50), direction varchar(50),floor varchar(50),taxtype varchar(200), \
                totalPrice varchar(200), unitPrice varchar(200),followInfo varchar(200),validdate varchar(50),validflag varchar(20))')

     dbc.execute('create table if not exists hisprice (id int(10) NOT NULL AUTO_INCREMENT primary key,houseID varchar(50) , date varchar(50), totalPrice varchar(200))')
     dbc.execute('create table if not exists cellinfo (id int(10) NOT NULL AUTO_INCREMENT primary key,Title varchar(50) , link varchar(200),district varchar(50),bizcircle varchar(50),tagList varchar(200))')

     conn.commit()
     dbc.close()
     return conn
#==============================================================================

def celllist_read_from_database(conn):
    cursor = conn.cursor()
    cursor.execute('select * from cellinfo ')
    values = cursor.fetchall()         #turple type

    celllist = []
    for j in range(len(values)):
        celllist.append(values[j][1])

    return celllist



def cellinfo_insert_mysql(conn,info_dict):

    t=(info_dict[u'Title'],info_dict[u'link'],info_dict[u'district'],info_dict[u'bizcircle'],info_dict[u'tagList'])  # for cellinfo

    cursor = conn.cursor()

    cursor.execute('select * from cellinfo where Title = (%s)',(info_dict[u'Title'],))
    values = cursor.fetchall()         #turple type

    if len(values)==0:        # new cell
        cursor.execute('insert into cellinfo (Title,link,district,bizcircle,tagList) values (%s,%s,%s,%s,%s)', t)
    else:
        cursor.execute('update cellinfo set link = %s,district = %s, bizcircle = %s,tagList = %s where Title = %s',\
                       (info_dict[u'link'],info_dict[u'district'],info_dict[u'bizcircle'],info_dict[u'tagList'],info_dict[u'Title']))

    conn.commit()
    cursor.close()


def houseinfo_insert_mysql(conn,info_dict):

    info_list = [u'houseID',u'Title',u'link',u'cellname',u'years',u'housetype',u'square',u'direction',u'floor',\
                u'taxtype',u'totalPrice',u'unitPrice',u'followInfo',u'validdate',u'validflag']
    t=[]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    t=tuple(t)    # for houseinfo

    today = get_today()
    t2=(info_dict[u'houseID'],today,info_dict[u'totalPrice'])  # for hisprice

    cursor = conn.cursor()

    cursor.execute('select * from houseinfo where houseID = (%s)',(info_dict[u'houseID'],))
    values = cursor.fetchall()         #turple type
    if len(values)>0:
        nvs = zip(info_list,list(values[0][1:]))
        Qres = dict( (info_list,value) for info_list,value in nvs)
    else:
        pass

    if len(values)==0:        # new house
        cursor.execute('insert into houseinfo (houseID,Title,link,cellname,years,housetype,square,direction,floor,\
                      taxtype,totalPrice,unitPrice,followInfo,validdate,validflag) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', t)
        cursor.execute('insert into hisprice (houseID,date,totalPrice) values (%s,%s,%s)', t2)
#        trigger_notify_email(info_dict,'newhouse')
    else:
        cursor.execute('update houseinfo set totalPrice = %s,unitPrice = %s,followInfo = %s,validdate = %s,\
                       validflag= %s where houseid = %s',(info_dict[u'totalPrice'],info_dict[u'unitPrice'],\
                                                          info_dict[u'followInfo'],today,'1',info_dict[u'houseID']))

        if int(today)>int(Qres[u'validdate']):
            cursor.execute('insert into hisprice (houseID,date,totalPrice) values (%s,%s,%s)', t2)
        else:
#            cursor.execute('update houseinfo set validflag= %s where houseid = %s',('1',info_dict[u'houseID']))
            cursor.execute('update hisprice set totalPrice= %s where houseid = %s',(info_dict[u'totalPrice'],info_dict[u'houseID']))
        if float(Qres[u'totalPrice']) != float(info_dict[u'totalPrice']):    # str2float,when str2int is error
            info_dict[u'oldprice'] = Qres[u'totalPrice']
#            trigger_notify_email(info_dict,'updateprice')

    conn.commit()
    cursor.close()
    # only to solve mysql conn not available problem
#    sql = "SELECT * FROM houseinfo"
#    cursor.execute( sql )
##    dbRec = cursor.fetchone()
#    while cursor.fetchone():       # comment this out to fix the "bug"
#        pass
#




def trigger_notify_email(info_dict,reason='newhouse'):
    if reason == 'newhouse':
        title = u'新上房源' + ' ' + info_dict[u'cellname'] + ' ' + info_dict[u'housetype'] + ' ' + info_dict[u'totalPrice']+'万'
        cotent_txt = u'新上房源' + ' ' + info_dict[u'cellname'] + ' ' + info_dict[u'housetype'] + ' 朝向' + info_dict[u'direction'] + \
                     ' 面积' + info_dict[u'square'] + ' 总价' + info_dict[u'totalPrice']+'万  单价' + info_dict[u'unitPrice']+'万每平米' \
                     + u'  房源编号' + info_dict[u'houseID'] + ' ' + u'查看链接 ' + info_dict[u'link']
        content_html = '<html><body><h1>新上房源</h1>' + '<p>' +  info_dict[u'cellname'] + ' ' + info_dict[u'housetype'] + \
                        ' 朝向' + info_dict[u'direction'] + ' 面积' + info_dict[u'square'] + ' 总价' + info_dict[u'totalPrice'] + \
                        '万  单价' + info_dict[u'unitPrice']+'万每平米' + u'  房源编号' + info_dict[u'houseID'] + ' ' + u'点击查看链接 ' + \
                        '<a href=\"'+ info_dict[u'link'] + '\">' +  info_dict[u'link']  + '</a>...</p>' + '</body></html>'
    else:
        title = u'房屋价格变动' + ' ' + info_dict[u'cellname'] + ' ' + info_dict[u'housetype'] + info_dict[u'oldprice'] + '----> ' + info_dict[u'totalPrice']+'万'
        cotent_txt = u'房屋价格变动' + ' ' + info_dict[u'cellname'] + ' ' + info_dict[u'housetype'] + ' 朝向' + info_dict[u'direction'] + \
                     ' 面积' + info_dict[u'square'] + ' 总价 ' + info_dict[u'oldprice']+'万 ' + '----> ' + info_dict[u'totalPrice']+'万  单价' + \
                     info_dict[u'unitPrice']+'万每平米' + u'  房源编号' + info_dict[u'houseID'] + ' ' + u'查看链接 ' + info_dict[u'link']
        content_html = '<html><body><h1>房屋价格变动</h1>' + '<p>' +  info_dict[u'cellname'] + ' ' + info_dict[u'housetype'] + \
                        ' 朝向' + info_dict[u'direction'] + ' 面积' + info_dict[u'square'] + ' 总价 ' + info_dict[u'oldprice']+'万 ' \
                        + '----> '+ info_dict[u'totalPrice'] + '万  单价' + info_dict[u'unitPrice']+'万每平米' + u'  房源编号' + \
                        info_dict[u'houseID'] + ' ' + u'点击查看链接 ' + '<a href=\"'+ info_dict[u'link'] + '\">' +  info_dict[u'link'] + \
                         '</a>...</p>' + '</body></html>'


    from_addr = 'ziyubiti@qq.com'
    #password = raw_input('Password: ')
    password = 'password'
    to_addr = 'ziyubiti@139.com'
    smtp_server = 'smtp.qq.com'

    msg = MIMEMultipart('alternative')
    msg.attach(MIMEText(cotent_txt, 'plain', 'utf-8'))
    msg.attach(MIMEText(content_html, 'html', 'utf-8'))

    msg['From'] = _format_addr(u'紫雨 <%s>' % from_addr)
    msg['To'] = _format_addr(u'紫雨 <%s>' % to_addr)
    msg['Subject'] = Header(title, 'utf-8').encode()
    smtp_port = 465   #25 or 587
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls() # 使用安全链接SSL,port 587,qq still is 25
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()



def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))



def all_set_unvalid(conn):
    cursor = conn.cursor()
    cursor.execute('update houseinfo set validflag= %s',('0',))
    conn.commit()
    cursor.close()


def get_today():
    now = datetime.now()
    m = now.month
    d = now.day
    if m<10:
        ms = '0'+str(m)
    else:
        ms = str(m)
    if d<10:
        ds = '0'+str(d)
    else:
        ds = str(d)
    today = str(now.year)+ ms + ds
    return today



def house_percell_spider(conn,cellname = u'荣丰2008'):

    url=u"http://bj.lianjia.com/ershoufang/rs" + quote(cellname) +"/"

    try:
        req = Request(url,headers=hds[random.randint(0,len(hds)-1)])
        source_code = urlopen(req,timeout=50).read()
        soup = BeautifulSoup(source_code,'lxml')
    except HTTPError as e:
        print (e)
        return
    except Exception as e:
        print (e)
        return
    total_pages = 0
#====================== method 1:step is good ,file run is wrong========================================================
#     page_info = "page_info =" + soup.find('div',{'class':'page-box house-lst-page-box'}).get('page-data')  #'{"totalPage":5,"curPage":1}'
#     exec(page_info)
#     total_pages = page_info['totalPage']
#==============================================================================
#======================method 2:string split  ========================================================
    try:
        page_info= soup.find('div',{'class':'page-box house-lst-page-box'})
    except AttributeError as e:
        page_info = None

    if page_info == None:
        return None

    page_info_str = page_info.get('page-data').split(',')[0]  #'{"totalPage":5,"curPage":1}'
    total_pages= int(page_info_str[-1])      # max page 9,total 30*9=270, no cell has so much house
#==============================================================================
    info_dict_all = {}   # if each house info_dict insert into database ,this info_dict_all is not needed

    for page in range(total_pages):
        if page>0:
            url_page=u"http://bj.lianjia.com/ershoufang/pg%drs%s/" % (page+1,quote(cellname))
            req = Request(url_page,headers=hds[random.randint(0,len(hds)-1)])
            source_code = urlopen(req,timeout=50).read()
            soup = BeautifulSoup(source_code,'lxml')

        
        nameList = soup.findAll("li", {"class":"clear"})
        i = 0

        for name in nameList:   # per house loop
            i = i + 1
            info_dict = {}
            info_dict_all.setdefault(i+page*30,{})

            housetitle = name.find("div",{"class":"title"})  #html
            info_dict.update({u'Title':housetitle.get_text().strip()})
            info_dict.update({u'link':housetitle.a.get('href')})   #atrribute get

            houseaddr = name.find("div",{"class":"address"})
            info = houseaddr.div.get_text().split('|')
            info_dict.update({u'cellname':info[0]})
            info_dict.update({u'housetype':info[1]})
            info_dict.update({u'square':info[2]})
            info_dict.update({u'direction':info[3]})

            housefloor = name.find("div",{"class":"flood"})
            floor_all = housefloor.div.get_text().split('-')[0].strip().split(' ')
            info_dict.update({u'floor':floor_all[0]})
            info_dict.update({u'years':floor_all[-1]})

            followInfo = name.find("div",{"class":"followInfo"})
            info_dict.update({u'followInfo':followInfo.get_text()})

            tax = name.find("div",{"class":"tag"})
            info_dict.update({u'taxtype':tax.get_text().strip()})   # none span
            #info_dict.update({u'taxtype':tax.span.get_text()})

            totalPrice = name.find("div",{"class":"totalPrice"})
            info_dict.update({u'totalPrice':totalPrice.span.get_text()})

            unitPrice = name.find("div",{"class":"unitPrice"})
            info_dict.update({u'unitPrice':unitPrice.get('data-price')})
            info_dict.update({u'houseID':unitPrice.get('data-hid')})

            today = get_today()
            info_dict.update({u'validdate':today})
            info_dict.update({u'validflag':str('1')})

            # adding open houseid url,and save the images for each house,TBC


            # houseinfo insert into mysql
            houseinfo_insert_mysql(conn,info_dict)

            info_dict_all[i+page*30] = info_dict

    return info_dict_all


def house_celllist_spider(conn,celllist = [u'荣丰2008',u'保利茉莉公馆']):
    all_set_unvalid(conn)
    for cellname in celllist:
        house = house_percell_spider(conn,cellname)
    return house         # unit test



def cell_perregion_spider(conn,regionname = u'xicheng'):

    url=u"http://bj.lianjia.com/xiaoqu/" + regionname +"/"

    #try:
    req = Request(url,headers=hds[random.randint(0,len(hds)-1)])
    source_code = urlopen(req,timeout=50).read()
    soup = BeautifulSoup(source_code,'lxml')
    #except (HTTPError, URLError), e:
    #    print e
    #    return
    #except Exception,e:
    #    print e
    #    return
    total_pages = 0
#====================== method 1:step is good ,file run is wrong========================================================
#     page_info = "page_info =" + soup.find('div',{'class':'page-box house-lst-page-box'}).get('page-data')  #'{"totalPage":5,"curPage":1}'
#     exec(page_info)
#     total_pages = page_info['totalPage']
#==============================================================================
#======================method 2:string split  ========================================================
    try:
        page_info= soup.find('div',{'class':'page-box house-lst-page-box'})
    except AttributeError as e:
        page_info = None

    if page_info == None:
        return None

    page_info_str = page_info.get('page-data').split(',')[0].split(':')[1]  #'{"totalPage":5,"curPage":1}'
    total_pages= int(page_info_str)
#==============================================================================
    info_dict_all = {}   # if each house info_dict insert into database ,this info_dict_all is not needed

    for page in range(total_pages):
        if page>0:
            url_page=u"http://bj.lianjia.com/xiaoqu/" + regionname +"/pg%d/" % (page+1,)
            req = Request(url_page,headers=hds[random.randint(0,len(hds)-1)])
            source_code = urlopen(req,timeout=50).read()
            soup = BeautifulSoup(source_code,'lxml')


        nameList = soup.findAll("li", {"class":"clear"})
        i = 0

        for name in nameList:   # per house loop
            i = i + 1
            info_dict = {}
            info_dict_all.setdefault(i+page*30,{})

            celltitle = name.find("div",{"class":"title"})  #html
            info_dict.update({u'Title':celltitle.get_text()})
            info_dict.update({u'link':celltitle.a.get('href')})   #atrribute get

            district = name.find("a",{"class":"district"})  #html
            info_dict.update({u'district':district.get_text()})
            bizcircle = name.find("a",{"class":"bizcircle"})
            info_dict.update({u'bizcircle':bizcircle.get_text()})

            tagList = name.find("div",{"class":"tagList"})
            info_dict.update({u'tagList':tagList.get_text()})

            # cellinfo insert into mysql
            cellinfo_insert_mysql(conn,info_dict)

            info_dict_all[i+page*30] = info_dict

#    return info_dict_all    #only for unit test


def cell_regionlist_spider(conn,regionlist = [u'xicheng']):
    for regionname in regionlist:
        cell_perregion_spider(conn,regionname)
#        celldict = cell_perregion_spider(conn,regionname)
#    return celldict       # only unit test
