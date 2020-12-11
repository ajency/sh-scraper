import json
import re
import dateutil.parser
from datetime import datetime


class DataFormatter:

    def __init__(self):
        print("object")

    def get_learn_type_from_title(self, title):
        if title != None:
            if str(title).lower() == "certification":
                return "Certifications"
            elif str(title).lower() == "programme" or str(title).lower() == "diploma" or str(title).lower() == "degree":
                return "Degree"
            else:
                return "Courses"

    def formattNulearnCourseData(self, nulearnCourseData):
        f = open('defaults/nulearn.json', "r")
        data = json.loads(f.read())
        course = data  # Get format from JSON
        course["id"] = self.get_value_from_key('course_id', nulearnCourseData)
        course["title"] = self.get_value_from_key(
            'course_name', nulearnCourseData)
        course["subtitle"] = self.get_value_from_key(
            'short_desc', nulearnCourseData)
        course["description"] = self.get_value_from_key(
            'course_desc', nulearnCourseData)
        ############################## set Learn type ###########################
        learn_value = self.get_learn_type_from_title(course['title'])
        # { 'default_display_label' : learn_value, 'slug' : learn_value.lower()}
        course["learn_type"] = learn_value
        course["provider"] = self.get_value_from_key(
            'institute', nulearnCourseData)
        course["provider_course_url"] = "https://www.nulearn.in/courses/" + \
            self.get_value_from_key('course_url', nulearnCourseData)
        course["import_source"] = "nulearn"
        course["status"] = "draft"
        # course["slug"] = self.get_value_from_key(
        #     'course_url', nulearnCourseData)
        course["courseImageUrl"] = "MEDIA::https://www.nulearn.in/uploads/images/" + \
            self.get_value_from_key('course_ban_image', nulearnCourseData)

        duration = self.get_value_from_key(
            'Duration', nulearnCourseData) or '0'

        course["expected_duration_unit"] = ""
        if("months" in duration.lower()):
            course["expected_duration_unit"] = "Months"
        elif("years" in duration.lower()):
            course["expected_duration_unit"] = "Years"
        course["expected_duration"] = int(float(
            duration.replace(course["expected_duration_unit"], "")))

        basic_information = {"image": {}, "medium": {}}
        basic_information["image"]["name"] = self.get_value_from_key(
            'course_ban_image', nulearnCourseData)
        basic_information["image"]["formats"] = {"medium": {
            "url": "MEDIA::https://www.nulearn.in/uploads/images/" + self.get_value_from_key('course_ban_image', nulearnCourseData)}}
        medium = self.get_value_from_key('label_visit', nulearnCourseData)
        if medium != None and len(medium) > 0:
            if medium == "ONLINE SESSIONS &amp; CAMPUS VISITS" or medium == "ONLINE &amp; ON CAMPUS MODULE":
                basic_information["medium"]["default_display_label"] = "Online + Offline"
                basic_information["medium"]["slug"] = "online+offline"
            elif medium == "COVERAGE" or medium == "ONLINE &amp; ON CAMPUS MODULE":
                basic_information["medium"]["default_display_label"] = "Online"
                basic_information["medium"]["slug"] = "online"
        else:
            basic_information["medium"]["default_display_label"] = "Not Specified"
            basic_information["medium"]["slug"] = "not-specified"
        course["basic_information"] = basic_information
        ################################ Generate content from chapter json #########################################
        chapters = self.get_value_from_key("chapters", nulearnCourseData)
        if chapters != None:
            course["content"] = self.get_content_from_chapters(chapters)
        ################################ End of content generation #########################################

        ################################ Generate detail information #########################################
        detail_information = {"languages": "English", "accessibilities": ["Medium",	"Mobile/Desktop"],
                              "availabilities": "Limited Access"}
        detail_information["batches"] = {"batch_start_date": self.returnDate(
            self.get_value_from_key('course_start_date', nulearnCourseData))}
        # detail_information["languages"] = ["English", ]

        detail_information["duration"] = {
            "expected_duration":  course["expected_duration"], "expected_duration_unit":  course["expected_duration_unit"]}

        course["detail_information"] = detail_information

        course["pricing"] = {"pricing_type": "Paid", "currency": "INR", "regular_price": self.get_value_from_key(
            'course_fee', nulearnCourseData), "sale_price": self.get_value_from_key('course_fee', nulearnCourseData),
            "finance_option": True, "financing_option": "EMI","finance_details": self.get_emi(nulearnCourseData)
                             }
        course["provider_information"] = {
            "provider": {
                "name": self.get_value_from_key('institute_name', nulearnCourseData),
                "currency": "INR",
                "country": "India"
            },
            "provider_url": "https://www.nulearn.in/courses/" + self.get_value_from_key('course_url', nulearnCourseData)
        }
        course["prerequisites"] = self.generate_prerequisites_from_eligibility(
            self.get_value_from_key('eligibility', nulearnCourseData))
        faculties = self.get_value_from_key("faculty", nulearnCourseData)
        instructors = []
        if faculties != None and len(faculties) > 0:
            facultiesData = json.loads(faculties)
            for faculty in facultiesData:
                instructor = {
                    "name": faculty["fac_name"],
                    "instructor_bio": faculty["fac_leading"],
                    "designation": "",
                    "image_url": "MEDIA::https://via.placeholder.com/300.png"
                }
                instructors.append(instructor)
        else:
            instructors = [{
                    "name": '',
                    "designation": '',
                    "instructor_bio": '',
                    "image_url": "MEDIA::"
                    }]
        course["instructors"] = instructors
        course["meta_information"] = {
            # "external_source_id" : course["id"],
            "meta_title": self.get_value_from_key("mtitle", nulearnCourseData),
            "meta_description": self.get_value_from_key("mdesc", nulearnCourseData),
            "meta_keywords": self.get_value_from_key("mkeywords", nulearnCourseData),
            "add_type": "import",
            "import_source": "Nulearn",
            "provider": "nulearn",
        }
        chapters = self.get_value_from_key("chapters", nulearnCourseData)
        if chapters != None:
            course["topics"] = self.get_topics_fromjson(chapters)

        reviews = self.getReviewsFromTestimonials(
            self.get_value_from_key("testimonials", nulearnCourseData))
        course["reviews"] = reviews

        return course

    def getReviewsFromTestimonials(self, testimonials):
        reviews = []
        try:
            testmonialArray = json.loads(testimonials)
            for testmonial in testmonialArray:
                review = {"reviewer_name": testmonial["p_name"], "review": testmonial["per_desc"],  "review_date": datetime.now(
                ).isoformat(),  "rating": 10}
                reviews.append(review)
        except Exception as e:
            print("invalid testmonial json")
            return [{
                "reviewer_name": " ",
                "review_date": datetime.now().isoformat(),
                "review":  " ",
                "rating": 10,
            }]
        return reviews

    def get_topics_fromjson(self, chapters):
        topics = []
        chaptersArray = json.loads(chapters)
        # print(chaptersArray)
        for chapter in chaptersArray:
            if chapter["pid"] == "null":
                topics.append(chapter["name"])
                # topic = {
                #     'id' : chapter['id'],
                #     'default_display_label': chapter['name'],
                #     'slug' : chapter['name'].replace(" ", "_")
                # }
                # topics.append(topic)
        return topics

    def get_content_from_chapters(self, chapters):
        chaptersArray = json.loads(chapters)
        content = "<p><ol>"
        i = 0
        for chapter in chaptersArray:
            if chapter['pid'] == 'null':
                if i == 0:
                    content = content + "<li>" + chapter['name'] + "</li><ul>"
                    i = i+1
                else:
                    content = content + "</ul><li>" + \
                        chapter['name'] + "</li><ul>"
            else:
                content = content + "<li>" + chapter['name'] + "</li>"

        content = content + "</ul></ol></p>"
        return content

    def generate_prerequisites_from_eligibility(self, eligibility):
        prerequisites_list = []
        if eligibility != None:
            clean = re.compile('<.*?>')
            eligibility = re.sub(clean, '', eligibility)
            prerequisites_lines = str(eligibility).splitlines()[0:]
            for pre_req in prerequisites_lines:
                if len(pre_req) > 0:
                    prerequisites_list.append({'option': pre_req[0:250]})

        return prerequisites_list

    def get_value_from_key(self, key, data):
        if key in data:
            return data[key]
        return None

    def returnDate(self, date):
        if date:
            if('Coming Soon' in date):
                return None
            d = dateutil.parser.parse(date.replace('-',''))
            return d.isoformat()
        return None
    
    def get_emi(self, nulearnCourseData):
        finance_string = '' + self.get_value_from_key("tenure01", nulearnCourseData) +": " + self.get_value_from_key("emi01", nulearnCourseData) + "\n"
        finance_string = finance_string + self.get_value_from_key("tenure02", nulearnCourseData) +": " + self.get_value_from_key("emi02", nulearnCourseData) + "\n"
        finance_string = finance_string + self.get_value_from_key("tenure_wint1", nulearnCourseData) +": " + self.get_value_from_key("emi_win_emi1", nulearnCourseData) + "\n"
        finance_string = finance_string + self.get_value_from_key("tenure_wint2", nulearnCourseData) +": " + self.get_value_from_key("emi_win_emi2", nulearnCourseData) + "\n"
        finance_string = finance_string + self.get_value_from_key("tenure_wint3", nulearnCourseData) +": " + self.get_value_from_key("emi_win_emi3", nulearnCourseData) + "\n"
        
        return finance_string
