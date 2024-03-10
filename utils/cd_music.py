import logging
class Music_CD:
    def __init__(self, image_url, title, author, publication_date, download_url):
        self.image_url = image_url
        self.title = title

        self.publication_date = publication_date
        self.download_url = download_url
        if author != "Unknown" or author != '':
            self.author = author
        else:
            self.author = 'Autor Desconhecido'
        self.publication_date = publication_date
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)

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
        self.image_url = json_data | ['image_url']
        self.author = json_data['author']
        self.publication_date = json_data['publication_date']
        self.download_url = json_data['download_url']
