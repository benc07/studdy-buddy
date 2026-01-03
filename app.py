from db import db, User, Course, Session, Friend, Message, Major, InterestCategory, Interest
from flask import Flask, request
import json
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from dotenv import load_dotenv
import os
from fetch_classes import fetch_all, fetch_classes_for_subject
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

GOOGLE_CLIENT_ID="437789147226-3b2ssaljk3jsjkijel1jlo9tapjqi2k3.apps.googleusercontent.com"

db.init_app(app)
with app.app_context():
        db.create_all()

def success_response(data, code=200):
    """
    Return a standardized success response
    """
    return json.dumps(data), code

def failure_response(data, code=404):
    """
    Return a standardized failure response
    """
    return json.dumps({"error": data}), code

def fetch_course():
    """
    Fetch course data and update the database
    """
    print("Fetching start")
    fetch_all(app)
    return {"status": "ok"}, 200

def list_of_majors():
    """
    Initialize predefined major data
    """
    print("start")
    majors_list = [
            "Agricultural Sciences",
            "Animal Science",
            "Anthropology",
            "Applied Economics and Management",
            "Archaeology",
            "Architecture",
            "Asian Studies",
            "Astronomy",
            "Atmospheric Science",
            "Biological Engineering",
            "Biological Sciences",
            "Biology and Society",
            "Biomedical Engineering",
            "Biometry and Statistics",
            "Chemical Engineering",
            "Chemistry",
            "China and Asia-Pacific Studies",
            "Civil Engineering",
            "Classics",
            "Cognitive Science",
            "College Scholar",
            "Communication",
            "Comparative Literature",
            "Computer Science",
            "Design and Environmental Analysis",
            "Earth and Atmospheric Sciences",
            "Economics",
            "Electrical and Computer Engineering",
            "Engineering Physics",
            "English",
            "Entomology",
            "Environment and Sustainability",
            "Environmental Engineering",
            "Fashion Design and Management",
            "Fiber Science",
            "Fine Arts",
            "Food Science",
            "French",
            "German Studies",
            "Global and Public Health Sciences",
            "Global Development",
            "Government",
            "History",
            "Hotel Administration",
            "Human Biology, Health, and Society",
            "Human Development",
            "Information Science",
            "Landscape Architecture",
            "Linguistics",
            "Materials Science and Engineering",
            "Mathematics",
            "Mechanical Engineering",
            "Music",
            "Nutritional Sciences",
            "Operations Research and Engineering",
            "Performing and Media Arts",
            "Philosophy",
            "Physics",
            "Plant Sciences",
            "Psychology",
            "Public Policy",
            "Religious Studies",
            "Sociology",
            "Spanish",
            "Statistical Science",
            "Undecided",
            "Urban and Regional Studies",
        ]
    with app.app_context():
        for m in majors_list:
            if not Major.query.filter_by(major=m).first():
                db.session.add(Major(major=m))
        db.session.commit()
        return {"status": "ok"}, 200
    
def list_of_interests():
    """
    Initialize predefined interest categories and interests data
    """
    categories_list={
        "Music": [
            "Pop", "Rock", "Jazz", "Classical", "Hip-hop", "Electronic",
            "Guitar", "Piano", "Drums", "Violin", "Saxophone"
        ],
        "Sports": [
            "Soccer", "Basketball", "Tennis", "Running", "Swimming", "Rock Climbing"
        ],
        "Reading": [
            "Fiction", "Non-fiction", "Science Fiction", "Fantasy", "Comics", "Poetry"
        ],
        "Games": [
            "Video Games", "Board Games", "Card Games", "Tabletop RPG", "Chess"
        ],
        "Outdoors": [
            "Hiking", "Camping", "Bird Watching", "Gardening", "Surfing"
        ],
        "Food": [
            "Cooking", "Baking", "Wine Tasting", "Coffee", "Tea", "Beer Brewing"
        ],
        "Art": [
            "Painting", "Sculpting", "Photography", "Drawing", "Knitting", "Sewing"
        ],
        "Tech": [
            "Programming", "Robotics", "Astronomy", "AI", "Electronics"
        ]
        }
    with app.app_context():
        for c in categories_list:
            category =  InterestCategory.query.filter_by(name=c).first()
            if not category:
                category = InterestCategory(name=c)
                db.session.add(category)
                db.session.flush()
            for i in categories_list[c]:
                interest = Interest.query.filter_by(name=i).first()
                if not interest:
                    interest= Interest(name=i, category_id=category.id)
                    db.session.add(interest)
        db.session.commit()
        return {"status": "ok"}, 200

@app.route("/")
def index():
    """
    Endpoint that returns a simple health check status.
    """
    return success_response({"status": "ok", "message": "backend running"}, 200)

# ------------------- GOOGLE LOGIN -------------------
@app.route("/auth/google", methods=["POST"])
def google_login():
     """
     Endpoint for Handling Google OAuth login 
     """
     try:
        body=json.loads(request.data)
        token=body.get("token_id")
        if not token:
            return failure_response("Missing ID Token", 400)
        idinfo=id_token.verify_oauth2_token(token, grequests.Request())
        print("TOKEN AUD:", idinfo.get("aud"))
        print("EXPECTED:", GOOGLE_CLIENT_ID)
        if idinfo["aud"] not in [GOOGLE_CLIENT_ID]:
            return failure_response("Invalid audience", 400)
        user_id=idinfo["sub"]
        email=idinfo.get("email")
        name=idinfo.get("name")
        picture=idinfo.get("picture")
        user=User.get_by_google_id(user_id)
        if not user:
            user = User(google_id=user_id, email=email, name=name, profile_picture=picture)
            db.session.add(user)
            db.session.commit()
        return success_response(user.serialize(), 201)
     except Exception as e:
          print("GOOGLE TOKEN ERROR:", str(e))
          return failure_response("Invalid token", 400)
     

# ------------------- USER ROUTES -------------------
@app.route("/users/")
def get_all_user():
     """
     Endpoint for getting all users
     """
     users = []
     for user in User.query.all():
        users.append(user.serialize())
     return success_response({"users": users})

@app.route("/users/<int:user_id>/")
def get_user_by_id(user_id):
     """
     Endpoint for getting user by id
     """
     user = User.query.filter_by(id=user_id).first()
     if user is None:
        return failure_response("User not found!")
     return success_response(user.serialize())

@app.route("/users/<int:user_id>/", methods=["POST"])
def update_user(user_id):
     """
     Endpoint for updating user profile
     
     Example input: 
     {
        "major": "Computer Science",
        "profile_picture": "https://example.com/me.jpg",
        "interests": [
            { "name": "Guitar", "category": "Music" },
            { "name": "Programming", "category": "Tech" },
            { "name": "Pottery", "category": "Art" }
        ]
     }
     """
     body=json.loads(request.data)
     major = body.get("major")
     interests = body.get("interests",[])
     profile_picture = body.get("profile_picture")
     user = User.query.filter_by(id=user_id).first()
     if user is None:
        return failure_response("User not found!")
     if major:
        major_obj = Major.query.filter_by(major=major).first()
        if not major_obj:
            return failure_response("Invalid major", 400)
        user.major = major_obj
     interest_list = []
     for name in interests:
        interest_name = name.get("name")
        category_name = name.get("category")
        if not interest_name or not category_name:
            continue 
        category = InterestCategory.query.filter_by(name=category_name).first()
        if not category:
            category = InterestCategory(name=category_name)
            db.session.add(category)
            db.session.flush()
        interest_obj = Interest.query.filter_by(name=interest_name, category_id=category.id).first()
        if not interest_obj:
            interest_obj = Interest(name=interest_name, category_id = category.id)
            db.session.add(interest_obj)
            db.session.commit()
        interest_list.append(interest_obj)
     user.interests = interest_list
     if not profile_picture is None:
         user.profile_picture=profile_picture 
     db.session.commit()
     return success_response(user.serialize(), 200)

@app.route("/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for removing user by ID
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!", 404)
    db.session.delete(user)
    db.session.commit()
    return success_response({"deleted_user": user.simple_serialize()}, 200)

@app.route("/users/<int:user_id>/friend/")
def get_friends(user_id):
    """
    Endpoint for getting all friends of a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
       return failure_response("User not found!")
    sent = Friend.query.filter_by(user_id=user_id, status="Accepted").all()
    received = Friend.query.filter_by(friend_id=user_id, status="Accepted").all()
    list=[]
    for items in sent:
        list.append(items.friend.simple_serialize())
    for items in received:
        list.append(items.user.simple_serialize())
    return success_response({"friends":list}, 200)

@app.route("/users/<int:user_id>/friend/<int:friend_id>/", methods=["POST"])
def send_friend_request(user_id, friend_id):
    """
    Endpoint for sending friend request
    """
    user = User.query.filter_by(id=user_id).first()
    friend = User.query.filter_by(id=friend_id).first()
    if not user or not friend:
        return failure_response("User not found", 404)
    current = Friend.query.filter(
        ((Friend.user_id==user_id) & (Friend.friend_id==friend_id)) | 
        ((Friend.user_id==friend_id) & (Friend.friend_id==user_id))
    ).first()
    if not current is None:
        return failure_response("Friendship already exists", 400)
    new = Friend(user_id=user_id, friend_id=friend_id, status="Pending")
    db.session.add(new)
    db.session.commit()
    return success_response(new.serialize(), 201)
    
@app.route("/users/<int:user_id>/friends/<int:friend_id>/", methods=["POST"])
def respond_request(user_id, friend_id):
    """
    Endpoint for accepting or rejecting request

    Example input:
    {
    "action":"accept" # or "reject"
    }
    """
    body = json.loads(request.data)
    action = body.get("action")
    if action not in ["accept","reject"]:
        return failure_response("Invalid action", 400)
    current = Friend.query.filter(
        ((Friend.user_id==user_id) & (Friend.friend_id==friend_id)) | 
        ((Friend.user_id==friend_id) & (Friend.friend_id==user_id))
    ).first()
    if not current:
        return failure_response("Friendship not found", 404)
    if action=="accept":
        current.status = "Accepted"
        db.session.commit()
        return success_response(current.serialize(), 201)
    else:
        db.session.delete(current)
        db.session.commit()
        return success_response({"Friend request rejected"}, 200)
    
@app.route("/users/<int:user_id>/<int:friend_id>/", methods=["DELETE"])
def delete_friend(user_id, friend_id):
    """
    Endpoint for removing user by ID
    """
    friendship = Friend.query.filter(
            ((Friend.user_id == user_id) & (Friend.friend_id == friend_id)) |
            ((Friend.user_id == friend_id) & (Friend.friend_id == user_id))
                ).first()
    if not friendship:
            return failure_response("Friendship not found!", 404)
    db.session.delete(friendship)
    db.session.commit()
    return success_response(friendship.serialize(), 200)
  
# ------------------- COURSE ROUTES -------------------
@app.route("/courses/")
def get_courses():
    """
    Endpoint to get all the courses
    """
    courses = []
    for course in Course.query.all():
        courses.append(course.simple_serialize())
    return success_response({"courses": courses})

@app.route("/courses/<int:course_id>/")
def get_course_by_id(course_id):
    """
    Endpoint to get a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return failure_response("Course not found", 404)
    return success_response(course.serialize())

@app.route("/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    """
    Endpoint to delete a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return failure_response("Course not found", 404)
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize(), 200)

# ------------------- SESSION ROUTES -------------------
@app.route("/session/<int:session_id>/")
def get_sessions(session_id):
    """
    Endpoint to get a session by id
    """
    session = Session.query.filter_by(id=session_id).first()
    if not session:
        return failure_response("Session not found", 404)
    return success_response(session.serialize())

@app.route("/session/<int:session_id>/", methods=["DELETE"])
def delete_session(session_id):
    """
    Endpoint to delete a session by id
    """
    session = Session.query.filter_by(id=session_id).first()
    if not session:
        return failure_response("Session not found", 404)
    db.session.delete(session)
    db.session.commit()
    return success_response(session.serialize(), 200)

# ------------------- SCHEDULE ROUTES -------------------
@app.route("/users/<int:user_id>/schedule/")
def get_user_schedule(user_id):
    """
    Endpoint to get all sessions from a user's schedule
    """
    user=User.query.filter_by(id=user_id).first()
    if not user:
        return failure_response("User not found", 404)
    list= [s.serialize() for s in user.sessions]
    return success_response({"sessions": list}, 200)

@app.route("/users/<int:user_id>/schedule/<int:session_id>/", methods=["POST"])
def add_session_to_schedule(user_id, session_id):
    """
    Endpoint to add a session to a user's schedule
    """
    user=User.query.filter_by(id=user_id).first()
    if not user:
        return failure_response("User not found", 404)
    session=Session.query.filter_by(id=session_id).first()
    if not session:
        return failure_response("Session not found", 404)
    if session in user.sessions:
        return failure_response("Session already in schedule", 400)
    user.sessions.append(session)
    db.session.commit()
    return success_response(user.serialize(), 201)

@app.route("/users/<int:user_id>/schedule/<int:session_id>/", methods=["DELETE"])
def remove_session_from_schedule(user_id, session_id):
    """
    Endpoint to remove a session from a user's schedule
    """
    user=User.query.filter_by(id=user_id).first()
    if not user:
        return failure_response("User not found", 404)
    if not session_id:
        return failure_response("Invalid body information", 400)
    session=Session.query.filter_by(id=session_id).first()
    if not session:
        return failure_response("Session not found", 404)
    if session in user.sessions:
        user.sessions.remove(session)
        db.session.commit()
    return success_response(user.serialize(), 200)

# ------------------- MESSAGE ROUTES -------------------
@app.route("/messages/send/", methods=["POST"])
def send_message():
    """
    Endpoint that send message from one user to another
    """
    body=json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    content = body.get("content", "")
    if not sender_id or not receiver_id or not content:
        return failure_response("Invalid body information", 400)
    sender = User.query.get(sender_id)
    receiver = User.query.get(receiver_id)
    if not sender or not receiver:
        return failure_response("User not found", 404)
    message = Message(sender_id=sender_id,receiver_id=receiver_id,content=content)
    db.session.add(message)
    db.session.commit()
    return success_response(message.serialize(), 201)

@app.route("/messages/<int:user_id>/<int:friend_id>/")
def get_conversation(user_id, friend_id):
    """
    Endpoint that get the conversation between two users
    """
    user=User.query.filter_by(id=user_id).first()
    friend=User.query.filter_by(id=friend_id).first()
    if not user or not friend:
        return failure_response("User not found", 404)
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == user_id))
    ).order_by(Message.sent_at).all()
    return success_response({"messages": [m.simple_serialize() for m in messages]}, 200)

@app.route("/messages/<int:user_id>/conversations/")
def get_inbox_preview(user_id):
    """
    Endpoint that get the latest message from each conversation for a user
    """
    user=User.query.filter_by(id=user_id).first()
    if not user:
        return failure_response("User not found", 404)
    messages = Message.query.filter(
        (Message.sender_id==user_id)|(Message.receiver_id==user_id)
    ).order_by(Message.sent_at.desc()).all()
    conversations = {}
    for items in messages:
        if items.sender_id==user_id:
            friend_id=items.receiver_id
        else:
            friend_id=items.sender_id
        if friend_id not in conversations:
            conversations[friend_id]=items.simple_serialize()
    return success_response({"conversations": conversations}, 200)

@app.route("/messages/<int:message_id>/", methods=["DELETE"])
def delete_message(message_id):
    """
    Deletes a message a user has sent
    """
    message=Message.query.filter_by(id=message_id).first()
    if not message:
        return failure_response("Message not found", 404)
    result = message.serialize()
    db.session.delete(message)
    db.session.commit()
    return success_response(result, 200)

# ------------------- SEARCH ROUTES -------------------
@app.route("/courses/search/")
def search_courses():
    """
    Endpoint to get a list of courses based on a query string

    Example url:  http://127.0.0.1:8000/courses/search/?q=math
    """
    query = request.args.get("q","")
    query = query.strip()
    if len(query)<3:
        return success_response({"courses":[], "sessions":[]})
    courses = Course.query.filter(
        (Course.code.ilike(f"%{query}%"))|(Course.name.ilike(f"%{query}%"))
    ).all()
    return success_response({"courses":[c.simple_serialize() for c in courses]}, 200)

@app.route("/users/<int:user_id>/match/", methods=["POST"])
def match_buddy(user_id):
    """
    Endpoint that returns a list of suggested buddies in same session or course based on majors and interests

    Example input:
    {
        "course_code": "Math1920",
        "session_ids": [2, 12]  #optional
    }
    """
    body=json.loads(request.data)
    code = body.get("course_code")
    session_ids = body.get("session_ids",[])
    if not code:
        return failure_response("Invalid body information", 400)
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return failure_response("User not found", 404)
    course = Course.query.filter_by(code=code).first()
    if not course:
        return failure_response("Course not found", 404)
    if session_ids:
        sessions = Session.query.filter(Session.id.in_(session_ids)).all()
    else:
        session_ids= [s.id for s in course.sessions]
        sessions = Session.query.filter(Session.id.in_(session_ids)).all()
    if not sessions:
        return failure_response("Session not found", 404)
    potential=[]
    for s in sessions:
        for student in s.students:
            if student.id!=user.id and student not in potential:
                potential.append(student)

    user_major_id = user.major.id if user.major else None
    user_interest_ids = {i.id for i in user.interests}
    user_category_ids = {i.category_id for i in user.interests}

    matches=[]

    for buddy in potential:
        score=0
        if user_major_id and buddy.major and buddy.major.id == user_major_id:
            score+=30
        buddy_interests = buddy.interests
        buddy_interest_ids = {i.id for i in buddy_interests}
        buddy_category_ids = {i.category_id for i in buddy_interests}
        common_interests = user_interest_ids.intersection(buddy_interest_ids)
        score+=15*len(common_interests)
        common_categories = user_category_ids.intersection(buddy_category_ids)
        category_bonus = max(0, len(common_categories)-len(common_interests))
        score+=5*category_bonus
        matches.append({"student": buddy.simple_serialize(), "score": score})
    
    matches.sort(key=lambda x: x["score"], reverse=True)
    return success_response({"matches": matches[:10]}, 200)    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)