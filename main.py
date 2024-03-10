from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrappers.scrapper import MelodyBrasilMusics
from scrappers.individual_cd import CorrectAuthorName

settings = get_project_settings()
configure_logging(settings)
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(MelodyBrasilMusics)
    yield runner.crawl(CorrectAuthorName)
    reactor.stop()

crawl()
reactor.run()
