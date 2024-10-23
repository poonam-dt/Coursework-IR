import scrapy
import json
from collections import Counter


class PublicationSpider(scrapy.Spider):
    name = 'publication_csmd'
    allowed_domains = ['pureportal.coventry.ac.uk']
    start_urls = [
        'https://pureportal.coventry.ac.uk/en/organisations/research-centre-for-computational-science-and-mathematical-modell/publications',
        'https://pureportal.coventry.ac.uk/en/organisations/research-centre-for-computational-science-and-mathematical-modell/persons/'
    ]

    # initialize counters for staff and publications
    staff_counter = Counter()
    publication_counter = Counter()
    staff_counter_dep = Counter()

    def __init__(self, name=None, **kwargs):
        super().__init__(name)
        self.staff_link_counter_dep = Counter()
        self.publication_counter_selected = Counter()
        self.staff_counter_selected = Counter()
        self.publications_list = list()
        self.authors_list = list()
        self.authors_list_csm = list()
        self.authors_links_overall = list()

    def parse(self, response):
        # Check which website the response is from and call the appropriate method
        if "pureportal.coventry.ac.uk/en/organisations/research-centre-for-computational-science-and-mathematical-modell/publications" in response.url:
            yield from self.parse_allPublications(response)
        elif "https://pureportal.coventry.ac.uk/en/organisations/research-centre-for-computational-science-and-mathematical-modell/persons/" in response.url:
            yield from self.parse_department(response)

    def parse_allPublications(self, response):
        publications_list = list()
        authors_temp = list(

        )
        for publication in response.css('div.rendering_researchoutput'):
            # check if the publication is from the desired department
            if 'research-centre-for-computational-science-and-mathematical-modell' not in response.url:
                continue

            # extract publication details
            publication_title = publication.css('h3.title span::text').get()
            publication_link = publication.css('h3.title a::attr(href)').get()

            # skip publications with missing data
            if publication_title is None or publication_link is None:
                continue

            authors = publication.css('.person span::text').getall()
            author_links = publication.css('a.person::attr(href)').getall()
            publication_date = publication.css('.date::text').getall()
            publication_journal = publication.css('.journal span::text').getall()
            authors_links_temp = publication.css(
                ".rendering_researchoutput span:not(.date):not(.title):not(.type):not(.pages):not(.pages):not(.numberofpages):not(.link):not(.type_family):not(.type_family_sep):not(.type_classification_parent):not(.type_parent_sep):not(.type_classification):not(.journal):not(.volume):not(.edition):not(.journalnumber):not(.common_hidden)::text").getall()
            # remove duplicate authors and their links

            for authors_temp in authors_links_temp:
                if authors_temp not in publication_journal and authors_temp != 'IEEE':
                    self.authors_links_overall.append(authors_temp)

            authors_set = set(authors)
            author_links_set = set(author_links)

            for author in authors_set:
                self.staff_counter[author] += 1
                self.publication_counter[author] += 1

                # add the publication and author details to the list
            self.publications_list.append({
                'title': publication_title,
                'link': publication_link,
                'authors': list(authors_set),
                'author_links': list(author_links_set),
                'Publication Journal': publication_journal,
                'publication_date': publication_date
            })
            # yield the publication and author details
            yield {
                'title': publication_title,
                'link': publication_link,
                'authors': list(authors_set),
                'author_links': list(author_links_set),
                'Publication Journal': publication_journal,
                'publication_date': publication_date
            }
            # follow the next page link and call the parse method again
            next_page_link = response.css('.next a::attr(href)').get()
            if next_page_link is not None:
                yield response.follow(next_page_link, self.parse)

    def parse_department(self, response):
        for authors in response.css('div.rendering_person'):
            if 'research-centre-for-computational-science-and-mathematical-modell' not in response.url:
                continue
            author_names = authors.css('div.rendering_person a.person span::text').getall()
            author_links = authors.css('div.rendering_person a.person::attr(href)').getall()

            if author_links is None:
                continue
            authors_set_csm = set(zip(author_names, author_links))
            authors_list = []
            for i in range(len(author_names)):
                authors_dict = {'authors': author_names[i], 'authors_link': author_links[i]}
                authors_list.append(authors_dict)
                self.staff_counter_dep[author_names[i]] += 1
            self.authors_list.extend(authors_list)
            yield {
                'authors': author_names,
                'authors_link': author_links
            }

    def closed(self, reason):
        authors_dep = []
        for author in self.authors_list:
            authors_dep.append(author['authors_link'])

        # select csm publications
        selected_publications = []
        for publication in self.publications_list:
            for author_link in publication['author_links']:
                if author_link in authors_dep:
                    selected_publications.append(publication)
                    break  # Once a match is found, move to the next publication
        # select csm authors whose publication crawled
        selected_authors = []
        for publication in selected_publications:
            for i in range(len(publication['authors'])):
                author_link = publication['author_links'][i]
                if author_link in authors_dep:
                    author_name = publication['authors'][i]
                    # check if author_link is already present in selected_authors
                    if not any(d.get("author_link") == author_link for d in selected_authors):
                        selected_authors.append({'author_name': author_name, 'author_link': author_link})

        # loop over selected publications and add publication link and author links to corresponding publication in publications list
        publications_csm = []
        current_publication = None
        for item in self.authors_links_overall:
            if item in [publication['title'] for publication in selected_publications]:
                current_publication = {'title': item, 'authors': [], 'publication_link': None, 'authors_link': None,
                                       'publication_date': None}
                publications_csm.append(current_publication)
            elif item not in [publication['title'] for publication in selected_publications]:
                current_publication['authors'].append(item)
                # check if this publication is in selected_publications
                selected_pub = next(
                    (pub for pub in selected_publications if pub['title'] == current_publication['title']), None)
                if selected_pub:
                    current_publication['publication_link'] = selected_pub['link']
                    current_publication['authors_link'] = selected_pub['author_links']
                    current_publication['publication_date'] = selected_pub['publication_date']
        print(len(publications_csm))
        # Write the author information to a JSON file
        with open("publications_csm.json", "w") as f:
            json.dump(publications_csm, f)
        # print the total number of staff and the number of publications per author
        print(f"Total number of publications have been crawled: {len(self.publications_list)}")
        print(f"Total number of person whose publications have been crawled: {len(self.staff_counter)}")
        print(f"number of staff in CSM:{len(self.staff_counter_dep)}")
        print(f"Number of publications by csm authors: {len(publications_csm)}")
        print(f"Number of CSM authors whose publication crawled: {len(selected_authors)}")
        # Show publications per authors
        # create a dictionary to keep track of the publication count for each author
        publications_per_author = {}
        # count the publications for each selected author
        for publication in selected_publications:
            for author_link in publication['author_links']:
                if author_link in [author['author_link'] for author in selected_authors]:
                    if author_link in publications_per_author:
                        publications_per_author[author_link] += 1
                    else:
                        publications_per_author[author_link] = 1

        author_data = list()
        for author_link, publication_count in publications_per_author.items():
            # get the author's name from self.authors_list
            author_name = next(
                (author['authors'] for author in self.authors_list if author['authors_link'] == author_link), None)
            if author_name:
                author_data.append(
                    {'Author name': author_name, 'Author link': author_link, 'Publication count': publication_count})
                print(f"Author name: {author_name}, Author link: {author_link}, Publication count: {publication_count}")
            else:
                print(f"Author link: {author_link}, Publication count: {publication_count}")
        # Write the author information to a JSON file
        with open("author_info.json", "w") as f:
            json.dump(author_data, f)
