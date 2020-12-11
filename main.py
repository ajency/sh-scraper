import requests
from dotenv import load_dotenv
from data_formatter import DataFormatter
import traceback
import os
import json
import app
load_dotenv()

formatter = DataFormatter()


def fetchNulearnData():
    try:
        response = requests.get(
            "https://www.nulearn.in/MainSite/retrieve/?id=all_course")
        data = response.json()
        return data
    except Exception as e:
        print("ERROR in API request <> {}".format(traceback.format_exc()))
    return None


def importDataToCMS(payload, course_platform):
    try:
        start = 0
        chunk_size = 10
        while start <= len(payload):
            dataChunk = payload[start: (start+chunk_size)]
            # print(json.dumps(dataChunk))
            response = requests.post(os.environ['apiUrl'] + '/import-learn-content/' +
                                     course_platform, headers={"Content-Type": "application/json"}, json=dataChunk)
            # print(response.json())
            # with open('data.json', 'a') as outfile:
            #     json.dump(dataChunk, outfile)
            # start = start + chunk_size
            break
    except Exception as e:
        print("Exception in bulk indexing: {}".format(traceback.format_exc()))


def fetchDataByCourseId(courseIds):
    courses = []
    all_courses = []
    nulearnCourses = fetchNulearnData()
    for course in nulearnCourses:
        print("formatting for {}".format(course['course_id']))
        if courseIds != None:
            if course['course_id'] in courseIds:
                course = formatter.formattNulearnCourseData(course)
                courses.append(course)
        else:
            course = formatter.formattNulearnCourseData(course)
            all_courses.append(course)

    if courseIds != None:
        return courses
    else:
        return all_courses


def lambda_handler(event, context=None):
    courses = None
    if 'importSource' in event and event['importSource'] != None:
        if event['importSource'].lower() == 'nulearn':
            if 'params' in event and event['params'] != None and 'courseIds' in event['params'] and event['params']['courseIds'] != None and len(event['params']['courseIds']) > 0:
                courses = fetchDataByCourseId(event['params']['courseIds'])
            else:
                print("getting all courses")
                courses = fetchDataByCourseId(None)
            if courses != None and len(courses) > 0:
                importDataToCMS(courses, 'Nulearn')
                return {'status': 200, 'message': 'courses scraped successfully'}
            else:
                return {'status': 200, 'message': 'no courses scraped'}
        elif event['importSource'].lower() == 'talentedge':
            if 'params' in event and event['params'] != None and 'course_scrape_urls' in event['params'] and event['params']['course_scrape_urls'] != None and len(event['params']['course_scrape_urls']) > 0:
                app.spider_handler(
                    event['params']['course_scrape_urls'], "talentedge")
                print("done")
                return {'status': 200, 'message': 'talentedge courses scraped successfully'}
            else:
                app.spider_handler([], "talentedge")
        elif event['importSource'].lower() == 'hughes':
            if 'params' in event and event['params'] != None and 'course_scrape_urls' in event['params'] and event['params']['course_scrape_urls'] != None and len(event['params']['course_scrape_urls']) > 0:
                app.spider_handler(
                    event['params']['course_scrape_urls'], "hughes")
                print("done")
                return {'status': 200, 'message': 'hughes courses scraped successfully'}
            else:
                app.spider_handler([], "hughes")
        elif event['importSource'].lower() == 'eduonix':
            if 'params' in event and event['params'] != None and 'course_scrape_urls' in event['params'] and event['params']['course_scrape_urls'] != None and len(event['params']['course_scrape_urls']) > 0:
                course_type = 'course'
                if('course_type' in event['params'] and event['params']['course_type'] != None ):
                    course_type = (event['params']['course_type'])  
                app.spider_handler(
                    event['params']['course_scrape_urls'], "eduonix",course_type=course_type)
                print("done")
                return {'status': 200, 'message': 'eduonix courses scraped successfully'}
            else:
                start = -1
                stop = -1
                course_type = 'course'
                if('start_page' in event['params'] and event['params']['start_page'] != None ):
                    start = (event['params']['start_page'])
                    
                if('stop_page' in event['params'] and event['params']['stop_page'] != None ):
                    stop = (event['params']['stop_page']) 
                    
                if('course_type' in event['params'] and event['params']['course_type'] != None ):
                    course_type = (event['params']['course_type'])  
                     
                app.spider_handler([], "eduonix",start=start, stop=stop,course_type=course_type)
        


payload = {"importSource": "hughes",
           "data_extract_mode": "api",
           "params":
           {
               'courseIds': [],
               # ["https://www.hugheseducation.com/executive-programmes/certificate-course-business-management"]
               'course_scrape_urls': [],
               'start_page': 21,
               'stop_page': 22,
               'course_type':'courses'
           }
           }
lambda_handler(payload)


# For eduoix, types of courses
# courses
# deals

# edegrees

# paths
# professional

