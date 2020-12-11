import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy import crawler
from twisted.internet import reactor
from multiprocessing import Process
import json
import requests
from time import sleep
import os
import random
from urllib.request import urlopen
from spiders.nulearn import NulearnSpider
from spiders.talentedge import TalentEdgeSpider
from spiders.hughes import HughesSpider
from spiders.eduonix import EduonixSpider
from dotenv import load_dotenv, find_dotenv
import traceback

USER_AGENTS = [
    ('Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/57.0.2987.110 '
        'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.79 '
        'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
        'Gecko/20100101 '
        'Firefox/55.0'),  # firefox
    ('Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.91 '
        'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/62.0.3202.89 '
        'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/63.0.3239.108 '
        'Safari/537.36'),  # chrome
]
load_dotenv(find_dotenv())


class URLParsing():
    url_parse = 'https://talentedge.com/mica/marketing-brand-management-course/'

    def add(self, url):
        self.url_parse = url

    def geturl(self):
        return self.url_parse


sentURL = URLParsing()


def returnResponse(res):
    return {
        "statusCode": 200,
        "body": res,
        "headers": {
            'Content-Type': 'application/json',
        }
    }


def selectCrawler(option):
    list_of_crawlers = {
        'nulearn': NulearnSpider,
        'talentedge': TalentEdgeSpider,
        'hughes': HughesSpider,
        'eduonix': EduonixSpider
    }
    return list_of_crawlers.get(option, TalentEdgeSpider)


def getAllCourseUrls(baseUrl, import_source, check_array=[],course_type='course'):
    print("process started")
    try:
        runner = crawler.CrawlerRunner()
        if(import_source == 'eduonix'):
            runner.crawl(selectCrawler(import_source),
                         urls=baseUrl, array=check_array,course_type=course_type)
        else:
            runner.crawl(selectCrawler(import_source), urls=baseUrl)
        deferred = runner.join()
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
    except Exception as e:
        print("error")


def spider_handler(urls, import_source, start=None, stop=None, course_type='course'):
    def f():
        try:
            if len(urls) > 0:
                n = random.randint(0, 5)
                headers = {'User-Agent': USER_AGENTS[n], "LOG_ENABLED": True}
                runner = crawler.CrawlerRunner()
                for url in urls:
                    runner.crawl(selectCrawler(import_source), urls=url,course_type=course_type)
                deferred = runner.join()
                deferred.addBoth(lambda _: reactor.stop())
                if not reactor.running:
                    reactor.run()
        except Exception as e:
            print("error {}".format(traceback.format_exc()))
    if len(urls) > 0:
        p = Process(target=f, )
        p.start()
        p.join()
    else:
        # fetch as per the import_source
        args = {
            "talentedge": "https://talentedge.com/browse-courses/",
            "hughes": "https://www.hugheseducation.com/BrowseCourses",
            "eduonix": "https://www.eduonix.com/courses"  # Insert URL
        }
        check_array = [start, stop]
        p = Process(target=getAllCourseUrls, args=(
            args[import_source], import_source, check_array,course_type))
        p.start()
        p.join()
