import argparse
import pathlib


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--output-file', help='File to save data', dest="output_file",
                        type=pathlib.Path, required=True)

    parser.add_argument('-u', '--url', help='scan single target', dest="url")
    parser.add_argument('-l', '--list', help='scan multiple target', dest='path')
    parser.add_argument('-crlf', help='scan for CRLF Injection', action='store_true', dest='crlf')
    parser.add_argument('-p', '--payload', help='use payloads from a file', dest='payload')
    parser.add_argument('--proxy', help='use proxy', action='store_true', dest='proxy')
    parser.add_argument('--wayback', help='fetch URLs from archive.org', action="store_true",
                        dest='waybacks')

    return parser.parse_args()
