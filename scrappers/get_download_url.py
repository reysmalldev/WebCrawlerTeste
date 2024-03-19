import re
from typing import Any
import scrapy
import json
from scrapy import signals
from pydispatch import dispatcher
import os
import sys
import datetime
import time
from pytz import timezone


sys.path.append(f'{os.path.dirname(os.getcwd())}{os.sep}WebCrawlerTeste')
from utils.generate_excel import generate_excel_table


class GetDownloadUrls(scrapy.Spider):
    name = 'melody'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'AUTOTHROTTLE': True,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': False

    }

    # deve ir ate 2963
    def __init__(self, **kwargs: Any):

        dispatcher.connect(self.spider_closed, signals.spider_closed)
        super().__init__(**kwargs)
        self.music_arr = json.load(open(f'{os.getcwd()}{os.sep}output{os.sep}musics.json'))
        self.actually_music = 0
        self.canRun = True

    def start_requests(self):

        while self.actually_music < len(self.music_arr) and self.canRun:
            yield scrapy.Request(self.music_arr[self.actually_music]['url_publication'])


    def parse(self, response, **kwargs):
        music_download_url = []
        try:
            music_download_url = response.xpath(
                '//div[@id="Blog1"]//div[@class="post-item-content"]//div[contains(@class, "post-body") and contains(@class, "post-content")]//a[@data-download-count]/@onclick').get()
            music_download_url = str(music_download_url).split('\'')
        except:
            pass

        for item in music_download_url:
            try:
                if re.match('https', item):
                    self.music_arr[self.actually_music]['download_url'] = item

                else:
                    break

            except:
                self.canRun = False
                pass
        self.actually_music += 1

    def spider_closed(self):
        def sorter_by_date(x):
            # 2024-03-07T13:16:00.002-03:00
            # %Y  -%M-%dT%H:%M:%S.%F -%z
            tz = 'America/Sao_Paulo'
            # date_publi = datetime.datetime.strptime(x["publication_date"], '%Y-%m-%dT%H:%M:%S.%f%z')
            date_publi = datetime.datetime.fromisoformat(x['publication_date'])
            date_publi_sao_paulo = date_publi.astimezone(timezone(tz))
            new_date = date_publi_sao_paulo.strftime('%d/%m/%Y %H:%M:%S')
            x['publication_date'] = new_date
            return date_publi

        self.music_arr = sorted(self.music_arr, key=sorter_by_date, reverse=True)
        time.sleep(1)
        json_dt = json.dumps(self.music_arr, indent=4)
        with open(f'{os.getcwd()}{os.sep}output{os.sep}musics.json', 'w+', encoding="utf-8") as outp:
            outp.write(json_dt)
            outp.close()

        generate_excel_table()
