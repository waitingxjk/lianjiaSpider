import urllib, urllib.parse
import hashlib
import time


def url_encoding(lng, lat, keywords: list, radius=2000):
    if not keywords:
        return
    # 
    query = "$".join(keywords)
    queryStr = '/place/v2/search?query={query}&location={lat},{lng}&radius={radius}&output=json&timestamp={timestamp}&ak=RfiQOLB0fWjGZKwECu5PkdowBCyDHwFq'
    queryStr = queryStr.format(query=query, lat=lat, lng=lng, radius=radius, timestamp=int(time.time()))
    
    # ��queryStr����ת�룬safe�ڵı����ַ���ת��
    encodedStr = urllib.parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    encodedStr = encodedStr + "&sn=" + hashlib.md5(urllib.parse.quote_plus(encodedStr).encode("utf-8")).hexdigest()

    return "http://api.map.baidu.com" + encodedStr

#url: http://cd.fang.lianjia.com/loupan/p_ztaweaacri/xiangqing
url = url_encoding( 103.882033, 30.829593, ["ҽԺ","����"])