import os
from scrapy import Request
from scrapy.spiders import CrawlSpider
from searchEnginePublications_copy.searchEnginePublications.spiders.crawler_publications import *
from scrapy.crawler import CrawlerProcess


class PublicationSpider_1(CrawlSpider):
    name = 'publication_abstract'
    allowed_domains = ['pureportal.coventry.ac.uk']
    publication_final = list()

    def start_requests(self):
        with open(r'/searchEnginePublications/publications_csm.json', 'r',
                  encoding='utf-8') as f:
            data = json.load(f)
            for publication in data:
                yield Request(publication['publication_link'], self.parse, meta={'publication': publication})

    def parse(self, response):
        publication = response.meta['publication']
        title = response.css('.rendering h1 span::text').getall()
        publication_link = response.url
        abstract = response.css('.textblock::text').getall()
        keywords = response.css('.concept::text').getall()
        authors_name = publication['authors']
        authors_links = publication['authors_link']
        publication_date = publication['publication_date']
        self.publication_final.append({
            'publication_title': title,
            'publication_link': publication_link,
            'abstract': abstract,
            'keywords': keywords,
            'authors_name': authors_name,
            'authors_links': authors_links,
            'publication_date': publication_date
        })
        yield {
            'title': title,
            'publication_link': publication_link,
            'abstract': abstract,
            'Keywords': keywords,
            'authors_name': authors_name,
            'authors_links': authors_links,
            'publication_date': publication_date
        }


if os.path.exists('documents.json'):
    os.remove('documents.json')

if os.path.exists('update.json'):
    os.remove('update.json')

begin = CrawlerProcess(settings={
    'FEED_URI': 'documents.json',
    'FEED_FORMAT': 'json',
    'FEED_EXPORT_TRUNCATE': True
})

update = CrawlerProcess(settings={
    'FEED_URI': 'update.json',
    'FEED_FORMAT': 'json',
    'FEED_EXPORT_TRUNCATE': True
})
