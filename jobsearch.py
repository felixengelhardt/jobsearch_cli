import logging
from urllib import request

import untangle
from bs4 import BeautifulSoup
from fabulous.color import bold


logging.basicConfig(level=logging.INFO)


class jobSearch:

    def __init__(self):
        self.config = untangle.parse("config.xml")
        self.engines = {}
        for engine in self.config.jobsearch.engines.engine:
            self.engines[engine['name']] = engine
        self.search_queries_default = {}
        for query in self.config.jobsearch.searchterms.searchterm:
            self.search_queries_default[query['name']] = query.cdata

    def create_queries(self, search_queries_dict=None):
        if search_queries_dict is None:
            search_queries_dict = self.search_queries_default
        queries_url_dict = {}
        for engine in self.engines:
            query = self.engines[engine].cdata \
                    + self.engines[engine]['query'] + search_queries_dict['jobtitle'] \
                    + "&" + self.engines[engine]['location'] + search_queries_dict['location'] \
                    + "&" + self.engines[engine]['radius'] + search_queries_dict['radius']
            queries_url_dict[self.engines[engine]['name']] = query
            logging.debug(query)
        return queries_url_dict

    def request_page(self, url):
        page = request.urlopen(url)
        return page

    def parse_page(self, page, engine):
        bspage = BeautifulSoup(page, 'lxml')
        if engine == 'monster':
            titles = [title.get_text().strip() for title in bspage.find_all('h2', class_='title')]
            logging.debug(len(titles))
            companies = [company.get_text().strip() for company in bspage.find_all('div', class_='company')]
            logging.debug(len(companies))
            urls = [title.find('a', href=True)['href'] for title in bspage.find_all('h2', class_='title')]
            logging.debug(len(urls))
        if engine == 'indeed':
            titles = [title.get_text().strip() for title in bspage.find_all('div', class_='title')]
            logging.debug(len(titles))
            companies = [company.get_text().strip() for company in bspage.find_all('span', class_='company')]
            logging.debug(len(companies))
            urls = ['http://www.indeed.de{}'.format(title.find('a', href=True)['href']) for title in
                    bspage.find_all('div', class_='title')]
            logging.debug(len(urls))
        if engine == 'stepstone':
            titles = [title.get_text().strip() for title in
                      bspage.find_all('div', class_='styled__JobItemFirstLineWrapper-sc-11l5pt9-2 dwJxVv')]
            logging.debug(len(titles))
            companies = [company.get_text().strip() for company in
                         bspage.find_all('div', class_="styled__CompanyName-iq4jvn-0 gakwWs")]
            logging.debug(len(companies))
            urls = ['http://www.stepstone.de{}'.format(title.find('a', href=True)['href']) for title in
                    bspage.find_all('div', class_='styled__JobItemFirstLineWrapper-sc-11l5pt9-2 dwJxVv')]
            logging.debug(len(urls))
        results_list = list(zip(titles, companies, urls))
        return results_list

    def print_results(self, result_list, engine="default"):
        print('{}:'.format(bold(engine)))
        for title, company, url in result_list:
            print('{}'.format(bold(title)))
            print('{}'.format(company))
            print('{}\n'.format(url))

def main():
    jobs = jobSearch()
    queries_dict = jobs.create_queries()
    for engine in queries_dict:
        page = jobs.request_page(queries_dict[engine])
        results = jobs.parse_page(page, engine)
        jobs.print_results(results,engine=engine)


if __name__ == "__main__":
    main()