import random
from urllib.parse import parse_qs, urlparse, urlunparse

import requests

user = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991',
    'Mozilla/5.0 (Linux; U; Android 4.2.2; en-us; A1-810 Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30',
    'Mozilla/5.0 (Windows NT 5.1; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Mozilla/5.0 (PLAYSTATION 3 4.81) AppleWebKit/531.22.8 (KHTML, like Gecko)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36 OPR/48.0.2685.52',
    'Mozilla/5.0 (SMART-TV; X11; Linux armv7l) AppleWebKit/537.42 (KHTML, like Gecko) Chromium/25.0.1349.2 Chrome/25.0.1349.2 Safari/537.42',
    'Mozilla/5.0 (Windows NT 6.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.2.7 (KHTML, like Gecko)',
    'Mozilla/5.0 (PlayStation 4 5.01) AppleWebKit/601.2 (KHTML, like Gecko)']

header = {'User-Agent': random.choice(user)}
proxies = {"http": "http://127.0.0.1:8000", "https": "http://127.0.0.1:8000"}
request = requests.Session()


def requester(url, proxy, parameters=''):
    if proxy:
        webpage = request.get(url, allow_redirects=False, headers=header, proxies=proxies, verify=False, timeout=30,
                              params=parameters)
    else:
        webpage = request.get(url, allow_redirects=False, headers=header, timeout=10, verify=False, params=parameters)

    return webpage


def multitest(url, payload_path="payloads.txt"):
    if urlparse(url).scheme == '':
        url = 'http://' + url
    if type(payload_path) is list:
        payloads = payload_path
    else:
        payloads = open(payload_path, encoding='utf-8').read().splitlines()

    if '=' in url:
        if url.endswith('='):
            url += 'r007'

        query_parsed = parse_qs(urlparse(url).query)
        keys = [i for i in query_parsed]
        values = [i for i in query_parsed.values()]

        parsed_url = list(urlparse(url))
        parsed_url[-2] = ''
        modified_url = urlunparse(parsed_url)

        query_list = []
        count = 0
        for key in keys:
            for payload in payloads:
                query_parsed[key] = payload
                query_list.append(query_parsed.copy())

            query_parsed[key] = values[count]
            count += 1
        return query_list, modified_url
    else:
        url_list = []
        print('Appending payloads just after the URL')
        if url.endswith('/'):
            pass
        elif not url.endswith('/'):
            url = url + '/'
        for payload in payloads:
            url_list.append(url + payload)

        return url_list
