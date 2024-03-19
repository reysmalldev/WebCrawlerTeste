import re
from typing import Any
import scrapy
import json
from scrapy import signals
from pydispatch import dispatcher
import os
import sys

sys.path.append(os.getcwd())
from utils.cd_music import Music_CD


class GetAllMusicsPage(scrapy.Spider):
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
        self.page_num = 1
        self.actually_music_index = 1
        self.max_results = 10
        self.musics_per_page = 10
        self.date_info_arr = []
        self.music_arr = []
        self.base_path = 'https://www.melodybrazil.com'
        # self.max_music_number = 2964  # se você trocar o valor máximo de músicas no site o programa se limitará (ou ampliará seu alcance) a
        # tal número de músicas para coleta.
        self.log_text = ''
        self.parse_selector_is_one = True
        self.counter_individual_requests_array = 0
        self.updated_max = ''
        self.can_repeat = True
        self.date_info_arr = json.load(open(f'{os.getcwd()}{os.sep}output{os.sep}date_info.json'))

    def start_requests(self):

        print(f'a len é {len(self.date_info_arr)}')
        # Iterando sobre o array de datas
        # Para cada objeto no date info, serão 10 músicas buscasdas
        # Com execeção da 1º página onde 12 musicas serão buscadas
        # date_info = self.date_info_arr[0]
        for date_info in self.date_info_arr:
            self.page_num = date_info['page_num']
            print(f'estamos {self.page_num}')
            if self.page_num > 1:
                self.base_path = f'https://www.melodybrazil.com/search?updated-max={date_info["updated_max"]}&max-results=10#PageNo={date_info["page_num"]}'
            yield scrapy.Request(self.base_path, callback=self.parse)
            print('m')

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
                        mus = Music_CD(title=music_title, author=music_author, image_url=music_image_url,
                                       publication_date=music_date_published, url_publication=music_url_publication)
                        m_dict = mus.to_dict()
                        self.music_arr.append(m_dict)
                    except:
                        pass
                else:
                    tester = False
                    break
            self.actually_music_index += 1
            inta += 1

    def spider_closed(self):
        json_dt = json.dumps(self.music_arr, indent=4)
        with open(f'{os.getcwd()}{os.sep}output{os.sep}musics.json', 'w+', encoding="utf-8") as outp:
            outp.write(json_dt)
            outp.close()
