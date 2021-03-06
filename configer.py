#!/usr/bin/env python3

import urllib.parse
import requests
import queue
import os
import interface

class Download_Configer(object):

    # Init download settings...
    def __init__(self, url, saveto):
        self.url = url
        parse_result = urllib.parse.urlparse(self.url)
        self.filename = self.url.split('/')[-1]
        self.protocol = parse_result.scheme
        self.domain = parse_result.netloc
        self.saveto = saveto
        self.path = os.path.join(self.saveto, self.filename)
        self.max_thread = 10
        self.min_block = 1000
        self.down_queue = queue.Queue(self.max_thread)
        self._get_url_header()
        self._block_content()
        self._touch_file()

    # Occur HEAD request and get more information
    def _get_url_header(self):
        interface.info_out('HTTP_REQUEST')
        headers = {
            'Range': 'bytes=0-1'
        }
        response = requests.get(self.url, stream = True, headers = headers)
        if response.status_code == 206:
            self.partital_content = True
            interface.info_out('PARTITAL_SUPPORT')
            self.content_length =int(response.headers['Content-Range']\
                    .split('/')[1])
        elif response.status_code // 100 == 4:
            interface.info_out('CONNECTION_ERROR', response.status_code)
        elif response.status_code // 100 == 2:
            self.partital_content = False
            interface.info_out('PARTITAL_NOT_SUPPORT')
            self.content_length = int(response.headers['Content-Length'])
        interface.info_out('CONTENT_LENGTH', self.content_length)

    # Break tasks into partital content
    def _block_content(self):
        if self.content_length // self.max_thread > self.min_block:
            self.min_block = self.content_length // self.max_thread+1
        self.x = 0
        while self.x < self.content_length:
            if self.x+self.min_block > self.content_length:
                self.down_queue.put((self.x, self.content_length-1))
            else:
                self.down_queue.put((self.x, self.x+self.min_block-1))
            self.x += self.min_block

    def _touch_file(self):
        open(self.path, 'w').close()


if __name__ == '__main__':
    d = Download_Configer('https://raw.githubusercontent.com/getlantern/lantern-binaries/master/lantern-installer-beta.exe',
            '/home/lancaster')
    while not d.down_queue.empty():
        print(d.down_queue.get())
