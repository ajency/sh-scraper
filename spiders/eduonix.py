import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
import requests
import json
import os
import app
import traceback
import re
from datetime import datetime
import requests
import brotli
from scrapy.http import HtmlResponse
import sys
from time import sleep
# Functions to format and return Object

f = open('xpath/eduonix.json', "r")
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
                 xpathTemplate["what_will_learn"][0]+"["+str(x)+"]"+xpathTemplate["what_will_learn"][1]).get() or ""
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
    #print(sys._getframe().f_code.co_name+'')
    op_text = text if text else "https://via.placeholder.com/150.png"
    op_text = op_text.replace("background:url('", "")
    op_text = op_text.replace("')", "")
    return "MEDIA::"+op_text


def Instructors(response, xpathTemplate):
    #print(sys._getframe().f_code.co_name+'')
    returnObject = []
    length = response.xpath(
        "count(//" + xpathTemplate["Instructors"][0]+")").get()
    length = int(float(length))
    for x in range(1, length+1):
        instructor_bio = response.xpath(xpathTemplate["Instructors"][1]+"["+str(x)+"]"+xpathTemplate["Instructors"][4]).get() or ''
        clean = re.compile('<.*?>')
        instructor_bio = re.sub(clean, '', instructor_bio)
        returnObject.append(
            {
                "name": response.xpath(xpathTemplate["Instructors"][1]+"["+str(x)+"]"+xpathTemplate["Instructors"][2]).get(),
                "designation": "",
                "instructor_bio": instructor_bio[0:250],
                "image_url": style_to_url(response.xpath(xpathTemplate["Instructors"][5]+"["+str(x)+"]"+xpathTemplate["Instructors"][6]).get())
            }
        )
    if(length < 1):
        return [{
                "name": "",
                "designation": "",
                "instructor_bio": "",
                "image_url": style_to_url("")
            }]
    return returnObject


def reviews(response, xpathTemplate):
    #print(sys._getframe().f_code.co_name+'')
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
                "review": response.xpath(xpathTemplate["reviews"][0]+"["+str(x)+"]"+xpathTemplate["reviews"][2]).get() or " ",
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
    #print(sys._getframe().f_code.co_name+'')
    ul_list = response.xpath(xpathTemplate["get_content"]).extract()
    clean = re.compile('<.*?>')
    content = ""
    for row in ul_list:
        newContent = re.sub(clean, '', row)
        content = content + newContent
    
    content = 'Found no content for the course, This is a Filler content to Fill the Minimum Requirement for it.' if len(content) < 30 else  content
    return content


def get_topics(response, xpathTemplate):
    #print(sys._getframe().f_code.co_name+'')
    try:
        length = response.xpath(
            "count(" + xpathTemplate["get_topics"][0]+")").get()
        length = int(float(length))
        modules = []
        for x in range(1, length + 1):
            module_heading = response.xpath(
                xpathTemplate["get_topics"][0]+"["+str(x)+"]"+xpathTemplate["get_topics"][1]).get()
            clean = re.compile('<.*?>')
            if(module_heading is not None):
                module_heading = module_heading.replace('-->','')
                module_heading = re.sub(clean, '', module_heading)
                module_heading = module_heading.replace('\n','')
                module_heading = module_heading.strip()
            else:
                module_heading = ''
            modules.append(module_heading)
        return modules
    except Exception as e:
        print('Error in get_topics')
        print(e)
    return ''


def generate_id(response, xpathTemplate):
    #print(sys._getframe().f_code.co_name+'')
    href = response.xpath(xpathTemplate["generate_id"]).get()
    clean = re.compile('<.*?>')
    href = re.sub(clean, '', href)
    return 'ED_' + str(href).lower().strip().replace(" ","_").replace("'","")


def generate_description(response, xpathTemplate):
    #print(sys._getframe().f_code.co_name+'')
    no_of_para = response.xpath(
        "count(" + xpathTemplate["generate_description"][0]+")").get()
    no_of_para = int(float(no_of_para))
    description = ""
    for x in range(1, no_of_para + 1):
        para = response.xpath(xpathTemplate["generate_description"][0]+"["+str(
            x)+"]"+xpathTemplate["generate_description"][1]).get() or ''
        # remove strong tags from here
        clean = re.compile('<.*?>')
        para = re.sub(clean, '', para)
        description = description + "<p>" + para + "</p>"

    description = 'Found no Descripion for the course, This is a Filler description to Fill the Minimum Requirement for it.' if description == '' else  description
    return description


def get_price_from_string(price_string):
    #print(sys._getframe().f_code.co_name+'')
    try:
        parsedprice = ''
        if(len(price_string) >= 1):
            price_list = [str(i) for i in price_string if i.isdigit()]
            separator = ''
            parsedprice = separator.join(price_list)

        return float(parsedprice[:-2])
    except Exception as e:
        print("Error at get_price from string")
        print(e)
        return ''


def getMedium(StringValue):
    #print(sys._getframe().f_code.co_name+'')
    if StringValue != None and "live & interactive" in str(StringValue).lower():
        return "Online"
    else:
        return "Not Specified"


def get_learn_type_from_title(title):
    #print(sys._getframe().f_code.co_name+'')
    if title != None:
        title = str(title).lower()
        if "certification" in title or "certificate" in title:
            return "Certifications"
        elif "programme" in title or "diploma" in title or "degree" in title:
            return "Degree"
        else:
            return "Courses"


def get_instruction_type(response, xpathTemplate):
    #print(sys._getframe().f_code.co_name+'')
    try:
        StringValue = response.xpath(
            xpathTemplate["get_instruction_type"]).get()
        if (StringValue and StringValue.split("/")):
            StringValue = StringValue.split("/")[2]
        if StringValue != None and "weekend classes" in str(StringValue).lower():
            return "Instructor paced"
    except Exception as e:
        print("ERROR in posting data to cms Instruction type")
    return "Others"


def call_eduonix_api(url,payload):
    files = [

    ]
    headers = {
        'authority': 'www.eduonix.com',
        'method': 'POST',
        'path': '/courses/catalog',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'cookie': '__cfduid=dad770a18046d092543020ab2e2c6e5411602656917; onix_Usercountry=India; onix_Usercurrency=INR; _gcl_au=1.1.297683866.1602656926; _ga=GA1.2.812038867.1602656926; onix_GDPR=onix_GDPR_set; _gid=GA1.2.920485464.1604575243; header_strip=close; PHPSESSID=dj9i17m0uo0m9u9lpfngu8d1sg; sess_defender=5944caf97410b43d3543213d27e6dcc941e2ace73c89a1ed41040c6633f9a94c69c8125e14570a4de5e438b9cd95b1282dead5fbf97ae0aa76d4e65a34d14e30VJz7If1VHrDIg9mlbw11WG%2FmFMSkZc%2FDNkwFy9rPjz5r6j7L05FJdw%2Bf; sc_is_visitor_unique=rx11839629.1604660052.B22B02DDC2014FEB61EBD461165CABE8.12.8.5.4.4.4.3.3.3; _uetsid=f052b9c01f5811ebbe7ec5e8d1cccd3d; _uetvid=293aa3201cd811eb8232f3cc2bbb2d50; __cfduid=de826410b23c0f32f6ae15012b84b610d1604300240; onix_Usercountry=India; onix_Usercurrency=INR; PHPSESSID=c2g7mivnvthm43536rv8d35cke; sess_defender=5ae402794d5cd64cd4216c2c50cb0c666048d6622d622c8f740c359f0856a9327e122b9def8c2b7234d13529c6c824f402f4640239aff6fd3d6cab3057e43b5dTgVHEOmLalPt8e0rdCmoLNjn%2B3HSdXtkLcl%2FRjN%2BtmWIeriJYzn2BZwC',
        'edu-pass': 'courses-page',
        'origin': 'https://www.eduonix.com',
        'referer': 'https://www.eduonix.com/courses',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.61',
        'x-requested-with': 'XMLHttpRequest'
    }
    response = requests.request(
                "POST", url, headers=headers, data=payload, files=files)
    return response
    
def get_eduonix_deals():
    url = "https://www.eduonix.com/deals/fetch_deals"

    payload = {'category':'mightydeals'}
    
    url_final_list = []
   
    types_array = ['mightydeals','otherDeals','super100Deals','skillDeals','mobileDeals','webDeals','softwareDeals','sysDeals','professionalDeal','buyWhatDeals']
    for x in types_array:
        payload = {'category':x}
        try:
            response =  call_eduonix_api(url,payload)
        except Exception as e:
            print("ERROR")
            print(e)
        # content = json.loads(response.content)['courses_html']
        content = str( response.content)
        url_list = re.findall("(?P<url>https:\/\/www.eduonix\.com\/[\S]+)\"",content)
        url_list =list(dict.fromkeys(url_list))
        url_final_list.extend(url_list)
    return url_final_list



def get_all_course_urls(arrayStart=[]):
    # get List of URL from the API call
    url = "https://www.eduonix.com/courses/catalog"

    payload = {'cata_sort': 'highest_rated',
            'category_id': '0',
            'module': 'courses',
            'onload': 'true'}
    
    url_final_list = []
    r1= 1
    r2 = 124
    if(len(arrayStart)==2):
        r1=arrayStart[0]
        r2=arrayStart[1]
    
    for x in range(r1,r2):
        suffix = '/'+str(x) if x != 1 else ''
        try:
            response =  call_eduonix_api(url+(suffix),payload)
        except Exception as e:
            print("ERROR")
            print(e)
        content = json.loads(response.content)['courses_html']
        url_list = re.findall("(?P<url>https:\/\/www.eduonix\.com\/[\S]+)\"",content)
        url_list =list(dict.fromkeys(url_list))
        url_final_list.extend(url_list)
    return url_final_list


def get_video_url(response, xpathTemplate):
    #print(sys._getframe().f_code.co_name+'')
    try:
        para_count = response.xpath(
            "count(" + xpathTemplate["get_video_url"][0]+")").get()
        para_count = int(float(para_count))
        if(response.xpath(xpathTemplate["get_video_url"][0]+"["+str(para_count)+"]"+xpathTemplate["get_video_url"][1]).get()):
            return (response.xpath(xpathTemplate["get_video_url"][0]+"["+str(para_count)+"]"+xpathTemplate["get_video_url"][1]).get() or '' ).replace("//","")
        else: 
            return ''
    except Exception as e:
        print("ERROR in posting data to cms Video URL"+e)
    return ""


def check_course_type(url):
    
    for regex_string in regex_check['international_url']:
        match = re.search(regex_string, url)
        if match:
            return 'international'

    return 'default'

def get_hours(response,xpathTemplate):
    try:
        op = response.xpath(xpathTemplate["total_duration_in_hrs"]).get().lower().replace('hours','').replace('+','')
        return int(float( op ))
    except Exception as e:
        print(e)

def remove_tags(text):
    text = re.sub('\n','',text)
    text = re.sub("\\'","\'",text)
    text = re.sub('<style>[\S\s]+<\/style>','',text)
    text = re.sub('<script>[\S\s]+<\/script>','',text)
    return text
    

class EduonixSpider(scrapy.Spider):
    name = 'eduonix'

    def __init__(self, array = [], *args, **kwargs):

        self.download_delay = 1
        urls = kwargs.pop('urls', [])
        course_type = kwargs.pop('course_type', '')
        self.arrayStart = array
        self.course_type = course_type
        if urls:
            self.start_urls = urls.split(',')
        super(EduonixSpider, self).__init__(*args, **kwargs)
        
    def get_all_course_types_urls(self):
        url = ''
        url_final_list = []
        search_string = '"(?P<url>https:\/\/www.eduonix\.com\/[\S]+)\""'
        if(self.course_type == 'course'):
            course_urls = get_all_course_urls(self.arrayStart)
        if(self.course_type == 'deals'):
            course_urls = get_eduonix_deals()
        if(self.course_type == 'edegrees'):
            url = 'https://www.eduonix.com/edegree'
            search_string = '<a href=\"(?P<url>https:\/\/www.eduonix\.com\/[\S]+e-?degree)\"'
        elif(self.course_type == 'paths'):
            url = 'https://www.eduonix.com/paths'
            search_string = "(?P<url>https:\/\/www.eduonix\.com\/paths\/[\S]+)\""
        elif(self.course_type == 'professional'):
            url = 'https://www.eduonix.com/professional-bundle'
            search_string = '<a href=\"(?P<url>https:\/\/www.eduonix\.com\/[\S]+)\">'
        else:
            return url_final_list
        response = requests.request("GET", url)
        content = str(response.content)

        if(self.course_type == 'professional'):
            content = re.search('\/\* New UI Ends \*\/(.*?)<!-- <\/DealsBody> -->',content).group(1)
        url_list = re.findall(search_string,content)
        url_list =list(dict.fromkeys(url_list))
        url_final_list = url_list
        return url_final_list

    def parse(self, response):
        # print(response.request.url)

        # choose as per the type
        print(response.request.url)
        f = open('defaults/eduonix.json', "r")
        op_object = json.loads(f.read())
        f.close()

        if response.request.url != "https://www.eduonix.com/courses":
            xpathTemplate = xpathTemplateCommon['default']
            f =open("eduonix.html",'w')
            f.write(response.text)
            f.close()
            if(self.course_type == 'deals'):
                xpathTemplate = xpathTemplateCommon['deals']
            elif(self.course_type == 'professional'):
                xpathTemplate = xpathTemplateCommon['professional']
            elif(self.course_type == 'paths'):
                xpathTemplate = xpathTemplateCommon['paths']
            elif(self.course_type == 'edegrees'):
                xpathTemplate = xpathTemplateCommon['edegrees']
            try:
                op_object_new = {
                    "id": generate_id(response, xpathTemplate),
                    "title": response.xpath(xpathTemplate["title"]).get().strip(),
                    "subtitle": (response.xpath(xpathTemplate["subtitle"]).get() or '' ).replace('\n','').strip()[0:250],
                    "description": generate_description(response, xpathTemplate),
                    "learn_type":  get_learn_type_from_title(response.xpath(xpathTemplate["learn_type"]).get()),
                    "provider_course_url": response.request.url,
                    "slug": str(response.xpath(xpathTemplate["slug"]).get()).strip().replace(" ", "_"),
                    "content": "<p>" + get_content(response, xpathTemplate) + "</p>",
                    "medium": getMedium(response.xpath(xpathTemplate["medium"]).get()),
                    "instruction_type": get_instruction_type(response, xpathTemplate),
                    "image_url": "",
                    "video_url": get_video_url(response, xpathTemplate),
                    "detail_information": {
                        "duration": {
                            "id": "",
                            "total_video_content_in_hrs": "",
                            "total_duration_in_hrs":  get_hours(response, xpathTemplate),
                            "total_duration_in_months": "",
                            "recommended_effort_per_week": "",
                            "avg_session_duration_with_instructor": ""
                        },
                        "batches": [
                            {
                                "id": "",
                                "batch_size": "",
                                "batch_schedule": "",
                                "batch_timings": "",
                                "batch_start_date": "",
                                "batch_end_date": ""
                            }
                        ]
                    },
                    "pricing": {
                        "id": "",
                        "pricing_type": "Paid",
                        "currency": "INR",
                        "regular_price": get_price_from_string(response.xpath(xpathTemplate["regular_price"]).get()),
                        "sale_price": get_price_from_string(response.xpath(xpathTemplate["sale_price"]).get()),
                        "schedule_of_sale_price": "",
                        "free_condition_description": "",
                        "conditional_price": ""
                    },
                    "what_will_learn": what_will_learn(response, xpathTemplate),
                    "target_students": target_students(response, xpathTemplate),
                    "prerequisites": prerequisites(response, xpathTemplate),
                    "skills_gained": [{"option":"None"}],  # array of strings
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
            except Exception as e:
                print(e)
            op_object.update(op_object_new)
            push_to_strapiCMS(op_object, "eduonix")
            a = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") + \
                ': ' + response.request.url + "Processed"
            print(a)
        else:
            print("Scraping all urls")
            course_urls = self.get_all_course_types_urls()
            count = 1
            course_urls =list(dict.fromkeys(course_urls))
            for url in course_urls:
                try:
                    yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={'count': count,'course_type':self.course_type})
                    print("URL Fetched:" + url)
                    count = count + 1
                except Exception as e:
                    print("ERROR when scraping {}".format(
                        traceback.format_exc()))


# #print(sys._getframe().f_code.co_name+'')


    

# edegrees
# paths
# professional
