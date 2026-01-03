import time 
import requests 
import json
from db import db, Course, Session

BASE_URL = "https://classes.cornell.edu/api/2.0"
ROSTER = "SP26"
API_TIMEOUT = 10
API_RATE_LIMIT = 1

def fetch_subjects():
    """
    Fetches the list of subjects for the configured roster from the Cornell classes API.
    """
    url = BASE_URL + "/config/subjects.json"
    result = requests.get(url, params={"roster":ROSTER}, timeout=API_TIMEOUT)
    if result.status_code!=200:
        raise Exception("Failed to get subjects")
    return result.json()["data"]["subjects"]

def fetch_classes_for_subject(subject):
    """
    Fetches all classes for a given subject from the Cornell classes API.
    """
    url = BASE_URL + "/search/classes.json"
    result = requests.get(url, params={"roster": ROSTER, "subject": subject}, timeout=API_TIMEOUT)
    if result.status_code!=200:
        print("Failed to get classes for"+subject)
        return []
    time.sleep(API_RATE_LIMIT)
    return result.json()["data"]["classes"]

def fetch_all(app):
    """
    Fetches all subjects and classes and syncs them into the local database.
    """
    subjects=fetch_subjects()

    with app.app_context():
        for subject in subjects:
            subject = subject["value"]
            classes = fetch_classes_for_subject(subject)
            for item in classes:
                course_code = item["subject"]+item["catalogNbr"]
                course_name = item["titleShort"]
                course = Course.query.filter_by(code=course_code).first()
                if course is None:
                    course = Course(code=course_code, name=course_name)
                    db.session.add(course)
                    db.session.commit()
                else:
                    if course.name!=course_name:
                        course.name=course_name 
                    if course.code!=course_code:
                        course.code=course_code 
                groups = item.get("enrollGroups",[])
                for group in groups:
                    sections = group.get("classSections",[])
                    for session in sections:
                        session_name = session["ssrComponent"]+session["section"]
                        class_number = str(session["classNbr"])
                        meeting = session.get("meetings",[])
                        if meeting!=[]:
                            time = meeting[0]["pattern"]+" "+meeting[0]["timeStart"]
                        else:
                            time = ""
                        existing = Session.query.filter_by(class_number=class_number).first()
                        if existing is None:
                            new_session = Session(course_id=course.id, class_number=class_number, name=session_name, time=time)
                            db.session.add(new_session)
                        else:
                            if existing.name!=session_name:
                                existing.name=session_name 
                            if existing.time!=time:
                                existing.time=time
                db.session.commit()

            
            

    