import re
from typing import Any
import scrapy
import json
from scrapy import signals
from pydispatch import dispatcher
import datetime
import numpy as np
from pytz import timezone
import os
import sys

sys.path.append(os.getcwd())
from utils.cd_music import Music_CD
from utils.generate_excel import generate_excel_table


class GetAllMusicsPage(scrapy.Spider):
    name = 'melody'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': False,
        'AUTOTHROTTLE_MAX_DELAY': 1,
        'AUTOTHROTTLE_START_DELAY': 0,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 50.0,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 50
    }

    # deve ir ate 2963
    def __init__(self, **kwargs: Any):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        super().__init__(**kwargs)
        self.page_num = 1
        self.actually_music_index = 1
        self.max_results = 10
        self.musics_per_page = 10
        self.date_info_arr = []
        self.music_arr = []
        self.base_path = 'https://www.melodybrazil.com'
        self.log_text = ''
        self.updated_max = ''
        self.date_info_arr = json.load(open(f'{os.getcwd()}{os.sep}output{os.sep}date_info.json'))
        self.counter1 = 0

    def start_requests(self):
        # Iterando sobre o array de datas
        # Para cada objeto no date info, serão 10 músicas buscadas
        # Com execeção da 1º página onde 12 musicas serão buscadas
        for date_info in self.date_info_arr:
            self.page_num = date_info['page_num']
            if self.page_num > 1:
                self.base_path = f'https://www.melodybrazil.com/search?updated-max={date_info["updated_max"]}&max-results=10#PageNo={date_info["page_num"]}'
            yield scrapy.Request(self.base_path, callback=self.parse)

    def parse(self, response, **kwargs):
        list_posts = response.xpath('//div[@class="grid-posts"]/div').getall()
        print(f'Len do list posts {len(list_posts)}')
        inta = 0
        while inta < len(list_posts):
            music_title = ''
            music_box_xpath = f'//div[@class="grid-posts"]/div[contains(@class, "hentry") and contains(@class, "post-{inta}")]'
            tester = True
            try:
                music_title = response.xpath(f'{music_box_xpath}/div[@class="post-info"]/h2/a/text()').get()
            except:
                pass
            while tester:
                lst = [i for i, d in enumerate(self.music_arr) if music_title in d.values()]
                if not lst:
                    try:
                        music_url_publication = response.xpath(f'{music_box_xpath}/div[1]/a/@href').get()
                        music_image_url = response.xpath(f'{music_box_xpath}/div[1]/a/img/@src').get()
                        music_author = response.xpath(
                            f'{music_box_xpath}/div[@class="post-info"]/div[@class="post-meta"]/span[@class="post-author"]/a/text()').get()
                        if music_author == "Unknown":
                            music_author = "Autor Desconhecido"
                        music_date_published = response.xpath(
                            f'{music_box_xpath}/div[@class="post-info"]/div[@class="post-meta"]/span[contains(@class, "post-date") and contains(@class, "published")]/time/@datetime').get()
                        mus = Music_CD()
                        mus.set_title(music_title)
                        mus.set_url_publication(music_url_publication)
                        mus.set_author(music_author)
                        mus.set_url_publication(music_url_publication)
                        mus.set_image_url(music_image_url)
                        mus.set_publication_date(music_date_published)
                        try:
                            yield scrapy.Request(
                                url=response.urljoin(music_url_publication),
                                cb_kwargs={
                                    'mus': mus,
                                },
                                callback=self.parse_download_url,
                            )
                        except:
                            mus.set_download_url('Não foi possível coletar')
                            m_dict = mus.to_dict()
                            self.music_arr.append(m_dict)
                    except:
                        pass
                else:
                    tester = False
                    break
            self.actually_music_index += 1
            inta += 1
        self.counter1 += 1

    def parse_download_url(self, response, mus):
        boolea_already_getted = False
        base_xpath = '//div[@class="post-item-content"]//div[contains(@class, "post-body") and contains(@class,"post-content")]'
        down_xpath_one = f'{base_xpath}//a[contains(@onclick, "http")]/@onclick'
        down_xpath_two = f'{base_xpath}//div/a[contains(@href, "javascript")]/@onclick'
        down_xpath_three = f'{base_xpath}//center/a[contains(@href, "http")]/@href'
        down_xpath_four = f'{base_xpath}//div/a[contains(@href, "http")]/@href'

        music_download_url = ''
        try:
            music_download_url = response.xpath(f'{down_xpath_one} | {down_xpath_two}').get()
            try:
                array_of_broken = music_download_url.split('\'')
                for i in array_of_broken:
                    if re.match('http', i):
                        music_download_url = i
                        boolea_already_getted = True
            except:
                if not boolea_already_getted:
                    try:
                        print('exceptou')
                        music_download_url = response.xpath(f'{down_xpath_three} | {down_xpath_four}').get()
                        boolea_already_getted = True
                    except:
                        print('exceptou de novo')
                        pass
        except:
            print('nao existe nenhum desses xpath')
        try:
            if music_download_url == '':
                music_download_url = 'Não há link de download disponível'
            mus.set_download_url(music_download_url)
            m_dict = mus.to_dict()
            self.music_arr.append(m_dict)
        except:
            pass

    def spider_closed(self):
        def sorter_by_date(x):
            # 2024-03-07T13:16:00.002-03:00
            # %Y  -%M-%dT%H:%M:%S.%F -%z
            tz = 'America/Sao_Paulo'
            date_publi = datetime.datetime.fromisoformat(x['publication_date'])
            date_publi_sao_paulo = date_publi.astimezone(timezone(tz))
            new_date = date_publi_sao_paulo.strftime('%d/%m/%Y %H:%M:%S')
            x['publication_date'] = new_date
            return date_publi

        self.music_arr = sorted(self.music_arr, key=sorter_by_date, reverse=True)
        json_dt = json.dumps(self.music_arr, indent=4)
        with open(f'{os.getcwd()}{os.sep}output{os.sep}musics.json', 'w+', encoding="utf-8") as outp:
            outp.write(json_dt)
            outp.close()

        generate_excel_table()
