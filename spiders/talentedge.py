import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
import requests
import json
import os
import app
import traceback
import re, sys
from datetime import datetime
import dateutil.parser
# Functions to format and return Object

f = open('xpath/talentedge.json', "r")
xpathTemplateCommon = json.loads(f.read())
regex_check = xpathTemplateCommon['regex_check']
xpathTemplate = xpathTemplateCommon['default']


def what_will_learn(response, xpathTemplate):
    # loop through the Xpaths here
    returnObject = []
    length = response.xpath(
        "count(" + xpathTemplate["what_will_learn"][0]+")").get()
    length = int(float(length))
    for x in range(1, length+1):
        returnObject.append(
            {"option":
             response.xpath(
                 xpathTemplate["what_will_learn"][0]+"["+str(x)+"]"+xpathTemplate["what_will_learn"][1]).get()[0:250] or ""
             }
        )

    return returnObject


def target_students(response, xpathTemplate):
    returnObject = []
    length = response.xpath(
        "count(" + xpathTemplate["target_students"][0]+")").get()
    length = int(float(length))
    for x in range(1, length+1):
        returnObject.append(
            {"option": response.xpath(
                xpathTemplate["target_students"][0]+"["+str(x)+"]"+xpathTemplate["target_students"][1]).get() or ""})

    return returnObject


def prerequisites(response, xpathTemplate):
    returnObject = []
    length = response.xpath(
        "count(" + xpathTemplate["prerequisites"][0]+")").get()
    length = int(float(length))
    for x in range(1, length+1):
        returnObject.append(
            {"option": response.xpath(
                xpathTemplate["prerequisites"][0]+"["+str(x)+"]"+xpathTemplate["prerequisites"][1]).get() or ""})

    return returnObject


def style_to_url(text):
    
    op_text = text if text else "https://via.placeholder.com/150.png"
    op_text = op_text.replace("background:url('", "")
    op_text = op_text.replace("')", "")
    return "MEDIA::"+op_text


def Instructors(response, xpathTemplate):
    
    returnObject = []
    try:
        length = response.xpath(
            "count(//" + xpathTemplate["Instructors"][0]+")").get()
        length = int(float(length))
        if (length == 0):
            return [{
                    "name": '',
                    "designation": '',
                    "instructor_bio": '',
                    "image_url": "MEDIA::"
                    }]
        for x in range(1, length+1):
            returnObject.append(
                {
                    "name": response.xpath(xpathTemplate["Instructors"][1]+"["+str(x)+"]"+xpathTemplate["Instructors"][2]).get() or "",
                    "designation": response.xpath(xpathTemplate["Instructors"][1]+"["+str(x)+"]"+xpathTemplate["Instructors"][3]).get() or "",
                    "instructor_bio": response.xpath(xpathTemplate["Instructors"][1]+"["+str(x)+"]"+xpathTemplate["Instructors"][4]).get()[0:250] or "",
                    "image_url": style_to_url(response.xpath(xpathTemplate["Instructors"][5]+"["+str(x)+"]"+xpathTemplate["Instructors"][6]).get()) or ''
                }
            )
    except Exception as e:
        print(e)
        return [{
                    "name": '',
                    "designation": '',
                    "instructor_bio": '',
                    "image_url": "MEDIA::"
                    }]
    return returnObject


def reviews(response, xpathTemplate):
    returnObject = []
    length = response.xpath("count(" + xpathTemplate["reviews"][0]+")").get()
    length = int(float(length))
    if (length == 0):
        return [{
                "reviewer_name": " ",
                "review_date": datetime.now().isoformat(),
                "review":  " ",
                "rating": 10,
                }]
    for x in range(1, length+1):
        returnObject.append(
            {
                "reviewer_name": response.xpath(xpathTemplate["reviews"][0]+"["+str(x)+"]"+xpathTemplate["reviews"][1]).get() or " ",
                "review_date": datetime.now().isoformat(),
                "review": response.xpath(xpathTemplate["reviews"][0]+"["+str(x)+"]"+xpathTemplate["reviews"][2]).get()[0:250] or " ",
                "rating": 10,
                "photo": "MEDIA::"+response.xpath(xpathTemplate["reviews"][0]+"["+str(x)+"]"+xpathTemplate["reviews"][3]).get() or " "
            }
        )
    return returnObject


def push_to_strapiCMS(data, course_platform):
    try:
        # print(json.dumps(data))
        response = requests.post(os.environ['apiUrl'] + '/import-learn-content/' +
                                 course_platform, headers={"Content-Type": "application/json"}, json=[data])
        # print("@@@Response@@@@@")
        # print(response.json())
    except Exception as e:
        print("ERROR in posting data to cms Push failed")


def get_content(response, xpathTemplate):

    ul_list = response.xpath(xpathTemplate["get_content"]).extract()
    clean = re.compile('<.*?>')
    content = ""
    for row in ul_list:
        newContent = re.sub(clean, '', row)
        content = content + newContent
    if(len(content) < 20):
        content = "Content too short to be read by Strapi!!!! Adding Extra characters to make the course visible on the Backend"
    
    return content[0:250]


def get_topics(response, xpathTemplate):
    
    try:
        length = response.xpath(
            "count(" + xpathTemplate["get_topics"][0]+")").get()
        length = int(float(length))
        modules = []
        for x in range(1, length + 1):
            module_heading = response.xpath(
                xpathTemplate["get_topics"][0]+"["+str(x)+"]"+xpathTemplate["get_topics"][1]).get()
            modules.append(module_heading)
        return modules
    except:
        print('Error in get_topics')
    return ''


def generate_id(response, xpathTemplate):
    href = response.xpath(xpathTemplate["generate_id"]).get()

    return 'TE_' + str(href).split("=")[1]


def generate_description(response, xpathTemplate):
    no_of_para = response.xpath(
        "count(" + xpathTemplate["generate_description"][0]+")").get()
    no_of_para = int(float(no_of_para))
    description = ""
    for x in range(1, no_of_para + 1):
        para = response.xpath(xpathTemplate["generate_description"][0]+"["+str(
            x)+"]"+xpathTemplate["generate_description"][1]).get() or '    ' 
        description = description + "<p>" + para + "</p>"
    
    try:
        if(len(xpathTemplate["generate_description"]) == 3):
            no_of_para = response.xpath(
                "count(" + xpathTemplate["generate_description"][2]+")").get()
            no_of_para = int(float(no_of_para))
            for x in range(1, no_of_para + 1):
                para = response.xpath(xpathTemplate["generate_description"][2]+"["+str(
            x)+"]"+xpathTemplate["generate_description"][1]).get() or '    ' 
                description = description + "<p>" + para + "</p>"
            if(len(description) < 20):
                description = "Description too short to be read by Strapi!!!! Adding Extra characters to make the course visible on the Backend"
            return description
    except:
        print("Error at Generate Description, failed to get description list ")
    
    if(len(description) < 20):
        description = "Description too short to be read by Strapi!!!! Adding Extra characters to make the course visible on the Backend"
    return description


def get_price_from_string(price_string):
    try:
        parsedprice = ''
        if(len(price_string) >= 1):
            price_list = [str(i) for i in price_string if i.isdigit()]
            separator = ''
            parsedprice = separator.join(price_list)

        return parsedprice
    except:
        print("Error at get_price from string")
        return ''


def getMedium(StringValue):
    if StringValue != None and "live & interactive" in str(StringValue).lower():
        return "Online"
    else:
        return "Not Specified"


def get_learn_type_from_title(title):
    if title != None:
        title = str(title).lower()
        if "certification" in title or "certificate" in title:
            return "Certifications"
        elif "programme" in title or "diploma" in title or "degree" in title:
            return "Degree"
        else:
            return "Courses"


def get_instruction_type(response, xpathTemplate):
    try:
        StringValue = response.xpath(
            xpathTemplate["get_instruction_type"]).get()
        if (StringValue and StringValue.split("/") and len(StringValue.split("/")) > 2 ):
            StringValue = StringValue.split("/")[2]
        if StringValue != None and "weekend classes" in str(StringValue).lower():
            return "Instructor paced"
    except Exception as e:
        print("ERROR in posting data to cms Instruction type")
        print(e)
    return "Others"


def get_all_course_urls(response):
    no_of_urls = response.xpath(
        "count(" + xpathTemplate["get_all_course_urls"][0]+")").get()
    no_of_urls = int(float(no_of_urls))
    print("found {} courses".format(no_of_urls))
    urls = []
    for x in range(1, no_of_urls + 1):
        url = response.xpath(xpathTemplate["get_all_course_urls"][0] +
                             "["+str(x)+"]"+xpathTemplate["get_all_course_urls"][1]).get()
        urls.append(url)
    return urls


def get_video_url(response, xpathTemplate):
    try:
        para_count = response.xpath(
            "count(" + xpathTemplate["get_video_url"][0]+")").get()
        para_count = int(float(para_count))
        return response.xpath(xpathTemplate["get_video_url"][0]+"["+str(para_count)+"]"+xpathTemplate["get_video_url"][1]).get() or ''
    except Exception as e:
        print("ERROR in posting data to cms Video URL")
    return ""


def check_course_type(url):
    for regex_string in regex_check['international_url']:
        match = re.search(regex_string, url)
        if match:
            return 'international'

    return 'default'

def get_text_date(text = ''):
    text = text.replace('Start - ','')
    d = dateutil.parser.parse(text)
    # return d.strftime("%b %d, %Y")
    return d.isoformat()
    
def get_emi(response, xpathTemplate):

    ul_list = response.xpath(xpathTemplate["emi_format"]).extract()
    clean = re.compile('<.*?>')
    content = ""
    for row in ul_list:
        newContent = re.sub(clean, '', row)
        content = content + newContent
    
    if(len(content) < 20):
        content = "Content too short to be read by Strapi!!!! Adding Extra characters to make the course visible on the Backend"
    
    return content

class TalentEdgeSpider(scrapy.Spider):
    name = 'talentedge'

    def __init__(self, *args, **kwargs):

        self.download_delay = 1
        urls = kwargs.pop('urls', [])
        if urls:
            self.start_urls = urls.split(',')
        super(TalentEdgeSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # print(response.request.url)

        # choose as per the type
        f = open('defaults/talentedge.json', "r")
        op_object = json.loads(f.read())

        if response.request.url != "https://talentedge.com/browse-courses/":
            if (check_course_type(response.request.url) == "international"):
                xpathTemplate = xpathTemplateCommon['international']
            else:
                xpathTemplate = xpathTemplateCommon['default']

            op_object_new = {
                "id": generate_id(response, xpathTemplate),
                "title": response.xpath(xpathTemplate["title"]).get(),
                "subtitle": response.xpath(xpathTemplate["title"]).get(),
                "description": generate_description(response, xpathTemplate)[0:250],
                "learn_type":  get_learn_type_from_title(response.xpath(xpathTemplate["learn_type"]).get()),
                "provider_course_url": response.request.url,
                "slug": str(response.xpath(xpathTemplate["slug"]).get()).replace(" ", "_"),
                "content": "<p>" + get_content(response, xpathTemplate) + "</p>",
                "medium": getMedium(response.xpath(xpathTemplate["medium"]).get()),
                "instruction_type": get_instruction_type(response, xpathTemplate),
                "image_url": "",
                "video_url": get_video_url(response, xpathTemplate),
                "detail_information": {
                    "duration": {
                        "id": "",
                        "total_video_content_in_hrs": "",
                        "total_duration_in_hrs":  "",
                        "total_duration_in_months": int(float(response.xpath(xpathTemplate["total_duration_in_months"]).get())),
                        "recommended_effort_per_week": "",
                        "avg_session_duration_with_instructor": ""
                    },
                    "batches": 
                        {
                            # "id": "",
                            "batch_size": "",
                            "batch_schedule": "",
                            "batch_timings": "",
                            "batch_start_date": get_text_date(response.xpath(xpathTemplate["batch_start_date"]).get()),
                            "batch_end_date": get_text_date(response.xpath(xpathTemplate["batch_end_date"]).get())
                        }
                },
                "pricing": {
                    "id": "",
                    "pricing_type": "Paid",
                    "currency": "INR",
                    "regular_price": get_price_from_string(response.xpath(xpathTemplate["regular_price"]).get()),
                    "sale_price": get_price_from_string(response.xpath(xpathTemplate["sale_price"]).get()),
                    "schedule_of_sale_price": "",
                    "free_condition_description": "",
                    "conditional_price": "",
                    "finance_option": True,
                    "financing_option": "EMI",
                    "finance_details": get_emi(response, xpathTemplate)
                },
                "what_will_learn": what_will_learn(response, xpathTemplate),
                "target_students": target_students(response, xpathTemplate),
                "prerequisites": prerequisites(response, xpathTemplate),
                "skills_gained": [],  # array of strings
                "instructors": Instructors(response, xpathTemplate),
                "reviews": reviews(response, xpathTemplate),
                "meta_information": {
                    "id": "",
                    "meta_title": "",
                    "meta_description": "",
                    "add_type": "",
                    "import_source": "",
                    "external_source_id": "",
                    "reject_reason": "",
                    "published": ""
                },
                "topics": get_topics(response, xpathTemplate)
            }
            op_object.update(op_object_new)
            push_to_strapiCMS(op_object, "talentedge")
            a = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") + \
                ': ' + response.request.url + "  - Processed"
            # print(op_object["pricing"])
            print(a)
        else:
            print("Scraping all urls")
            course_urls = get_all_course_urls(response)
            count = 1
            for url in course_urls:
                try:
                    yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={'count': count})
                    print("URL Fetched:" + url)
                    count = count + 1
                except Exception as e:
                    print("ERROR when scraping {}".format(
                        traceback.format_exc()))
