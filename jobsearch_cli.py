from urllib import request
from bs4 import BeautifulSoup
from pathlib import Path
import numpy as np
import json
import re
import os
import ast
import pydoc
import itertools
import logging
import argparse

def getIndeedJobs(bs4Page):
    #
    # bs4 gets indeed non-premium job ads as javascript snippet
    # therefore special treatment is necessary
    #
    indeedDict = {
        'title': [],
        'cmp': [],
        'city': [],
        'jk': []
    }
    jobs = []
    try:
        indeed = bs4Page.find('script', text=re.compile('jobmap')).text
        indeedJobs = re.findall('jobmap\[.*\].*=.*\{.*\}', indeed)
        indeedJobs = [ re.sub('jobmap\[.*\].*=.*\{','',job) for job in indeedJobs ]
        indeedJobs = [ re.sub('\}','', job) for job in indeedJobs ]
        indeedJobs = [ job.split(',') for job in indeedJobs ]
        for entry in itertools.chain.from_iterable(indeedJobs):
            if entry.split(':')[0] in getTags['indeed']:
                 indeedDict[entry.split(':')[0]].append(entry.split(':')[1].strip("'"))
        jobs = [x for x in indeedDict.values()]
        logging.debug(jobs)
        return jobs
    except AttributeError:
        print('Something went wrong. There are no jobs here.\n')
        return None


def getJobs(engine, config, jobname, location, radius):
    print('Checking for jobs on {}:'.format(engine))
    logging.debug('Input für Funktion getJobs {} {} {} {}'.format(engine, jobname, location, radius))
    logging.debug(config['engineURL'][engine].format(jobname, location, radius))
    page = request.urlopen(config['engineURL'][engine].format(jobname, location, radius))
    bs4Page = BeautifulSoup(page, 'lxml')
    jobs = []
    #
    # Not yet used
    #
    #if engine == 'stepstone':
    #    test = bs4Page.find_all('a', class_='job-element__url', href=True)
    #    logging.debug([x.get('href') for x in test])
    if engine == 'indeed':
        jobs = getIndeedJobs(bs4Page)
        if jobs is None:
            jobs = []
    else:
        logging.debug(ast.literal_eval(config['searchTags'][engine]))
        for entry in ast.literal_eval(config['searchTags'][engine]):
            jobs.append([x.get_text().strip() for x in bs4Page.find_all(entry[0],
                class_=entry[1])])
    jobs = np.array(jobs).T.tolist()
    return jobs

def getConfig(homedir):
    f = open('{}/config.json'.format(homedir), 'r')
    configFile = f.read()
    f.close()
    configJson = json.loads(configFile)
    logging.debug(configJson)
    return configJson


def main(engines, jobname, location, radius, config):
    engines = engines.strip().split(',')
    if 'all' in engines:
        engines = ['monster', 'indeed', 'stepstone']
    jobs = {}
    for engine in engines:
        logging.debug(config['engineURL'][engine])
        jobs[engine] = getJobs(engine, config, jobname, location, radius)
    return jobs

if __name__ == '__main__':
    config = getConfig(Path.home())
    parser = argparse.ArgumentParser(description='Jobsearch on the Commandline\
        with Python.')
    parser.add_argument(
        '-j', '--jobTitle', help='Title of the job you are looking for', default='{}'.format(config['title']))
    parser.add_argument(
        '-l', '--location', help='Location you want to your job to be', default='{}'.format(config['location']))
    parser.add_argument(
        '-r', '--radius', help='Search radius around entered location', default='{}'.format(config['radius']))
    parser.add_argument(
        '-e', '--engine', help="""Set the job search engine. Default value is
        all, valid values monster, indeed, stepstone, all. Use a comma to
        seperate engines""",
        default='all')
    args = parser.parse_args()
    logging.debug('Suchkriterien: {} {} {} {}'.format(args.engine, args.jobTitle, args.location, args.radius))
    jobs = main(args.engine, args.jobTitle, args.location, args.radius, config)
    engines = jobs.keys()
    output = ''
    for engine in engines:
        output = output + 'The following jobs were found on {}.de\n\n'.format(engine)
        for job in jobs[engine]:
            output = output + 'Job Title: {}\nCompany: {}\nLocation: {}\n\n'.format(job[0],job[1],job[2])
        output = output + '------------------------------------------------\n\n'
    pydoc.pager(output)
