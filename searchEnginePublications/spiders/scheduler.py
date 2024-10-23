#Importing Libraries
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from searchEnginePublications_copy.searchEnginePublications.spiders.crawler_publications import PublicationSpider
from searchEnginePublications_copy.searchEnginePublications.spiders.publications_abstract import PublicationSpider_1
from scrapy.settings import Settings
import logging
from datetime import datetime, timedelta


def schedule_spiders():
    #setting = get_project_settings()
    settings = Settings()
    settings.setmodule("searchEnginePublications.searchEnginePublications.settings")
    runner = CrawlerRunner(settings)
    spiders = [PublicationSpider, PublicationSpider_1]  # taking both spiders

    # Schedule first spider
    d = runner.crawl(spiders[0])
    d.addCallback(lambda _: runner.crawl(spiders[1]))  # Schedule second spider after first spider completes

    # Schedule next run on 6 PM
    next_day = (datetime.now() + timedelta(days=(4 - datetime.now().weekday()) % 7))  # Find the next run
    next_run = datetime(next_day.year, next_day.month, next_day.day, hour=18)  # Set the time for 6 PM
    days_until_next_run = (
                next_run - datetime.now()).days  # Calculate the number of days until next run

    seconds_until_next_run = (
            next_run - datetime.now()).total_seconds()  # Calculate the number of seconds
    print(f"Next run in {days_until_next_run} days, on {next_run.strftime('%Y-%m-%d')}")

    with open("log.txt", "a") as f:
        f.write(
            f"Last crawled: {datetime.now().strftime('%Y-%m-%d')}, Next crawl: {next_run.strftime('%Y-%m-%d')}\n")
    reactor.callLater(seconds_until_next_run, schedule_spiders)


def catch_error(failure):
    logging.error(failure.getTraceback())
    print(f"Error: {failure.getErrorMessage()}")

if __name__=="__main__":
    schedule_spiders()
    reactor.run()