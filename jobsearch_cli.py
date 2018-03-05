from urllib import request
from bs4 import BeautifulSoup
from pathlib import Path
import numpy as np
import re
import os
import itertools
import sys
import logging
import argparse

engineUrls = {
    'monster': 'https://www.monster.de/jobs/suche/?q={}&where={}&cy=de&rad={}&sort=dt.rv.di&page=1',
    'indeed': 'https://de.indeed.com/Jobs?as_and={}&as_phr=&as_any=&as_not=&as_ttl=&as_cmp=&st=&l={}&radius={}&fromage=&limit=&sort=&psf=advsrch',
    'stepstone': 'https://www.stepstone.de/5/ergebnisliste.html?stf=freeText&ns=1&qs=%5B%5D&companyID=0&cityID=0&sourceOfTheSearchField=homepagemex%3Ageneral&searchOrigin=Homepage_top-search&ke={}&ws={}&ra={}'}

getTags = {
    'monster': [('div', 'jobTitle'), ('div', 'company'), ('div', 'job-specs job-specs-location')],
    'stepstone': [('h2', 'job-element__body__title'),
        ('div', 'job-element__body__company'),
        ('li', 'job-element__body__location')]} # Stepstone URL ', ('a', 'job-element__url')'

logging.basicConfig( level=logging.WARN) #filename='jobsearch.log',

def getIndeedJobs(bs4Page):
    title = []
    company = []
    city = []
    url = []
    indeedDict = {
        'title' : [],
        'cmp' : [],
        'city' : [],
        'jk' : []
    }
    jobs= []
    try:
        indeed = bs4Page.find('script', text=re.compile('jobmap')).text
        indeedJobs = re.findall('jobmap\[.*\].*=.*\{.*\}', indeed)
        indeedJobs = [ re.sub('\}','',re.sub('jobmap\[.*\].*=.*\{','',job)).split(',') for job in indeedJobs ]
        #indeedJobs = [ re.sub('\}','',job) for job in indeedJobs ]
        #indeedJobs = [ job.split(',') for job in indeedJobs ]
        for entry in itertools.chain.from_iterable(indeedJobs):
            for key in ['title', 'cmp', 'city', 'jk']:
                if re.match('^{}:'.format(key),entry):
                    indeedDict[key].append(entry.split(':')[1].strip("'"))
        jobs = [x for x in indeedDict.values()]
        logging.debug(jobs)
        return jobs 
    except AttributeError:
        print('Something went wrong. There are no jobs here.\n')
        pass

def getJobs(engine, jobname, location, radius):
    print('Checking for jobs on {}:\n'.format(engine))
    logging.debug('Input für Funktion getJobs {} {} {} {}'.format(engine, jobname, location, radius))            
    page = request.urlopen(engineUrls[engine].format(jobname, location, radius))
    bs4Page = BeautifulSoup(page, 'lxml')
    jobs = []
    if engine == 'stepstone':
        test = bs4Page.find_all('a', class_='job-element__url', href=True)
        logging.debug([x.get('href') for x in test])
    #
    # bs4 gets indeed non-premium job ads as javascript snippet 
    # therefore special treatment is necessary
    #
    if engine == 'indeed':
        jobs = getIndeedJobs(bs4Page)
    else:
        for entry in getTags[engine]:
            jobs.append([x.get_text().strip() for x in bs4Page.find_all(entry[0],
                class_=entry[1])])
    jobs = np.array(jobs).T.tolist()
    return jobs


def main(engines, jobname, location, radius):
    engines = engines.strip().split(',')
    if 'all' in engines:
        engines = ['monster', 'indeed', 'stepstone']
    jobs = {}
    for engine in engines:
        jobs[engine] = getJobs(engine, jobname, location, radius)
        for job in jobs[engine][0:9]:
            print(u'Job Title: {}\nCompany: {}\nLocation: {}\n'.format(job[0], job[1], job[2]))


if __name__ == '__main__':
    homedir = Path.home()
    if os.path.isfile('{}/.jobsearch_cli'.format(homedir)):
        f = open('{}/.jobsearch_cli'.format(homedir),'r')
        jobTitle = f.readline().split('=')[1].strip()
        location = f.readline().split('=')[1].strip()
        radius = f.readline().split('=')[1].strip()
        logging.debug('{} {} {}'.format(jobTitle, location, radius))
        f.close()        
    else:
        print('No config with defaults found. Please enter your default search queries')
        title = input('Please enter job title: ')
        location = input('Please enter location: ')
        radius = input('Please enter radius around location which is acceptable: ')
        f = open('{}/.jobsearch_cli'.format(homedir),'w')
        f.write('title={}\nlocation={}\nradius={}'.format(title, location, radius))
        f.close()
        sys.exit()
    parser = argparse.ArgumentParser(description='Jobsearch on the Commandline\
        with Python.')
    parser.add_argument(
        '-j', '--jobTitle', help='Title of the job you are looking for', default='{}'.format(jobTitle))
    parser.add_argument(
        '-l', '--location', help='Location you want to your job to be', default='{}'.format(location))
    parser.add_argument(
        '-r', '--radius', help='Search radius around entered location', default='{}'.format(radius))
    parser.add_argument(
        '-e', '--engine', help='Set the job search engine. Default value is \
        all, valid values monster, indeed, stepstone, all. Use a comma to \
        seperate engines',
        default='all')
    args = parser.parse_args()
    logging.debug('Suchkriterien: {} {} {} {}'.format(args.engine, args.jobTitle, args.location, args.radius))
    main(args.engine, args.jobTitle, args.location, args.radius)
