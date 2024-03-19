import logging
class Music_CD:
    def __init__(self, image_url, title, author, publication_date, url_publication):
        self.image_url = image_url
        self.title = title
        self.url_publication = url_publication
        self.publication_date = publication_date
        self.download_url = ''
        if author != "Unknown" or author != '':
            self.author = author
        else:
            self.author = 'Autor Desconhecido'
        self.publication_date = publication_date
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)

    def set_download_url(self, download_url):
        self.download_url = download_url

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
        self.image_url = json_data | ['image_url']
        self.author = json_data['author']
        self.publication_date = json_data['publication_date']
        self.download_url = json_data['download_url']
        self.url_publication = json_data['url_publicacao']
