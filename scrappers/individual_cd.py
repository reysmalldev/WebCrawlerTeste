from typing import Any
import scrapy
import json
from scrapy import signals
from pydispatch import dispatcher
import os
import datetime
import time
from pytz import timezone
from utils.generate_excel import generate_excel_table
from utils.cd_music import Music_CD


class CorrectAuthorName(scrapy.Spider):
    name = 'melody'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'AUTOTHROTTLE': True
    }

    # deve ir ate 2963
    def __init__(self, **kwargs: Any):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        super().__init__(**kwargs)
        self.page_num = 1
        self.music_arr = []
        # self.max_music_number = 2964  # se você trocar o valor máximo de músicas no site o programa se limitará (ou ampliará seu alcance) a
        # tal número de músicas para coleta.
        self.log_text = ''
        self.parse_selector_is_one = True
        self.counter_individual_requests_array = 0
        self.music_arr = json.load(open(f'{os.getcwd()}{os.sep}output{os.sep}musics.json'))
        self.music_arr_final = []

    def start_requests(self):
        self.music_arr = json.load(open(f'{os.getcwd()}{os.sep}output{os.sep}musics.json'))
        for music in self.music_arr:
            yield scrapy.Request(music['download_url'], callback=self.parse)
            time.sleep(0.02)

    def parse(self, response, **kwargs):
        music_author = response.xpath('//div[@class="post-item-content"]//div[@class="post-meta"]/span[@class="post-author"]/a/text()').get()
        print(f'music {self.counter_individual_requests_array}')
        self_music = self.music_arr[(self.counter_individual_requests_array)]
        m_cd = Music_CD(title=self_music['title'], download_url=self_music['download_url'],
                        publication_date=self_music['publication_date'], image_url=self_music['image_url'],
                        author=music_author)
        self.music_arr_final.append(m_cd.to_dict())
        self.counter_individual_requests_array += 1

    def spider_closed(self):
        def sorter_by_date(x):
            # 2024-03-07T13:16:00.002-03:00
            # %Y  -%M-%dT%H:%M:%S.%F -%z
            tz = 'America/Sao_Paulo'
            date_publi = datetime.datetime.strptime(x["publication_date"], '%Y-%m-%dT%H:%M:%S.%f%z')
            date_publi_sao_paulo = date_publi.astimezone(timezone(tz))
            new_date = date_publi_sao_paulo.strftime('%d/%m/%Y %H:%M:%S')
            x['publication_date'] = new_date
            return date_publi

        self.music_arr_final = sorted(self.music_arr_final, key=sorter_by_date, reverse=True)
        time.sleep(1)
        json_dt = json.dumps(self.music_arr_final, indent=4)
        with open(f'{os.getcwd()}{os.sep}output{os.sep}musics.json', 'w+', encoding="utf-8") as outp:
            outp.write(json_dt)
            outp.close()
        with open(f'{os.getcwd()}{os.sep}output{os.sep}musicas_array.txt', 'w+', encoding="utf-8") as outp:
            outp.write(str(self.music_arr_final))
            outp.close()

        generate_excel_table()
