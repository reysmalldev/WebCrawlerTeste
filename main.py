import time
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrappers.enconde_uri import GetDatesOfUrl
from scrappers.get_pages import GetAllMusicsPage

settings = get_project_settings()
configure_logging(settings)
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(GetDatesOfUrl)
    time.sleep(1)
    yield runner.crawl(GetAllMusicsPage)
    reactor.stop()

crawl()
reactor.run()
