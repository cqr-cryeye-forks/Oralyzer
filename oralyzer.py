#!/usr/bin/env python3
import json
import random
import ssl
import sys
import warnings

import requests
from bs4 import BeautifulSoup

from args import init_args
from constants import result_dict
from core.crlf import crlf_scan
from core.others import requester, multitest, urlparse
from core.wayback import get_urls


def analyze(url, file):
    if urlparse(url).scheme == '':
        url = 'http://' + url
    # global multi_test
    multi_test = multitest(url, file)

    print('Infusing payloads')
    if isinstance(multi_test, tuple):
        for params in multi_test[0]:
            testing_break = request(url=multi_test[1], params=params, file=file)

            if testing_break:
                break
    else:
        for url in multi_test:
            testing_break = request(url=url, file=file)
            if testing_break:
                break


def request(url, file, proxy='', params='', payload_index=0):
    skip = 1
    if proxy:
        try:
            page = requester(url, True, params)
        except requests.exceptions.Timeout:
            print(f"Timeout {url}")
            return skip
        except requests.exceptions.ConnectionError:
            print("Connection Error")
            return skip
    else:
        try:
            page = requester(url, False, params)
        except requests.exceptions.Timeout:
            print(f"Timeout {url}")
            return skip
        except requests.exceptions.ConnectionError:
            print(f"Connection Error {url}")
            return skip
        except IndexError:
            payload_index = 0

    function_break = check(page, page.request.url, file[payload_index])
    payload_index += 1
    if function_break:
        return skip


def check(page_var, final_url, payload='http://www.google.com'):
    skip = 1
    redirect_codes = [i for i in range(300, 311, 1)]
    soup = BeautifulSoup(page_var.text, 'html.parser')
    location = 'window.location' in str(soup.find_all('script'))
    href = 'location.href' in str(soup.find_all('script'))
    google = payload in str(soup.find_all('script'))
    metas = str(soup.find_all('meta'))
    meta_tag_search = payload in metas

    if page_var.status_code in redirect_codes:
        if meta_tag_search and "http-equiv=\"refresh\"" in metas:
            # TODO: maybe need to add it to dict?
            print("Meta Tag Redirection")
            return skip

        else:
            if 'redirects' not in result_dict:
                result_dict['redirects'] = []

            # Check if the URL is not already in the 'redirects' list
            if not any(entry['url'] == final_url for entry in result_dict['redirects']):
                result_dict['redirects'].append({'url': final_url, 'redirected_to': page_var.headers['Location']})

            # result_dict['redirects'].append({'url': final_url, 'redirected_to': page_var.headers['Location']})
            print(f'Header Based Redirection: {final_url} -> {page_var.headers['Location']}')

    elif page_var.status_code == 200:
        if 'found' not in result_dict and location or href:
            result_dict['found'] = []

        if google:

            print("Javascript Based Redirection")
            if location and href:
                print(f"Vulnerable Source Found: {location} -> \033[1mwindow.location\033[00m")
                print(f"Vulnerable Source Found: {href} .> \033[1mlocation.href\033[00m")

                if not any(entry['url'] == final_url for entry in result_dict['found']):
                    result_dict['found'].append(
                        {
                            'url': final_url,
                            'status_code': 200,
                            'vulnerable': True,
                            'href': href,
                            'location': location,
                            'info': 'Javascript Based Redirection.\n'
                                    'Try fuzzing the URL for DOM XSS',
                        }
                    )

            elif href:
                print(f"Vulnerable Source Found: {href} -> \033[1mlocation.href\033[00m")

                if not any(entry['url'] == final_url for entry in result_dict['found']):
                    result_dict['found'].append(
                        {
                            'url': final_url,
                            'status_code': 200,
                            'vulnerable': True,
                            'href': href,
                            'info': 'Javascript Based Redirection.\n'
                                    'Try fuzzing the URL for DOM XSS',
                        }
                    )

            elif location:
                print(f"Vulnerable Source Found: {location} -> \033[1mwindow.location\033[00m")

                if not any(entry['url'] == final_url for entry in result_dict['found']):
                    result_dict['found'].append(
                        {
                            'url': final_url,
                            'status_code': 200,
                            'vulnerable': True,
                            'location': location,
                            'info': 'Javascript Based Redirection.\n'
                                    'Try fuzzing the URL for DOM XSS',
                        }
                    )

            print("Try fuzzing the URL for DOM XSS")
            return skip

        elif location:
            if 'window.location = {}'.format(payload):
                print(payload, ' - it\'s a payload, however saving location. In next row: ')
                print(f"Vulnerable Source Found: {location} -> \033[1mwindow.location\033[00m")
                print("Try fuzzing the URL for DOM XSS")

                if not any(entry['url'] == final_url for entry in result_dict['found']):
                    result_dict['found'].append(
                        {
                            'url': final_url,
                            'status_code': 200,
                            'vulnerable': True,
                            'location': location,
                            'info': 'Try fuzzing the URL for DOM XSS',
                        }
                    )

                return skip
            else:
                print("%s Potentially Vulnerable Source Found: \033[1mwindow.location\033[00m")

                if not any(entry['url'] == final_url for entry in result_dict['found']):
                    result_dict['found'].append(
                        {
                            'url': final_url,
                            'status_code': 200,
                            'vulnerable': True,
                            'location': location,
                            'info': 'Potentially Vulnerable Source',
                        }
                    )
        # else:
        #     print(f"{final_url} not vulnerable, but 200")
        #
        #     if not any(entry['url'] == final_url for entry in result_dict['found']):
        #         result_dict['found'].append(
        #             {
        #                 'url': final_url,
        #                 'status_code': 200,
        #                 'vulnerable': False,
        #             }
        #         )

        if meta_tag_search and "http-equiv=\"refresh\"" in str(page_var.text):
            print("Meta Tag Redirection")

            # if 'redirects' not in result_dict:
            #     result_dict['redirects'] = []

            if not any(entry['url'] == final_url for entry in result_dict['found']):
                result_dict['found'].append(
                    {
                        'url': final_url,
                        'status_code': 200,
                        'vulnerable': False,
                        'info': 'Meta Tag Redirection.',
                    }
                )

            return skip

        elif "http-equiv=\"refresh\"" in str(page_var.text) and not meta_tag_search:
            print("The page is only getting refreshed")

            if not any(entry['url'] == final_url for entry in result_dict['found']):
                result_dict['found'].append(
                    {
                        'url': final_url,
                        'status_code': 200,
                        'vulnerable': False,
                        'info': 'The page is only getting refreshed.',
                    }
                )

            return skip

    # elif page_var.status_code == 404:
    #     print(f"{final_url} status {page_var.status_code}")
    # elif page_var.status_code == 403:
    #     print(f"{final_url} status {page_var.status_code}")
    # elif page_var.status_code == 400:
    #     print(f"{final_url} status {page_var.status_code}")

    else:
        if 'not_found' not in result_dict:
            result_dict['not_found'] = []

        if not any(entry['url'] == final_url for entry in result_dict['not_found']):
            result_dict['not_found'].append({'url': final_url, 'status_code': page_var.status_code})

        print(f"{final_url} {page_var.status_code}")


def main():
    if sys.version_info.major > 2 and sys.version_info.minor > 6:
        pass
    else:
        print("Oralyzer requires at least Python 3.7.x to run.")
        exit()

    warnings.filterwarnings('ignore')
    ssl._create_default_https_context = ssl._create_unverified_context

    args = init_args()

    url = args.url
    path = args.path
    proxy = args.proxy
    output_file = args.output_file

    if not args.url and not args.path:
        print('Made by \033[97mr0075h3ll\033[00m')
        print('You wrote wrong arguments.')
        exit()

    if args.payload:
        file_path = args.payload
        file = open(file_path, encoding='utf-8').read().splitlines()
    else:
        try:
            file_path = 'payloads.txt'
            file = open(file_path, encoding='utf-8').read().splitlines()
        except FileNotFoundError:
            print("Payload file not found! Try using '-p' flag to use payload file of your choice")
            exit()

    if args.path:
        url_list = open(path, encoding='utf-8').read().splitlines()

    try:
        if not args.waybacks and not args.crlf and args.url:
            analyze(url=url, file=file)

        elif args.crlf:
            if args.proxy and args.path:
                for url in url_list:
                    print(f"Target {url}")
                    crlf_scan(url=url, foxy=True)
                    print("__")
            elif args.proxy and not args.path:
                crlf_scan(url=url, foxy=True)

            elif args.path and not args.proxy:
                for url in url_list:
                    print(f"Target {url}")
                    crlf_scan(url=url, foxy=False)
                    print("__")
            else:
                crlf_scan(url=url, foxy=False)

        elif not args.waybacks and args.path:
            for url in url_list:
                print(f"Target {url}")
                analyze(url=url, file=file)
                print("__")

        elif args.url and args.waybacks:
            print("Getting juicy URLs with \033[1m\033[93mwaybackurls\033[00m\033[00m")
            get_urls(url, "wayback_urls.txt")

        elif args.path and args.waybacks:
            print("Getting juicy URLs with \033[93mwaybackurls\033[00m")
            for url in url_list:
                print(f"Target: {url}")
                get_urls(url=url, path="wayback_{}.txt".format(random.randint(0, 100)))
                print("__")

        else:
            print("Filename not specified")

    except KeyboardInterrupt:
        print("Quitting...")
        exit()

    json_data = json.dumps(result_dict)
    output_file.write_text(json_data)
    print(f"Final results save to {output_file.absolute().as_uri()}")


if __name__ == '__main__':
    main()
