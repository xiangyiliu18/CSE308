from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session
)
from werkzeug.exceptions import abort
from database import db_session, User, CanAva, Role, CampaignCanvasser, Assignment, CampaignLocation, Campaign, Questionnaire, Result, TaskLocation
import json
import logging
import datetime
import time
import re
from locking import theLock

# Create canvasser blueprint
bp = Blueprint('canvasser', __name__, url_prefix='/canvasser')

''' Global variables '''
user_email="" #### Keep the canvasser's email to be avaliable for getting User, Role Object #####

''' Key = Assignment Object; Value = List of TaskLocation object'''
assignments={}  ## store all assignments 
past_assignments={}  ## store past assignments which date value less than today
upcoming_assignments={} ## store upcoming assignments which date value not less than today
'''Key = fdsf, Value ='''
detail={} ### work_for view_detail_assignment

today = datetime.date.today()  ## get today's date yyyy-mm-dd


### update the availability dates for the canvasser#######
@bp.route('/update_ava')
def update_ava():
	theLock.acquire()
	# Fetching info from the calendar implemented in canvasser
	title = request.args.get('title')
	start = request.args.get('start')
	############ Change Date string to Date object (yyyy-mm-dd)
	dateStrings = start.split()
	dateString = dateStrings[3] + " " + dateStrings[1] + " " + dateStrings[2]
	struc = time.strptime(dateString, '%Y %b %d')
	startDate = datetime.date(struc.tm_year, struc.tm_mon, struc.tm_mday)

	''' Create CanAva object,and add it to DB'''
	ava_obj = CanAva(startDate)
	''' Query Role Id firstly, the get the CanAva obj'''
	role_obj = db_session.query(Role).filter(Role.email == user_email, Role.role == 'canvasser').first()
	role_obj.roles_relation_2.append(ava_obj)
	db_session.commit()

	logging.info("updating availability for email "+user_email+" with "+" the date on "+start)
	theLock.release()
	return 'update'

### remove the availability dates for the canvasser ###
@bp.route('/remove_ava')
def remove_ava():
	theLock.acquire()
	# Fetching info from the calendar implemented in canvasser
	title = request.args.get('title')
	start = request.args.get('start')
	############ Change Date string to Date object (yyyy-mm-dd)
	dateStrings = start.split()
	dateString = dateStrings[3] + " " + dateStrings[1] + " " + dateStrings[2]
	struc = time.strptime(dateString, '%Y %b %d')
	startDate = datetime.date(struc.tm_year, struc.tm_mon, struc.tm_mday)

	''' Query Role Id firstly, the query CanAva obj'''
	role_obj = db_session.query(Role).filter(Role.email == user_email, Role.role == 'canvasser').first()
	ava_obj = db_session.query(CanAva).filter(CanAva.role_id == role_obj.id, CanAva.theDate == startDate).first()
	db_session.delete(ava_obj)
	db_session.commit()

	logging.info("delete available date for email "+user_email+" with "+" the date on "+start)
	theLock.release()
	return 'remove'


# Method for rendering the canvasser's homepage
@bp.route('/canPage/<u_name>', methods=('GET', 'POST'))
def canPage(u_name):
	global user_email
	global assignments
	global past_assignments
	global upcoming_assignments
	global today

	''' The first time to load assignments for the canvasser'''
	assignments={}
	past_assignments={}
	upcoming_assignments={}
	'''The first time to load canvasser's email'''
	user_email = session['info']['email']
	session['info']['account'] = 'canvasser'
	session.modified = True
 
	#### Query Role Object from DB  #########
	role_obj = db_session.query(Role).filter(Role.email == user_email, Role.role =='canvasser').first()

	#### Load available dates of the canvasser to the calendar
	events = db_session.query(CanAva).filter(CanAva.role_id == role_obj.id).all()
	avails =[]
	if len(events)>0:
		for instance in events:
			avails.append({
				'title':"Avaliable",
				'constraint': 'Ava',
				'start':str(instance.theDate),
				'textColor':'black !important',
				'backgroundColor': "#FF3B30!important"
				})
	### One Canvasser Role object may have multiple corresponding campaingCanvasser Objects
	camp_canvassers = db_session.query(CampaignCanvasser).filter(CampaignCanvasser.role_id == role_obj.id).all()
	######### Load all assigmenets, past_assignments, upcoming_assignments ###
	for ele in camp_canvassers:
		## Get assignments of this canvasser for one specified Campign
		ass_obj = db_session.query(Assignment).filter(Assignment.canvasser_id == ele.id).all()
		for ass in ass_obj:
			### ass ---> One Assignment object(id, canvasser_id, theDate, done, two relation)
			###  Sort the TaskLocation list based on the value of the TaskLocation's order
			task_locs = ass.assignment_relation_task_loc
			task_locs.sort(key= lambda x: x.order)
			###  Retrieve location values for getting the marker later in html page
			assignments[ass] =ass.assignment_relation_task_loc
			if ass.theDate < today:
				past_assignments[ass] = assignments[ass]
			else:
				upcoming_assignments[ass] = assignments[ass]
			### show there're assignments on calendar
			avails.append({
				'title':"Have Assignment",
				'constraint': 'Ass',
				'start':str(ass.theDate),
				'textColor':'black !important',
				'backgroundColor': "#7FFFD4 !important"
				})

	if(len(avails) != 0):
		canvasEvents = json.dumps(avails)
		logging.debug("fetching info availability  and assignemnt from database for "+ user_email)
		logging.info("Load all information for the homepage of the canvasser with email: "+user_email)
		return render_template('canvasser_html/canvas.html',avails=canvasEvents, u_name=u_name)
	##### len(avails) = 0
	return render_template('canvasser_html/canvas.html',avails=None, u_name=u_name)


# Enter viewing upcomming assignment html page
@bp.route('/view_assignment/<u_email>')
def view_assignment(u_email):
	global assignments
	global today
	global past_assignments
	global upcoming_assignments

	if assignments=={}:
		'''Without any assignments'''
		flash("You do not have any assignments")
		return redirect(url_for('canvasser.canPage', u_name = session['info']['name']))
	'''if there're some assignments'''
	return render_template('canvasser_html/view_assignment.html',upcoming_assignments= upcoming_assignments, past_assignments= past_assignments, detail=None)


'''Work For viewingn assignment detail'''
@bp.route('/view_assignment_detail', methods=('GET', 'POST'))
def view_assignment_detail():
	global assignments
	global user_email
	global detail
	global upcoming_assignments
	global past_assignments

	if request.method == 'POST':
		print("view assignment detail")
		ass_id = request.form.get('assignment')
		if not ass_id:
			flash("Failed to view assignemnt detail because of the empty value")
			return redirect(url_for('canvasser.view_assignment', u_email=user_email))
		if ass_id == "None":
			return redirect(url_for('canvasser.view_assignment', u_email=user_email))
		'''Get non-empty Assignment ID'''
		ass_id = int(ass_id)
		detail={}
		''' Retrieve Canvasser Name'''
		canvasser = db_session.query(User).filter(User.email == user_email).first()
		detail['canvasser_name'] = canvasser.name
		''' Retrieve Assignment Object'''
		ass_obj = db_session.query(Assignment).filter(Assignment.id == ass_id).first()
		''' 
			When the key is assignment, the value is assignment object's relation
		'''
		detail['assignment'] = ass_obj
		''' Retrieve Compaign Canvasser object'''
		campaign_canavsser = db_session.query(CampaignCanvasser).filter(CampaignCanvasser.id == ass_obj.canvasser_id).first()
		detail['compaign_name'] = campaign_canavsser.campaign_name
		''' Retrieve multiple TaskLocation Objects'''
		detail['location'] = ass_obj.assignment_relation_task_loc #### For getting date and order values

		'''Get Specified Campaign Object'''
		camp = db_session.query(Campaign).filter(Campaign.name == campaign_canavsser.campaign_name).first()
		'''Get Questionaire'''
		detail['questions'] = camp.campaigns_relation_3
		'''Get Talking Point'''
		detail['talking'] = camp.talking
		return render_template('canvasser_html/view_assignment.html',upcoming_assignments= upcoming_assignments, past_assignments= past_assignments, detail=detail)
	return redirect(url_for('canvasser.view_assignment', u_email=user_email))



# Enter create_canvass html
@bp.route('/create_canvass')
def create_canvass():
	global assignments
	global user_email
	global today

	assignments = {}
	#### Query Role Object from DB  #########
	role_obj = db_session.query(Role).filter(Role.email == user_email, Role.role =='canvasser').first()
	### One Canvasser Role object may have multiple corresponding campaingCanvasser Objects
	camp_canvassers = db_session.query(CampaignCanvasser).filter(CampaignCanvasser.role_id == role_obj.id).all()
	######### Load all assigmenets, past_assignments, upcoming_assignments ###
	for ele in camp_canvassers:
		## Get assignments of this canvasser for one specified Campign
		ass_obj = db_session.query(Assignment).filter(Assignment.canvasser_id == ele.id).all()
		for ass in ass_obj:
			### ass ---> One Assignment object(id, canvasser_id, theDate, done, two relation)
			###  Sort the TaskLocation list based on the value of the TaskLocation's order
			task_locs = ass.assignment_relation_task_loc
			task_locs.sort(key= lambda x: x.order)
			###  Retrieve location values for getting the marker later in html page
			assignments[ass] =ass.assignment_relation_task_loc
			if ass.theDate < today:
				past_assignments[ass] = assignments[ass]
			else:
				upcoming_assignments[ass] = assignments[ass]

	ass_info={} 


	current_assignment=None  ## Keep current day's assignment
	for ele in assignments:
		if ele.theDate == today:
			current_assignment = ele
			break;

	if not current_assignment:
		flash("Fail to canvassing assingment creation.  You do not have current today assignment!")
		return redirect(url_for('canvasser.canPage', u_name = session['info']['name']))
	if current_assignment.done:
		flash("You do not have any more canvassing assignment today!!")
		return redirect(url_for('canvasser.canPage', u_name = session['info']['name']))
	''' You have current today's assignment'''
	### Find the most rec_visited location ###
	rec_visited = None
	unvisited = []
	
	for ele in current_assignment.assignment_relation_task_loc:
		if ele.visited:
			rec_visited = ele
		else:
			unvisited.append(ele)
	### sort unvisited 
	unvisited.sort(key= lambda x: x.order)

	''' Retrieve Campaign Canvasseer Object to get Campaign Name'''
	camp_obj =db_session.query(CampaignCanvasser).filter(CampaignCanvasser.id == current_assignment.canvasser_id).first()

	'''Retriving basic Campaign Info from Campaign'''
	campaign = db_session.query(Campaign).filter(Campaign.name == camp_obj.campaign_name).first()

	questions = db_session.query(Questionnaire).filter(Questionnaire.campaign_name == campaign.name).all()

	if not camp_obj:
		flash("Fail to canvassing assingment creation.No campaign!!")
		return redirect(url_for('canvasser.canPage', u_name = session['info']['name']))
	''' 
	the simplest assumption is that each canvasser starts the work day at the first location in the assigned task.
	if there's only one location in the assignment, then no travelled direction need to be shown
	'''
	locations = current_assignment.assignment_relation_task_loc

	ass_info['current_ass'] = current_assignment
	if not rec_visited:
		## if no most recently location, the first location should be the start location
		rec_visited = unvisited[0]
	ass_info['rec_visited'] = rec_visited
	ass_info['unvisited'] = unvisited
	ass_info['locations'] = locations
	ass_info['campaign_name'] = camp_obj.campaign_name
	ass_info['campaign'] = campaign
	ass_info['questions'] = questions

	return render_template('canvasser_html/create_canvass.html', ass_info = ass_info)


# Enter canvas_start html
@bp.route('/change_next_location', methods=['GET','POST'])
def change_next_location():
	if request.method == 'POST':
		global assignments
		print("Change Next Location")

		if request.method == 'POST':
			## format : TaskLocation.id|TaskLocation.assignment_id
			next_location = request.form['end']
			(task_id, ass_id) = next_location.split('|')

			all_locations = db_session.query(TaskLocation).filter(TaskLocation.assignment_id == int(ass_id)).all()
			task_loc = db_session.query(TaskLocation).filter(TaskLocation.id == task_id).first()
			
			all_unvisited=[]
			for ele in all_locations:
				if not ele.visited:
					all_unvisited.append(ele)
			all_unvisited.sort(key= lambda x: x.order)
			## Get the original order of the next location
			old_order = all_unvisited[0].order
			## Get the order of the new next location
			new_order = task_loc.order

			if(old_order != new_order):
				for ele in all_unvisited:
					if ele.order < new_order:
						ele.order += 1
					elif ele.order == new_order:
						ele.order = old_order
				db_session.commit()
				flash("Change Next Location Successfully!!")
			else:
				flash("You did not change the next location!!")

	return redirect(url_for("canvasser.create_canvass"))


####location--- TaskLocation.id
@bp.route('/submit_result/<location>', methods=['POST'])
def submit_result(location):
	global assignments
	global user_email
	location = db_session.query(TaskLocation).filter(TaskLocation.id == location).first()

	if request.method == 'POST':
		### Retrieve the data "spoke to"
		spoke_to = request.form['spoke_to'] ## value = 0/1
		if spoke_to == "0":
			spoke_to = False
		elif spoke_to == "1":
			spoke_to = True
		#### Retrieve the data "rating"
		rating = 0
		if 'rating' in request.form:
			rating = request.form['rating'] # value = 1/.../5
		### Retrieve the Assignment Data from DB
		temp_assign = db_session.query(Assignment).filter(Assignment.id == location.assignment_id).first()
		### Retrieve the Campaingn Canavsser from DB
		campaign_name=None
		campaign_canavsser = db_session.query(CampaignCanvasser).filter(CampaignCanvasser.id == temp_assign.canvasser_id).first()
		if campaign_canavsser:
			campaign_name = campaign_canavsser.campaign_name

		if campaign_name:
			camp_obj = db_session.query(Campaign).filter(Campaign.name == campaign_name).first()
			if(not camp_obj.start):
				camp_obj.start = True
				db_session.commit()

		### Retrieve Question String list from DB
		questions = db_session.query(Questionnaire).filter(Questionnaire.campaign_name == campaign_name).all()

		answers = ""
		quest = ""
		for q in questions:
			s=str(q.id)
			qq = request.form[s]
			##### 0|1|2|2|1.........
			answers += (qq + "|")
			### did you here?|did you like?|... 
			quest  += (str(q.question) +"|")

		brief_note = request.form['brief_note']

		result = Result(quest,answers,spoke_to,rating,brief_note)

		location.taskLocation_relation = result
		location.visited = True

		db_session.commit()

		''' Check if we finish all locations'''
		all_locations = db_session.query(TaskLocation).filter(TaskLocation.assignment_id == temp_assign.id).all()
		check_done = True
		for ele in all_locations:
			if not ele.visited:
				check_done = False
				break
		if check_done:
			temp_assign.done = True
			db_session.commit()
			flash("Submit Result Successfully! And no more visited locations")
			return redirect(url_for('canvasser.canPage', u_name = session['info']['name']))

		else:
			flash("Submit Result Successfully! Go to next location.")

	return redirect(url_for("canvasser.create_canvass"))
