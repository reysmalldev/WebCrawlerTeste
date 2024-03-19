import logging


class Music_CD:
    def __init__(self):
        self.title = ''
        self.image_url = ''
        self.author = ''
        self.url_publication = ''
        self.publication_date = ''
        self.download_url = ''

    def set_download_url(self, download_url):
        self.download_url = download_url

    def set_author(self, author):
        if author != "Unknown" or author != '':
            self.author = author
        else:
            self.author = 'Autor Desconhecido'

    def set_publication_date(self, publication_date):
        self.publication_date = publication_date

    def set_title(self, title):
        self.title = title

    def set_url_publication(self, url_publication):
        self.url_publication = url_publication
    def set_image_url(self, image_url):
        self.image_url = image_url
    def to_dict(self):
        return {
            'title': self.title,
            'author': self.author,
            'publication_date': self.publication_date,
            'url_publication': self.url_publication,
            'download_url': self.download_url,
            'image_url': self.image_url,
        }

    def from_json(self, json_data):
        self.title = json_data['title']
        self.image_url = json_data['image_url']
        self.author = json_data['author']
        self.publication_date = json_data['publication_date']
        self.download_url = json_data['download_url']
        self.url_publication = json_data['url_publication']
