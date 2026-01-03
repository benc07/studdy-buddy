from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

user_session_table = db.Table(
    "user_session_association",
    db.Model.metadata,
    db.Column("session_id", db.Integer, db.ForeignKey("sessions.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
)

user_interest_table = db.Table(
    "user_interest_association",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("interest_id", db.Integer, db.ForeignKey("interests.id"))
)

class User(db.Model):
    """
    User model
    """
    __tablename__ = "users"
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    google_id=db.Column(db.String, unique=True, nullable=False)
    name=db.Column(db.String, nullable=False)
    email=db.Column(db.String, unique=True, nullable=False)
    profile_picture=db.Column(db.String)
    major_id = db.Column(db.Integer, db.ForeignKey("majors.id"))
    major = db.relationship("Major", back_populates="users")
    interests = db.relationship("Interest", secondary=user_interest_table, back_populates="users")
    sessions=db.relationship("Session", secondary=user_session_table, back_populates="students", passive_deletes=True)
    friendships=db.relationship("Friend", foreign_keys="[Friend.user_id]", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

    @classmethod
    def get_by_google_id(cls, google_id):
        """
        Return the user associated with the given Google ID
        """
        return cls.query.filter_by(google_id=google_id).first()
    
    def __init__(self,**kwargs):
        """
        Initialize User object/entry
        """
        self.google_id = kwargs.get("google_id","")
        self.name = kwargs.get("name","")
        self.email = kwargs.get("email","")
        self.profile_picture =  kwargs.get("profile_picture","")
        self.major = None
        self.interests= []
        self.sessions = []

    def serialize(self):
        """
        Serialize a user object
        """
        return{
            "id": self.id,
            "google_id": self.google_id,
            "name": self.name,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "major": self.major.serialize() if self.major else None,
            "interests": [i.simple_serialize() for i in self.interests] if self.interests else [],
            "sessions": [s.simple_serialize() for s in self.sessions] if self.interests else [],
            "friendships": [s.simple_serialize() for s in self.friendships]
        }
    
    def simple_serialize(self):
        """
        Serialize a simple user object
        """
        return{
            "id": self.id,
            "name": self.name,
            "email": self.email
        }
    
class Course(db.Model):
    """
    Course model
    """
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    sessions = db.relationship("Session", back_populates="course", cascade='delete')

    def __init__(self, **kwargs):
        """
        Initializes a Course instance with code and name.
        """
        self.code=kwargs.get("code","")
        self.name=kwargs.get("name","")

    def serialize(self):
        """
        Serializes the course including its sessions.
        """
        return{
            "id": self.id,
            "code":self.code,
            "name": self.name,
            "sessions": [s.simple_serialize() for s in self.sessions]
        }
    def simple_serialize(self):
        """
        Serializes the course without session details.
        """
        return{
            "id": self.id,
            "code": self.code,
            "name": self.name
        }
    
    
class Session(db.Model):
    """
    Session model
    """
    __tablename__ = "sessions"
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    class_number = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    time = db.Column(db.String)
    course = db.relationship("Course", back_populates="sessions")
    students=db.relationship("User",secondary=user_session_table, back_populates="sessions", passive_deletes=True)

    def __init__(self,**kwargs):
        """
        Initializes a Session instance with course information.
        """
        self.course_id = kwargs.get("course_id")
        self.class_number = kwargs.get("class_number")
        self.name = kwargs.get("name")
        self.time=kwargs.get("time")

    def serialize(self):
        """
        Serializes the session including course and student details.
        """
        return {
            "id": self.id,
            "class_number": self.class_number,
            "name": self.name,
            "time": self.time,
            "course": self.course.simple_serialize(),
            "students": [s.simple_serialize() for s in self.students]
        }
    
    def simple_serialize(self):
        """
        Serializes the session without course and student details.
        """
        return {
            "id": self.id,
            "class_number": self.class_number,
            "name": self.name,
            "time": self.time
        }


class Friend(db.Model):
    """
    Friend model
    """
    __tablename__="friends"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String, default = 'Pending', nullable=False)
    user = db.relationship("User",foreign_keys=[user_id], back_populates="friendships")
    friend = db.relationship("User", foreign_keys=[friend_id], passive_deletes=True)

    def __init__(self, **kwargs):
        """
        Initializes a Friend relationship instance.
        """
        self.user_id = kwargs.get("user_id")
        self.friend_id = kwargs.get("friend_id")
        self.status = kwargs.get("status")

    def serialize(self):
        """
        Serializes the friendship including friend details.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "friend_id": self.friend_id,
            "status": self.status,
            #"friend": self.friend.simple_serialize()
        }
    
    def simple_serialize(self):
        """
        Serializes the friendship only with friend's id and status
        """
        return{
            "friend_id": self.friend_id,
            "status": self.status
        }
    
    
class Message(db.Model):
    """
    Message Model
    """
    __tablename__="messages"
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = db.Column(db.String, nullable=False)
    sent_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    sender = db.relationship("User", foreign_keys=[sender_id], passive_deletes=True)
    receiver = db.relationship("User", foreign_keys=[receiver_id], passive_deletes=True)

    def __init__(self, **kwargs):
        """
        Initializes a Message instance with sender, receiver, and content.
        """
        self.sender_id = kwargs.get("sender_id")
        self.receiver_id = kwargs.get("receiver_id")
        self.content = kwargs.get("content", "")
        self.sent_at = kwargs.get("sent_at")

    def serialize(self):
        """
        Serializes the message including sender and receiver details.
        """
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "sent_at": self.sent_at.isoformat(),
            "sender": self.sender.simple_serialize(),
            "receiver": self.receiver.simple_serialize()
        }
    
    def simple_serialize(self):
        """
        Serializes the message only with content.
        """
        return{
            "content": self.content
        }  

class Major(db.Model):
    """
    Major model
    """
    __tablename__ = "majors"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    major = db.Column(db.String, unique=True, nullable=False)
    users = db.relationship("User", back_populates="major")

    def __init__(self, **kwargs):
        """
        Initializes a Major instance.
        """
        self.major = kwargs.get("major", "")

    def serialize(self):
        """
        Serializes the major with all fields.
        """
        return {
            "id": self.id,
            "major": self.major
        }

class InterestCategory(db.Model):
    """
    InterestCategory model.
    """
    __tablename__="interest_categories"
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    interests=db.relationship("Interest", back_populates="category", cascade="all, delete", passive_deletes=True)
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")

    def serialize(self):
        """
        Serializes an InterestCategory instance.
        """
        return {
            "id": self.id,
            "name": self.name,
            "interests": [i.simple_serialize() for i in self.interests]
        }

    def simple_serialize(self):
        """
        Serializes without interests.
        """
        return {
            "id": self.id,
            "name": self.name
        }
    
class Interest(db.Model):
    """
    Interest model.
    """
    __tablename__ = "interests"
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    category_id=db.Column(db.Integer, db.ForeignKey("interest_categories.id"), nullable=False)
    category = db.relationship("InterestCategory", back_populates="interests")
    users = db.relationship("User", secondary=user_interest_table, back_populates="interests", passive_deletes=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        if kwargs.get("category_id") is not None:
            self.category_id = kwargs.get("category_id")
        else:
            category_name = kwargs.get("category")
            category = InterestCategory.query.filter_by(name=category_name).first()
            if category:
                self.category_id = category.id
            else:
                category = InterestCategory(name=category_name)
                db.session.add(category)
                db.session.commit()
                self.category_id = category.id

    def serialize(self):
        """
        Serializes an Interest instance.
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.simple_serialize(),
            "users": [u.simple_serialize() for u in self.users]
        }

    def simple_serialize(self):
        """
        Serializes an Interest instance without users' information.
        """
        return {
            "id": self.id,
            "name": self.name,
            "category_id": self.category_id
        }
    

