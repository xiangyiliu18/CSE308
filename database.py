from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, Boolean, Float, String, Date, Text, ForeignKey, UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import relationship
from datetime import date
import pymysql

# Database connection string example
# 'mysql+pymysql://username:password@address:port/databaseName'
# Connect to the database with the database connection string
engine = create_engine('mysql+pymysql://xiangyiliu:111308288@mysql3.cs.stonybrook.edu:3306/xiangyiliu', convert_unicode=True)
#engine = create_engine('mysql+pymysql://cmbeck:108518007@mysql3.cs.stonybrook.edu:3306/cmbeck', convert_unicode=True)
#engine = create_engine('mysql+pymysql://xiangli5:110445032@mysql3.cs.stonybrook.edu:3306/xiangli5', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,bind=engine))
# Make the sqlalchemy object relation mapper base class
Base = declarative_base()
Base.query = db_session.query_property()


# Function to initalize the database
def init_db():
    Base.metadata.create_all(bind=engine)

''' Database table models/object relational classes'''

class User(Base):
    __tablename__ = 'users'

    email = Column(String(80), primary_key=True)
    password = Column(String(255), nullable=False)
    name = Column(String(80), nullable=False)
    avatar = Column(String(160), nullable=True, default ="None")
    ##########  One User Can Have Multiple Roles(Canvasser, Admin, Managers)
    users_relation = relationship('Role', backref='users', cascade="all,save-update,delete-orphan", lazy = True)

    def __init__(self,email, password, name,avatar):
        self.email = email
        self.password = password
        self.name = name
        self.avatar = avatar

    def __repr__(self):
        return "<User(email='%s', password='%s', avatar='%s')>" % (self.email, self.password, self.avatar)


class Role(Base): 
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    email=Column(String(80), ForeignKey('users.email', onupdate="CASCADE", ondelete="CASCADE")) #User's email
    role= Column(String(20), nullable=False)  ####### (canvasser, manager, admin)

    ################## Only manager role has this relationship, it refers to one or multiple campaings##############
    roles_relation = relationship("CampaignManager", backref= "roles",cascade="all,save-update, delete-orphan")
    ################## Only canvasser role has this relationship, it refers to one or multiple campaings##############
    roles_relation_1 = relationship("CampaignCanvasser", backref= "roles",cascade="all,save-update,delete-orphan")
    ################## Only canvasser role has this relationship, it refers to one or one on its available dates ##############
    roles_relation_2 = relationship("CanAva", backref= "roles",cascade="all,save-update,delete-orphan")

    UniqueConstraint(email, role)  

    # A collection of roles on User
    def __init__(self, role):
        self.role = role
    
    def __repr__(self):
        return "<Role(email='%s',role='%s')>" % (self.email,self.role)


class Campaign(Base):
    __tablename__ = 'campaigns'

    name = Column(String(80),  primary_key = True) 
    startDate = Column(Date, nullable=False)  ##  Formart = 2018-11-11
    endDate = Column(Date, nullable=False)
    talking = Column(Text, default="None", nullable= True) 
    duration = Column(Integer, default = 0, nullable=True)
    ## Mark if the compaign start some assingment or not
    start = Column(Boolean, default=False, nullable= False)

    ########## One Campaign has multiple Managers##############
    campaigns_relation= relationship("CampaignManager", backref = "campaigns",cascade="all,save-update,delete-orphan")
    ######### One Campaign has multiple Canvassers################
    campaigns_relation_1= relationship("CampaignCanvasser", backref = "campaigns",cascade="all,save-update,delete-orphan")
    ########## One campaign has multiple Locations###################
    campaigns_relation_2= relationship("CampaignLocation", backref = "campaigns",cascade="all,save-update,delete-orphan")
    ######### One campaign has multiple questions############
    campaigns_relation_3=relationship("Questionnaire",backref="campaigns",cascade="all,save-update,delete-orphan")

    def __init__(self, name, startDate, endDate,talking,duration):
        self.name = name
        self.startDate = startDate
        self.endDate = endDate
        self.talking = talking
        self.duration = duration

    def __repr__(self):
        return "<Campaign(name='%s', startDate='%s', endDate='%s')>" % (self.name, self.startDate, self.endDate)


class Questionnaire(Base):
    __tablename__ = 'questionnaires'

    id = Column(Integer, primary_key = True)
    campaign_name = Column(String(80),ForeignKey('campaigns.name', onupdate="CASCADE", ondelete="CASCADE"))
    question = Column(String(160),nullable = False)

    def __init__(self, question):
       self.question = question


class CampaignLocation(Base):   # Association Table (Campaign + Locations)
    __tablename__ = 'campaign_locations'

    id = Column(Integer, primary_key = True)
    campaign_name = Column(String(80),ForeignKey('campaigns.name', onupdate="CASCADE", ondelete="CASCADE") )
    location = Column(String(200),nullable=False)
    lat = Column(Float,nullable = False)
    lng = Column(Float,nullable = False)

    UniqueConstraint(campaign_name, location)

    def __init__(self,  location, lat, lng):
        self.location = location
        self.lat= lat
        self.lng = lng

    def __repr__(self):
        return "<Locations(Campaign name='%s', location='%s' lat ='%s')>" % (self.campaign_name, self.location, self.lat)



class CampaignManager(Base):   # Association Table (Campaign + ManagerRole)
    __tablename__ = 'campaign_managers'

    id = Column(Integer, primary_key = True)
    campaign_name = Column(String(80),ForeignKey('campaigns.name', onupdate="CASCADE", ondelete="CASCADE") )
    role_id = Column(Integer, ForeignKey('roles.id', onupdate="CASCADE", ondelete="CASCADE"))
    UniqueConstraint(campaign_name, role_id) 

    def __repr__(self):
        return "<Managers(Campaign name='%s', role_id='%s')>" % (self.campaign_name, self.role_id)


class CampaignCanvasser(Base):   # Association Table (Campaign + CanvasserRole)
    __tablename__ = 'campaign_canvassers'

    id = Column(Integer, primary_key = True)
    campaign_name = Column(String(80),ForeignKey('campaigns.name', onupdate="CASCADE", ondelete="CASCADE") )
    role_id = Column(Integer, ForeignKey('roles.id', onupdate="CASCADE", ondelete="CASCADE"))

    canvasser_relation=relationship("Assignment", backref="campaign_canvassers",cascade="all,save-update,delete-orphan")

    UniqueConstraint(campaign_name, role_id) # one canvasser + one campaign 

    def __repr__(self):
        return "<Canvassers(Campaign name='%s', role_id='%s')>" % (self.campaign_name, self.role_id)


class GlobalVariables(Base):
    __tablename__ = 'globals'

    id = Column(Integer, primary_key=True)
    workDayLength = Column(Integer, default = 1, nullable =False)
    averageSpeed = Column(Float, default = 1.0, nullable = False)

    def __init__(self, workDayLength, averageSpeed):
        self.workDayLength = workDayLength
        self.averageSpeed = averageSpeed

    def __repr__(self):
        return "<GlobalVariables(workDayLength='%d', averageSpeed='%f')>" % (self.workDayLength, self.averageSpeed)


class CanAva(Base):
    __tablename__='can_avas'  

    id = Column(Integer,primary_key = True)
    role_id = Column(Integer, ForeignKey('roles.id', onupdate="CASCADE", ondelete="CASCADE"))
    theDate = Column(Date, nullable= False)
    UniqueConstraint(role_id, theDate)

    def __init__(self,theDate):
        self.theDate = theDate  

    def __repr__(self):
        return "<CanAva(role_id='%d', theDate='%s')>" % (self.role_id, self.theDate)

###### One canvasser has one task in one day for a specified campaign #######
class Assignment(Base):
    __tablename__='assignments'

    id = Column(Integer, primary_key = True)
    canvasser_id = Column(Integer, ForeignKey('campaign_canvassers.id', onupdate="CASCADE", ondelete="CASCADE"))
    theDate = Column(Date, nullable= False)
    ########   Flag to check if the assginment is done or not
    done = Column(Boolean, nullable=False, default=False)

    ##### One assignment is like one task, but one task has multiple locations ######
    assignment_relation_task_loc= relationship("TaskLocation", backref="assignments",cascade="all,save-update,delete-orphan")
    UniqueConstraint(canvasser_id, theDate)

    def __init__(self,theDate, done):
        self.theDate = theDate
        self.done = done

    def __repr__(self):
        return "<Assignment( canvasser_id='%d', theDate='%s')>" % (self.canvasser_id, self.theDate)

####### One Task is a set of locations #############
class TaskLocation(Base):
    __tablename__='task_locations'

    id = Column(Integer, primary_key = True)
    assignment_id=Column(Integer, ForeignKey('assignments.id', onupdate="CASCADE", ondelete="CASCADE"))
    location = Column(String(200),nullable=False)
    lat = Column(Float,nullable = False)
    lng = Column(Float,nullable = False)
    order = Column(Integer, nullable = False)
    visited = Column(Boolean, nullable=False, default=False)

    UniqueConstraint(assignment_id, location)
    #UniqueConstraint(assignment_id, lat, lng)

    ##### One specified location has one result  ##########
    taskLocation_relation = relationship("Result", uselist=False, backref="task_locations", cascade="all,save-update,delete-orphan")


    def __init__(self, location, lat, lng, order):
        self.location = location
        self.lat = lat
        self.lng = lng
        self.order = order

    def __repr__(self):
        return "<TaskLocation('id='%d', location='%s', assignment_id='%d', order='%d')>" % (self.id, self.location, self.assignment_id, self.order)


## With One to One relation to TaskLocation
class Result(Base):
    __tablename__='result'

    id = Column(Integer, primary_key = True)
    taskLocation_id = Column(Integer, ForeignKey('task_locations.id', onupdate="CASCADE", ondelete="CASCADE"))
    questions = Column(Text, nullable = True) ## q1|q2|q3|q4
    answers = Column(Text, nullable = True)  # 0-no, 1-yes, 2-without
    ### answer format 0|1|0|1
    spoke_to = Column(Boolean, nullable= False, default=False)
    rating = Column(Integer, nullable= False, default=0)
    brief_notes = Column(Text, default="None", nullable=False)

    def __init__(self, questions,answers,spoke_to,rating, brief_notes):
        self.questions=questions
        self.answers = answers
        self.spoke_to = spoke_to
        self.rating = rating
        self.brief_notes = brief_notes

    def __repr__(self):
        return "<Result(result_id='%d', rating='%f', brief_notes='%s')>" % (self.id, self.rating, self.brief_notes)

# For populating the database for testing purposes.
if __name__ == "__main__":
    init_db()
    p1 = generate_password_hash('1234')
    ### Two with admin only
    user1 = User('cool_admin1@c.com', p1, 'Cool Admin1', 'None')
    user2 = User('cool_admin2@c.com', p1, 'Cool Admin2', 'None')
    db_session.add(user1)
    db_session.add(user2)

    admin_1 = Role('admin')
    admin_2 = Role('admin')
    user1.users_relation=[admin_1]
    user2.users_relation=[admin_2]

    ### Two with admin/manager/canvasser
    user3 = User('cool_all1@c.com', p1, 'Cool All1', 'None')
    db_session.add(user3)
    admin_3 = Role('admin')
    canvasser_1 = Role('canvasser')
    manager_1 = Role('manager')
    user3.users_relation=[admin_3,canvasser_1, manager_1]

    user4 = User('cool_all2@c.com', p1, 'Cool All2', 'None')
    db_session.add(user4)
    admin_4 = Role('admin')
    canvasser_2 = Role('canvasser')
    manager_2 = Role('manager')
    user4.users_relation=[admin_4,canvasser_2, manager_2]

    ### 13 managers
    user5 = User('cool_can1@c.com', p1, 'Cool Canvasser1', 'None')
    db_session.add(user5)
    canvasser_3 = Role('canvasser')
    user5.users_relation=[canvasser_3]

    user6 = User('cool_can2@c.com', p1, 'Cool Canvasser2', 'None')
    db_session.add(user6)
    canvasser_4 = Role('canvasser')
    user6.users_relation=[canvasser_4]

    user7 = User('cool_can3@c.com', p1, 'Cool Canvasser3', 'None')
    db_session.add(user7)
    canvasser_5 = Role('canvasser')
    user7.users_relation=[canvasser_5]

    user8 = User('cool_can4@c.com', p1, 'Cool Canvasser4', 'None')
    db_session.add(user8)
    canvasser_6 = Role('canvasser')
    user8.users_relation=[canvasser_6]

    user9 = User('cool_can5@c.com', p1, 'Cool Canvasser5', 'None')
    db_session.add(user9)
    canvasser_7 = Role('canvasser')
    user9.users_relation=[canvasser_7]

    user10 = User('cool_can6@c.com', p1, 'Cool Canvasser6', 'None')
    db_session.add(user10)
    canvasser_8 = Role('canvasser')
    user10.users_relation=[canvasser_8]

    user11 = User('cool_can7@c.com', p1, 'Cool Canvasser7', 'None')
    db_session.add(user11)
    canvasser_9 = Role('canvasser')
    user11.users_relation=[canvasser_9]

    user12 = User('cool_can8@c.com', p1, 'Cool Canvasser8', 'None')
    db_session.add(user12)
    canvasser_10 = Role('canvasser')
    user12.users_relation=[canvasser_10]

    user13 = User('cool_can9@c.com', p1, 'Cool Canvasser9', 'None')
    db_session.add(user13)
    canvasser_11= Role('canvasser')
    user13.users_relation=[canvasser_11]

    user14 = User('cool_can10@c.com', p1, 'Cool Canvasser10', 'None')
    db_session.add(user14)
    canvasser_12 = Role('canvasser')
    user14.users_relation=[canvasser_12]

    user15 = User('cool_can11@c.com', p1, 'Cool Canvasser11', 'None')
    db_session.add(user15)
    canvasser_13 = Role('canvasser')
    user15.users_relation=[canvasser_13]

    user16 = User('cool_can12@c.com', p1, 'Cool Canvasser12', 'None')
    db_session.add(user16)
    manager_14 = Role('canvasser')
    user16.users_relation=[manager_14]

    user17 = User('cool_can13@c.com', p1, 'Cool Canvasser13', 'None')
    db_session.add(user17)
    canvasser_15 = Role('canvasser')
    user17.users_relation=[canvasser_15]

    user18 = User('cool_man1@c.com', p1, 'Cool Manager1', 'None')
    db_session.add(user18)
    manager_3 = Role('manager')
    user18.users_relation=[manager_3]

    user19 = User('cool_man2@c.com', p1, 'Cool Manager2', 'None')
    db_session.add(user19)
    manager_4 = Role('manager')
    user19.users_relation=[manager_4]


    glo = GlobalVariables(360,60)
    db_session.add(glo)
    
    db_session.commit()




