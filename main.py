from typing import Iterable, Any
import scrapy
import re
import pandas as pd
import json
from scrapy import signals
from pydispatch import dispatcher
import sys
import os
import datetime
import time
import numpy as np
from pytz import timezone
from styleframe import StyleFrame, Styler, utils
def generateExcelTable():
    df = pd.read_json(f"{os.getcwd()}{os.sep}output{os.sep}musics.json")
    df = df.rename(columns={
        'title': 'Título',
        'image_url': 'Link da Imagem',
        'author': 'Autor',
        'publication_date': 'Data da Publicação',
        'download_url': 'Link de Download'
    })
    writer = StyleFrame.ExcelWriter(f"{os.getcwd()}{os.sep}output{os.sep}cds_melody_brasil.xlsx")

    sf = StyleFrame(df)

    sf.set_column_width('Título', 55)
    sf.set_column_width('Link da Imagem', 65)
    sf.set_column_width('Autor', 40)
    sf.set_column_width('Data da Publicação', 50)
    sf.set_column_width('Link de Download', 80)

    sf.apply_column_style(cols_to_style=df.columns,
                          styler_obj=Styler(bg_color=utils.colors.white, bold=False, font=utils.fonts.arial,
                                            font_size=12), style_header=True, )
    sf.apply_column_style(cols_to_style=['Link da Imagem', 'Link de Download'],
                          styler_obj=Styler(font_color=utils.colors.blue, font_size=10))
    sf.apply_headers_style(styler_obj=Styler(font_size=14, bold=True, font=utils.fonts.arial))

    sf.to_excel(writer, sheet_name='Sheet1')
    writer.close()


class Music_CD:
    def __init__(self, image_url, title, author, publication_date, download_url):
        self.image_url = image_url
        self.title = title

        self.publication_date = publication_date
        self.download_url = download_url
        if author != "Unknown":
            self.author = author
        else:
            self.author = 'Autor Desconhecido'
        self.publication_date = publication_date
        # try:
        #     #  2024-03-08T11:11:00.001-03:00
        #     #  %H  -%M-%ST%H:%M:%S.%F-%z
        #     time_object =
        #     #'2024-03-08T11:11:00.001-03:00
        #     time_object = datetime.time.fromisoformat(publication_date)
        #     print(time_object)
        #     data = publication_date.split('T')
        #     data1 = data[0].split('-')
        #     self.publication_date = time_object
        #     # self.publication_date = f'{data1[2]}/{data1[1]}/{data1[0]}'
        # except:
        #

    def to_dict(self):
        return {
            'title': self.title,
            'image_url': self.image_url,
            'author': self.author,
            'publication_date': self.publication_date,
            'download_url': self.download_url
        }

    def from_json(self, json_data):
        self.title = json_data['title']
        self.image_url = json_data|['image_url']
        self.author = json_data['author']
        self.publication_date = json_data['publication_date']
        self.download_url = json_data['download_url']


class MelodyBrasilMusics(scrapy.Spider):
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
        self.post_results = 10  # todas as páginas do site só retornam 10 músicas no máximo
        self.json_start = (self.page_num - 1) * self.post_results
        self.base_url = 'https://www.melodybrazil.com/feeds/posts/summary?start-index=1&max-results=10&alt=json-in-script&callback=dataFeed'
        self.music_arr = []
        self.music_dic = {}
        self.max_music_number = 2964  # se você trocar o valor máximo de músicas no site o programa se limitará (ou ampliará seu alcance) a
        # tal número de músicas para coleta.
        self.log_text = ''

    def start_requests(self):
        print(f'entrou e o minimo {self.page_num}')
        while self.page_num <= self.max_music_number:
            if self.page_num != 1:
                print(f'page_num: {self.page_num}')
                # page_num = 2964, então (2964 - 1) * 10 = 2963 *10 = 29630
                self.base_url = f'https://www.melodybrazil.com/feeds/posts/summary?start-index={(self.page_num - 1) * 10}&max-results=10&alt=json-in-script&callback=dataFeed'
            self.log_text += self.base_url + '\n'
            yield scrapy.Request(self.base_url, self.parse)
            self.page_num += 1
            time.sleep(0.10)

    def parse(self, response, **kwargs):
        text_of_response = response.text
        # print(text_of_response)
        text_of_response = re.findall(r'\{.+}', text_of_response)

        for r in text_of_response:
            jsonob = json.loads(r)
            with open(f'{os.getcwd()}{os.sep}page2888.json', 'w+') as test:
                test.write(json.dumps(jsonob, indent=4))
            # print(jsonob)
            list_of_entrys = jsonob["feed"]["entry"]
            self.music_dic.update({f'{self.page_num}': list_of_entrys})
            cout = 0
            while cout < len(list_of_entrys):
                try:
                    image_url = list_of_entrys[cout]["media$thumbnail"]["url"]
                except:
                    image_url = "https://static.mytuner.mobi/media/tvos_radios/enwr9jglhqxn.jpg"
                    pass
                title = list_of_entrys[cout]["title"]["$t"]
                author = list_of_entrys[cout]["author"][0]["name"]["$t"]
                publication_date = list_of_entrys[cout]["published"]["$t"]
                download_url = ''
                list_of_links = list_of_entrys[cout]["link"]

                for i in list_of_links:
                    try:
                        if i["title"] == title:
                            download_url = i["href"]
                    except:
                        pass
                m = Music_CD(image_url, title, author, publication_date, download_url)
                m_dict = m.to_dict()
                self.music_arr.append(m_dict)

                cout += 1

    def spider_closed(self):
        def sorter_by_date(x):
            tz = 'America/Sao_Paulo'
            date_publi = datetime.datetime.strptime(x["publication_date"], '%Y-%m-%dT%H:%M:%S.%f%z')
            date_publi_sao_paulo = date_publi.astimezone(timezone(tz))
            new_date = date_publi_sao_paulo.strftime('%d/%m/%Y %H:%M:%S')
            x['publication_date'] = new_date
            return date_publi

        # 2024-03-07T13:16:00.002-03:00
        # %Y  -%M-%dT%H:%M:%S.%F -%z
        self.music_arr = sorted(self.music_arr, key=sorter_by_date, reverse=True)
        time.sleep(1)
        json_dt = json.dumps(self.music_arr, indent=4)
        with open(f'{os.getcwd()}{os.sep}output{os.sep}musics.json', 'w+') as outp:
            outp.write(json_dt)
            outp.close()
        with open(f'{os.getcwd()}{os.sep}output{os.sep}logger.text', 'w+') as outpa:
            outpa.write(self.log_text)
            outpa.close()
        generateExcelTable()
