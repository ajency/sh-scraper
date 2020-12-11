import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
import json


class NulearnSpider(scrapy.Spider):
    name = 'nulearn'

    def __init__(self, *args, **kwargs):

        urls = kwargs.pop('urls', [])
        if urls:
            self.start_urls = urls.split(',')
        super(NulearnSpider, self).__init__(*args, **kwargs)

    # custom_settings = {'ROTATING_PROXY_LIST_PATH': 'Proxy List.txt', 'DOWNLOADER_MIDDLEWARES': {
    #     'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    #     'rotating_proxies.middlewares.BanDetectionMiddleware': 620
    # }}

    def parse(self, response):
        # links = response.xpath(
        #     "//div[@class='mob-inst-course-wrapper']/a[@class='mob-menu-link w-inline-block']/@href")
        # xp = "//div[@class='mob-inst-course-wrapper']/a[@class='mob-menu-link w-inline-block']/@href"

        # return (Request(url, callback=self.parse_url,  meta={'ROTATING_PROXY_LIST_PATH': 'Proxy List.txt', 'DOWNLOADER_MIDDLEWARES': {
        #      'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        #      'rotating_proxies.middlewares.BanDetectionMiddleware': 620
        #  }}
        # ) for url in response.xpath(xp).extract())
        op_object = {"title": "",
                     "description": ""}
        links = response.xpath("//h1[@class='course-page-name']/text()")
        op_object = {"title": response.xpath("//h1[@class='course-page-name']/text()").get(),
                     "description": response.xpath("//p[@class='course-banner-para']/text()").get(),
                     "provider":  response.xpath("//div[@class='course-icon-block'][1]/h4[@class='course-banner-sub-lael']/text()").get(),
                     "provider_course_url": "https://www.nulearn.in/courses/executive-certificate-programme-in-data-analytics-with-r",
                     #  "add_type": "Manual",
                     "import_source": "nulearn",
                     # (Replace - with _ to slugify)
                     "external_source_id": "nulearn_executive_certificate_programme_in_data_analytics_with_r",

                     "content": response.xpath("//div[@class='course-detail-container about-course-con']/p[1]/text()").get(),
                     "basic_information": {
            "medium": {
                "default_display_label": response.xpath("//div[@class='course-icon-block'][5]/div/text()").get(),
            },
            "instruction_type": response.xpath("//div[@class='course-icon-block'][5]/div/text()").get(),
            # needs revision
            "image_url": response.xpath("//div[@class='course-pg-banner']/div[@class='course-banner-img']/@style").get(),
        },
            "duration": {
            "total_duration": response.xpath("//div[@class='course-icon-block'][2]/h4[@class='course-banner-sub-lael']/text()").get(),
        },
            "batches": [
            {
                "batch_count": response.xpath("//div[@class='course-icon-block'][3]/h4[@class='course-banner-sub-lael']/text()").get(),
                "batch_start_date":  response.xpath("//div[@class='course-icon-block'][4]/h4[@class='course-banner-sub-lael']/text()").get(),
            }
        ],
            "pricing": {
            "currency": "INR",
                        "regular_price":  response.xpath("//div[@class='fee-stru-line'][1]//h2[@class='program-fee-amount']/text()").get(),
        },
            "provider_information": {
            "provider": {
                "name": response.xpath("//div[@class='course-icon-block'][1]/h4[@class='course-banner-sub-lael']/text()").get(),
            }
        },
            # "what_will_learn": [
            #     {
            #         "option": "Understanding Analytics and its Role in the Organizations"
            #     },
            #     {
            #         "option": "Data Warehouse, OLAP and Pivot Table"
            #     }
            # ],
            # "target_students": [
            #     {
            #         "option": "Professionals who are looking to upgrade their career in Data Analytics."
            #     },
            #     {
            #         "option": "Entrepreneurs/Managers & Leaders, Coordinators and Team Members"
            #     }
            # ],
            #     "prerequisites": [
            #     {
            #         "option": "Graduation or equivalent degree from any recognized University or Institute"
            #     },
            #     {
            #         "option": "Working Professionals with minimum of 2 years of experience"
            #     }
            # ],
            # "skills_gained": [
            #     {
            #         "name": "CERTIFICATION FROM IIM ROHTAK"
            #     }
            # ],
            # "Instructors": [
            #     {
            #         "name": "Dr. Manas Tripathi",
            #         "designation": "M.TECH, P.H.D (BITS PILANI)",
            #         "instructor_bio": "Dr. Manas Tripathi works as an Assistant Professor in the area of Information Systems at Indian Institute of Management Rohtak. ",
            #         "instructor_image": "https://www.nulearn.in/uploads/images/Prof-Manas-Tripathi-faculty.jpg"
            #     }
            # ],
            # "reviews": [
            #     {
            #         "reviewer_name": "Bala Murali Krishnan",
            #         "review": "The curriculum has been designed wonderfully as per the industry standards. The curriculum is sure to add value to the daily tasks we do. The admission process was really smooth and the team's job is really appreciable as they take feedback and work on it. Great job team Nulearn"
            #     }
            # ]
        }

        # print('\x1b[6;30;42m' + links.get() + '\x1b[0m')
        html = ''
        link_list = []
        for link in links:
            # Extract the URL text from the element
            url = link.get()
            html += json.dumps(op_object)
        with open('/tmp/output.txt', 'a') as page:
            page.write(html)
        page.close()

        # return (Request('https://www.nulearn.in/courses/executive-certificate-programme-in-data-analytics-with-r', callback=self.parse_url,  meta={'ROTATING_PROXY_LIST_PATH': 'Proxy List.txt', 'DOWNLOADER_MIDDLEWARES': {
        #      'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        #      'rotating_proxies.middlewares.BanDetectionMiddleware': 620
        #  }}
        # ) )
