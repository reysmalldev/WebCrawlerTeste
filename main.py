from typing import Iterable, Any

import scrapy
import json
import os
import sys

class Music_CD:
    def __init__(self, image_url, title, author, publication_date, download_url):
        self.image_url = image_url
        self.title = title
        self.author = author
        self.publication_date = publication_date
        self.download_url = download_url

    def to_dict(self):
        return {
            'title': self.title,
            'image_url': self.image_url,
            'author': self.author,
            'publication_date': self.publication_date,
            'download_url': self.download_url
        }

class MelodyBrasilMusics(scrapy.Spider):
    name = 'melody'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'AUTOTHROTTLE': True
    }
    count = 0  # deve ir ate 2963

    def start_requests(self):
        base = 'https://www.melodybrazil.com/'
        yield scrapy.Request(base)

    def parse(self, response, **kwargs):
        grid_of_musics = response.xpath('//div[@class="grid-posts"]/div')
        list_of_musics = []
        for music in grid_of_musics:
            image_url = music.xpath('//div[@class="grid-posts"]/div/div/a/img/@src').get()
            title = music.xpath('//div[@class="grid-posts"]/div/div[@class="post-info"]/h2/a/text()').get()
            author = music.xpath('//div[@class="grid-posts"]/div/div[@class="post-info"]/div[@class="post-meta"]/span[@class="post-author"]/text()').get()
            publication_date = music.xpath('//div[@class="grid-posts"]/div/div[@class="post-info"]/div[@class="post-meta"]/span[contains(@class, "post-date") and contains(@class, "published")]/time/text()').get().strip()
            download_url = music.xpath('//div[@class="grid-posts"]/div/div[@class="post-info"]/h2/a/@href').get()
            m = Music_CD(image_url, title, author, publication_date, download_url)
            m_dict = m.to_dict()
            list_of_musics.append(m_dict)
            # print(m_dict)

          # @class="post-date published"
        json_object = json.dumps(list_of_musics, indent=4)
        # Writing to sample.json
        with open(f"{os.getcwd()}{os.sep}extracted{os.sep}data.json", "w+") as outfile:
            outfile.write(json_object)
