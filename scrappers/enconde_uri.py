import re
from requests.utils import quote
from typing import Any
import scrapy
import json
from scrapy import signals
from pydispatch import dispatcher
import os
import sys

sys.path.append(os.getcwd())
from utils.date_infor import DateInfor


class GetDatesOfUrl(scrapy.Spider):
    name = 'melody'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'AUTOTHROTTLE': True,
        'DOWNLOAD_DELAY': 0.5,
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
        self.base_path = 'https://www.melodybrazil.com/feeds/posts/summary?start-index=1&max-results=10&alt=json-in-script&callback=findPostDate'
        # self.max_music_number = 2964  # se você trocar o valor máximo de músicas no site o programa se limitará (ou ampliará seu alcance) a
        # tal número de músicas para coleta.
        self.log_text = ''
        self.parse_selector_is_one = True
        self.counter_individual_requests_array = 0
        self.updated_max = ''
        self.can_repeat = True

    def start_requests(self):
        while self.page_num < self.max_results and self.can_repeat:
            if self.page_num > 1:
                self.base_path = f'https://www.melodybrazil.com/feeds/posts/summary?start-index={(self.page_num - 1) * self.musics_per_page}&max-results={self.musics_per_page}&alt=json-in-script&callback=findPostDate'
            yield scrapy.Request(self.base_path, self.parse)

    def parse(self, response, **kwargs):
        text_of = response.text
        text_of = re.findall(r'\{.+}', text_of)
        text_of_response = json.loads(str(text_of[0]))
        if 'feed' in text_of_response:
            try:
                entrys = text_of_response['feed']['entry']
                self.updated_max = entrys[0]['published']['$t']
                ref = self.updated_max[0:19] + self.updated_max[23:29]
                ref = quote(ref)

                dt_info = DateInfor(page_num=self.page_num, datetime=self.updated_max, max_res=10, start_index=1,
                                    updated_max=ref)
                self.date_info_arr.append(dt_info.to_dict())

                self.max_results = int(text_of_response['feed']['openSearch$totalResults']['$t'])
            except:
                self.can_repeat = False
        else:
            pass
        self.page_num += 1

    def spider_closed(self):
        json_dt = json.dumps(self.date_info_arr, indent=4)
        with open(f'{os.getcwd()}{os.sep}output{os.sep}date_info.json', 'w+', encoding="utf-8") as outp:
            outp.write(json_dt)
            outp.close()