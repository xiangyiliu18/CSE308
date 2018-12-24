from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session
)
from werkzeug.exceptions import abort
from database import db_session, User, Campaign, Role,CampaignLocation,CampaignCanvasser, CampaignManager, Questionnaire, Assignment, GlobalVariables, CanAva, TaskLocation, Result
from sqlalchemy.sql.expression import func
from gmap import key
import googlemaps
from assignmentCreator import makeAssign
import datetime
from datetime import date
import math
from locking import theLock
import logging

user_email="" #### Keep the canvasser's email to be avaliable for getting User, Role Object #####

detail={} ### work_for view_detail_assignment

today = datetime.date.today()  ## get today's date yyyy-mm-dd


#link google map
gmaps = googlemaps.Client(key = key)

#create the manager blueprint
bp = Blueprint('manager', __name__, url_prefix='/manager')

''' Store All Campaigns Info : Key = campaign Name ; Value = Detail Info the specified Campaign'''
camp = {}

view_all_camp_ass={}
view_ass_detail={}
view_camp_obj=None

''' Create Assignment for one Campaing'''
def createAssignment(newCamp):
	'''
	newCamp---> campaign Object
	'''
	# flag for marking the assignment the campaign as possible
	assignmentPossible = False

	# get headquarters for starting location for routing algorithm
	globalVars = db_session.query(GlobalVariables).first()
	hq = (0, 0, 'address')
	# get campaign location data
	locations = []
	# add the headquarters to the location set
	locations.append(hq)
	# add all campaign locations to the locations set
	locations_relation = newCamp.campaigns_relation_2
	for ele in locations_relation:
		locations.append((ele.lat, ele.lng, ele.location))

	# get the start and end dates of the campaign
	startDate = newCamp.startDate
	endDate = newCamp.endDate
	#print(locations)
	# make assignments with the routing alorithm
	assignments = makeAssign(locations, newCamp.duration)
	#print("assignments %s" %assignments)
	#print(assignments)
	dates = [] ###### Store the Valid CanAva Objects

	''' Get all Campaign Canvassers'''
	camp_canvassers = newCamp.campaigns_relation_1
	for ele in camp_canvassers:
		''' Get all this Campaign Canvasser's all avaliable dates'''
		canDates = db_session.query(CanAva).filter(CanAva.role_id == ele.role_id).all()
		for ele_ava in canDates:
			if ele_ava.theDate >= startDate and ele_ava.theDate <= endDate:
				dates.append(ele_ava)

	'''sort dates by earliest available CanAva objects'''
	dates.sort(key= lambda d: d.theDate)

	# assign assignments to dates
	mappedAssignments = {}  ### Key = Canvasser'role_id Value = CanAva and assignment
	while(len(dates) > 0 and len(assignments) > 0):
		dTemp = dates.pop(0)  #### CanAva
		aTemp = assignments.pop(0)  #####  list of set(lat, lng)

		if(dTemp.role_id in mappedAssignments):
			mappedAssignments[dTemp.role_id].append((dTemp,aTemp))
		else:
			mappedAssignments[dTemp.role_id] = [(dTemp, aTemp)]
	
	#if no more assingments then this mapping is possible
	if(len(assignments) == 0):
		assignmentPossible = True

	## add assignments to database
	for ele in mappedAssignments:  ## Key---> Role Id ; Value= the serveral list of [(CanAva, assingment),(...)]
		# ele is the key---> role_id
		campCanvasser= db_session.query(CampaignCanvasser).filter(CampaignCanvasser.campaign_name == newCamp.name, CampaignCanvasser.role_id == ele).first()
		## mappedAssignments[ele]--> sets of (CanAva, assignment)
		for ele_ass  in mappedAssignments[ele]:
			###### ele_ass =one set (CanAva, assignment)
			### ele_ass[0] --- CanAva
			### ele_ass[1] -- assignment
			ass_obj = Assignment(ele_ass[0].theDate, False)

			## ele_ass[1] -----[(lat, lng), (lat1, lng1)....]
			for order in range(len(ele_ass[1])):
				lat = ele_ass[1][order][0] 
				lng = ele_ass[1][order][1]
				locString = ele_ass[1][order][2]
				#print(locString)
				## Get location from the campaign location db
				allCampLocation =db_session.query(CampaignLocation).filter(CampaignLocation.campaign_name == newCamp.name).all()
				### Get campLocation Object, and retrieve location address string: loc
				''' campLocation = [one campaignLocation object]'''
				campLocation = [loc for loc in allCampLocation if (math.isclose(loc.lat, lat) and math.isclose(loc.lng, lng) and (loc.location == locString))]
				loc = campLocation[0].location
				#### Create Task Location Object  #########
				task_loc_obj = TaskLocation(loc,lat,lng,order)
				''' Add TaskLocation Object to Assignment Obejct'''
				ass_obj.assignment_relation_task_loc.append(task_loc_obj)

			''' Add the new created Assignment Object to CampaignCanvasser Obejct'''
			#print(campCanvasser)
			campCanvasser.canvasser_relation.append(ass_obj)
			#print(ass_obj)
			db_session.commit()

			# remove taken dates out of available in the database
			# Delet(CanAva)
			db_session.delete(ele_ass[0])
			db_session.commit()

	return assignmentPossible



#function to render the manager page and set the manager page url
@bp.route('/manpage', methods=('GET', 'POST'))
def manPage():
	########### View Campaign Is the First Page #########################
	global user_email
	session['info']['account'] = 'manager'
	user_email = session['info']['email']
	session.modified = True
	return redirect(url_for('manager.viewCampaign'))


@bp.route('/view_campaign')
def viewCampaign():
	global user_email
	if len(camp) !=0:   ############### Reload Campaings Info from  datebase
		camp.clear()
	role_obj = db_session.query(Role).filter(Role.email == user_email, Role.role == "manager").first()
	''' Retrieve all Campaigns'''
	all_camp = db_session.query(CampaignManager).filter(CampaignManager.role_id == role_obj.id).all()

	campaigns=[]

	for ele in all_camp:
		ele_camp = db_session.query(Campaign).filter(Campaign.name == ele.campaign_name).first()
		campaigns.append(ele_camp)

	###### Loop for retrieving each campaign info
	for  obj in campaigns:
		camp_ele =[]
		camp_ele.append(obj) # camp_ele[0] = campaign 

		managers= [] #### Store all manager user objects for each campaign
		for ele in obj.campaigns_relation:
			manager_role = db_session.query(Role).filter(Role.id == ele.role_id).first()
			manager_user = db_session.query(User).filter(User.email == manager_role.email).first()
			managers.append(manager_user)
		camp_ele.append(managers)  # camp_ele[1] = manager

		canvassers = []  #### Store all canvasser user objects for each campaign
		for ele in obj.campaigns_relation_1:
			canvasser_role = db_session.query(Role).filter(Role.id == ele.role_id).first()
			canvasser_user = db_session.query(User).filter(User.email == canvasser_role.email).first()
			canvassers.append(canvasser_user)
		camp_ele.append(canvassers) # camp_ele[2] = canvasser

		locations = [] #### Store all location objects for each campaign
		for ele in obj.campaigns_relation_2:
			locations.append(ele)
		camp_ele.append(locations) # camp_ele[3] = locations

		questions= [] #### Store all question objects for each campaign
		for ele in obj.campaigns_relation_3:
			questions.append(ele)
		camp_ele.append(questions) # camp_ele[4] = questions

		
		''' Retrieve Campaign Canvasseer Object to get Campaign Name'''
		cans = db_session.query(CampaignCanvasser).filter(CampaignCanvasser.campaign_name == obj.name).all()
		'''Gets All Assignemnt object for this Campaign'''
		assignment_list =[]
		for c in cans:
			assignedCanvasser = db_session.query(Assignment).filter(Assignment.canvasser_id == c.id).all()
			for a in assignedCanvasser:
				assignment_list.append(a)

		'''w'''
		location_obj = []
		for a in assignment_list:
			loc = db_session.query(TaskLocation).filter(TaskLocation.assignment_id == a.id).all()
			for l in loc:
				tup = (l.location, l.visited)
				location_obj.append(tup)
		camp_ele.append(location_obj)

		camp[obj.name] = camp_ele
	return render_template('manager_html/view_campaign.html', camp=camp, name = None, camp_list = [], index =0 )


''' Selecct One Campaign, And View its Details'''
@bp.route('/view_campaign_detail/', methods=('POST','GET'))
def viewCampaignDetail():
	print("Enter View Campaign Detail\n")
	campaign_name = request.form['campaign-name']
	name = request.form['action']  # Managers/Canvassers/Locations/Questions
	if(name == "Managers"):
		return render_template('manager_html/view_campaign.html', camp=camp, name = campaign_name,camp_list = camp[campaign_name][1], index =1)
	elif (name == "Canvassers"):
		return render_template('manager_html/view_campaign.html', camp=camp, name = campaign_name,camp_list = camp[campaign_name][2], index =2)
	elif (name == "Locations"):
		return render_template('manager_html/view_campaign.html', camp=camp, name = campaign_name, camp_list = camp[campaign_name][3], index =3)
	elif (name == "Questions"):
		return render_template('manager_html/view_campaign.html', camp=camp, name = campaign_name, camp_list = camp[campaign_name][4], index =4)
	else:
		return render_template('manager_html/view_campaign.html', camp=camp, name = None, camp_list =[], index = 0)



@bp.route('/create_campaign/<u_email>', methods=['GET','POST'])
def createCampaign(u_email):
	global assignments
	''' Key is 'email', Value is 'name'''
	all_managers={}
	all_canvassers={}

	'''Get all managers from db '''
	manager_roles = db_session.query(Role).filter(Role.role == 'manager', Role.email != u_email).all()
	for ele in manager_roles:
		ele_user = db_session.query(User).filter(User.email == ele.email).first()
		all_managers[ele.email] = ele_user.name

	'''Get all cavasser from db'''
	canvasser_roles = db_session.query(Role).filter(Role.role == 'canvasser').all()
	for ele in canvasser_roles:
		ele_user = db_session.query(User).filter(User.email == ele.email).first()
		all_canvassers[ele.email] = ele_user.name

	''' For submit button'''
	if request.method == 'POST':
		theLock.acquire()
		campaign_name = request.form['name'] # string
		startDate = request.form['start_date'] #string 2018-11-26
		endDate = request.form['end_date'] 
		talking = request.form['talking'] #string 
		duration = request.form['duration']  # string : default = 1
		managers = request.form.getlist('managers')  ## list of emails
		canvassers = request.form.getlist('canvassers') ## list of emails
		questions_text = request.form['questions_text']  #string (multi-lines)
		locations = request.form['locations_text'] #string (multi-lines)s
		#print("%s %s %s %s %s %s %s %s %s" %(campaign_name, startDate, endDate, talking, duration, managers, canvassers, questions_text, locations))
		
		

		if not (campaign_name and startDate and endDate and duration and locations):
			flash("Failed to create campaign, there're empty values!!")
			theLock.release()
			return render_template('manager_html/create_campaign.html', managers = all_managers, canvassers = all_canvassers, index = 5)
		## No empty
		## Add campaign's creator
		managers.append(u_email)
		questions=[] ### split quqestion with new line into one list 

		if questions_text != None and questions_text.strip() !="":
			questions = questions_text.split("\n")

		valid_locations =[]  #### Store valiad locations(address, lat, lng)

		''' Check if locations are valid or not'''
		if locations != "" :
			 locations_arr = locations.split('\n')
			 for ele in locations_arr:
			 	if(gmaps.geocode(ele) == []):
			 		flash("Failed to create campaign, the address("+ele+") is not valid!!")
			 		theLock.release()
			 		return render_template('manager_html/create_campaign.html', managers = all_managers, canvassers = all_canvassers, index = 5)
			 	lat = gmaps.geocode(ele)[0]['geometry']['location']['lat']
			 	lng = gmaps.geocode(ele)[0]['geometry']['location']['lng']
			 	address=gmaps.geocode(ele)[0]['formatted_address']
			 	test = (address,lat, lng)
			 	'''Check if there're some repeated locations'''
			 	if test in valid_locations:
			 		flash("Failed to create campaign, the address: ("+address+") is repeated!!!")
			 		theLock.release()
			 		return render_template('manager_html/create_campaign.html', managers = all_managers, canvassers = all_canvassers, index = 5)
			 	else:
			 		valid_locations.append((address,lat, lng))

		#print("valid location list---> %s" %valid_locations)

		''' Create New Campaign Object'''
		check_camp = db_session.query(Campaign).filter(Campaign.name == campaign_name).first()
		if(check_camp):
			flash("This Campaign Name already exists, please enter the unique campaign name!")
			theLock.release()
			return render_template('manager_html/create_campaign.html', managers = all_managers, canvassers = all_canvassers, index = 5)
		''' New Campaign Object'''
		newCamp = Campaign(campaign_name,startDate,endDate,talking,int(duration))
		db_session.add(newCamp)

		''' Add all managers to the newCamp relationship,'''
		for ele in managers:
			ele_obj = CampaignManager()
			role_obj = db_session.query(Role).filter(Role.email == ele, Role.role == 'manager').first()
			role_obj.roles_relation.append(ele_obj)
			newCamp.campaigns_relation.append(ele_obj)

		''' Add all canvassers to the newCamp relationship-1, androle relationship-1'''
		for ele in canvassers:
			ele_obj = CampaignCanvasser()
			role_obj = db_session.query(Role).filter(Role.email == ele, Role.role == 'canvasser').first()
			role_obj.roles_relation_1.append(ele_obj)
			newCamp.campaigns_relation_1.append(ele_obj)

		''' Add all questions to the newCamp relationship-3'''
		for ele in questions:
			if ele.strip() !="":
				ele_obj = Questionnaire(ele)
				newCamp.campaigns_relation_3.append(ele_obj)

		''' Add all locationto the newCamp relationship-2'''
		for ele in valid_locations:
			ele_obj =  CampaignLocation(ele[0], float(ele[1]), float(ele[2]))
			newCamp.campaigns_relation_2.append(ele_obj)

		db_session.commit()

		#if not enough dates/canvassers display warning
		if(not createAssignment(newCamp)):
			flash("Create Campagin successfully, but did not make compeletely assingments !")
		else:
			flash("Create Compaingn and make compeletely assignments successfully !")
		theLock.release()
		return redirect(url_for('manager.manPage'))

	return render_template('manager_html/create_campaign.html', managers = all_managers, canvassers = all_canvassers, index = 5)



####### Action == "Edit Campaign"
@bp.route('/edit_campaign/<u_email>', methods=['GET','POST'])
def editCampaign(u_email):
	global assignments

	''' Retrieve all Campaigns fistlly'''
	all_campaigns = db_session.query(Campaign).all()
	''' Key is 'email', Value is 'name'''
	all_managers={}
	all_canvassers={}

	'''Get all managers '''
	manager_roles = db_session.query(Role).filter(Role.role == 'manager').all()
	for ele in manager_roles:
		ele_user = db_session.query(User).filter(User.email == ele.email).first()
		all_managers[ele.email] = ele_user.name
	'''Get all cavasser'''
	canvasser_roles = db_session.query(Role).filter(Role.role == 'canvasser').all()
	for ele in canvasser_roles:
		ele_user = db_session.query(User).filter(User.email == ele.email).first()
		all_canvassers[ele.email] = ele_user.name

	if request.method == 'POST':
		if request.form['submit'] == 'select_campaign':
			campaign_name = request.form['campaign_list']

			campaign = db_session.query(Campaign).filter(Campaign.name == campaign_name).first()
			campaign_manager = campaign.campaigns_relation
			campaign_canvasser = campaign.campaigns_relation_1
			campaign_location = campaign.campaigns_relation_2
			campaign_question = campaign.campaigns_relation_3

			###here is all the manager assign to the campaign
			managers={}
			for cm in campaign_manager:
				cm_email = db_session.query(Role).filter(Role.id == cm.role_id).first().email
				cm_user = db_session.query(User).filter(User.email == cm_email).first()
				managers[cm_email] = cm_user.name

			###here is all the canvasser assign to the campaign
			canvassers={}
			for cc in campaign_canvasser:
				cc_email = db_session.query(Role).filter(Role.id == cc.role_id).first().email
				cc_user = db_session.query(User).filter(User.email == cc_email).first()
				canvassers[cc_email] = cc_user.name

			###
			#comparing two dictionary 
			###
			unselected_managers=all_managers
			all(map(unselected_managers.pop, managers))

			unselected_canvassers=all_canvassers
			all(map(unselected_canvassers.pop, canvassers))

			return render_template('manager_html/edit_campaign.html', campaign_name = campaign_name, all_campaigns = all_campaigns, unselected_managers = unselected_managers, unselected_canvassers = unselected_canvassers, managers = managers, canvassers=canvassers, start_date = campaign.startDate, end_date = campaign.endDate, talking=campaign.talking, question=campaign_question, location=campaign_location, duration=campaign.duration,index = 6)


		elif request.form['submit'] == 'submit_change':
			theLock.acquire()
			old_campaign_name = request.form['campaign_list']
			new_campaign_name = request.form['name']
			startDate = request.form['start_date']
			endDate = request.form['end_date']
			talking = request.form['talking']
			duration = request.form.get('duration')  # default = ''
			managers = request.form.getlist('managers')  ## format = email
			canvassers = request.form.getlist('canvassers') ## format = email
			questions_text = request.form['questions_text']  #string (multi-lines)
			locations_text = request.form['locations_text'] #string (multi-lines)s  ## format = address|lat|lng

			current_campaign = db_session.query(Campaign).filter(Campaign.name == old_campaign_name).first()
			####### if campaign already started some assignment, you can not modify it
			if current_campaign.start:
				flash("Failed to change, Some assignments already started!!")
				theLock.release()
				return redirect(url_for('manager.manPage'))

			if old_campaign_name != new_campaign_name:
				new_camp = db_session.query(Campaign).filter(Campaign.name == new_campaign_name).first()
				if new_camp:
					flash("Failed to change, Please change to new unique Campaign Name!!")
					theLock.release()
					return redirect(url_for('manager.manPage'))

			if new_campaign_name is '':
				current_campaign.name = old_campaign_name
			else:
				current_campaign.name = new_campaign_name
				
			questions=[] ### split quqestion with new line into one list 
			if questions_text != None and questions_text.strip() !="":
				questions = questions_text.split("\n")

			locations =[]  #### Store valiad locations(address, lat, lng)

			''' Check if locations are valid or not'''
			if locations_text != "" :
				 locations_arr = locations_text.split('\n')
				 for ele in locations_arr:
				 	if(gmaps.geocode(ele) == []):
				 		flash("Failed to create campaign, the address("+ele+") is not valid!!")
				 		theLock.release()
				 		return render_template('manager_html/create_campaign.html', managers = all_managers, canvassers = all_canvassers, index = 5)
				 	lat = gmaps.geocode(ele)[0]['geometry']['location']['lat']
				 	lng = gmaps.geocode(ele)[0]['geometry']['location']['lng']
				 	address=gmaps.geocode(ele)[0]['formatted_address']
				 	test = (address,lat, lng)
				 	'''Check if there're some repeated locations'''
				 	if test in locations:
				 		flash("Failed to create campaign, the address: ("+address+") is repeated!!!")
				 		theLock.release()
				 		return render_template('manager_html/create_campaign.html', managers = all_managers, canvassers = all_canvassers, index = 5)
				 	else:
				 		locations.append((address,lat, lng))

			current_campaign.startDate = startDate
			current_campaign.endDate = endDate
			current_campaign.talking = talking
			current_campaign.duration = duration

			## Keep the old canvassers list
			all_camp_can =[]## (campaign_canvasser obj)
			for ele in current_campaign.campaigns_relation_1:
				all_camp_can.append(ele)

			current_campaign.campaigns_relation = []
			current_campaign.campaigns_relation_1 = []
			current_campaign.campaigns_relation_2 = []
			current_campaign.campaigns_relation_3 = []

			db_session.commit()

			for ele in managers:
				ele_obj = CampaignManager()
				role_obj = db_session.query(Role).filter(Role.email == ele, Role.role == 'manager').first()
				role_obj.roles_relation.append(ele_obj)
				current_campaign.campaigns_relation.append(ele_obj)

			''' Add all canvassers to the newCamp relationship-1, androle relationship-1'''
			for ele in canvassers:
				ele_obj = CampaignCanvasser()
				role_obj = db_session.query(Role).filter(Role.email == ele, Role.role == 'canvasser').first()
				role_obj.roles_relation_1.append(ele_obj)
				current_campaign.campaigns_relation_1.append(ele_obj)

			''' Add all questions to the newCamp relationship-3'''
			for ele in questions:
				if ele.strip() !="":
					ele_obj = Questionnaire(ele)
					current_campaign.campaigns_relation_3.append(ele_obj)

			''' Add all locationto the newCamp relationship-2'''
			for ele in locations:
				ele_obj =  CampaignLocation(ele[0], float(ele[1]), float(ele[2]))
				current_campaign.campaigns_relation_2.append(ele_obj)

			db_session.commit()

			'''Need to  re-assign taskes, So we need to give back to canvasser their available dates'''
			## Get all Campaign canvasser

			## all_camp_can= set of (role_id, campaign_canvaser_id)
			for ele in all_camp_can:
				can_ass = ele.canvasser_relation
				if len(can_ass) > 0:
					for instance in can_ass:
						ass_date = instance.theDate
						ava_obj = CanAva(ass_date)
						role_obj = db_session.query(Role).filter(Role.id == ele.role_id).first()
						role_obj.roles_relation_2.append(ava_obj)
						db_session.commit()

			#if not enough dates/canvassers display warning
			if(not createAssignment(current_campaign)):
				flash("Create Campaign successfully, but did not make compeletely assingments !")
			else:
				flash("Create Campaign and make compeletely assignments successfully !")
			theLock.release()
			return redirect(url_for('manager.manPage'))
	else:
		if all_campaigns == []:
			flash("You do not have any campaigns need to be edited.")
			return redirect(url_for('manager.manPage'))

		return render_template('manager_html/edit_campaign.html', all_campaigns = all_campaigns,index = 6)


''' Method for deleting Campaing'''
@bp.route('/delete_campaign/<campName>/', methods=('GET', 'POST'))
def delete(campName):
    if request.method == 'POST':
    	deletedCamp = db_session.query(Campaign).filter(Campaign.name == campName).first()
    	if deletedCamp is not None:
    		''' Find the deletedCamp, and delete'''
    		db_session.delete(deletedCamp)
    		db_session.commit()
    		flash("Delete the Campaign Successfully","info")
    return redirect(url_for('manager.viewCampaign'))



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@bp.route('/view_result', methods=('GET','POST'))
def view_result():
	assign_obj = db_session.query(Assignment).all()
	assign_info = []
	for a in assign_obj:
		locations = db_session.query(TaskLocation).filter(TaskLocation.assignment_id == a.id ).all()
		locationCount = len(locations)

		canvas = db_session.query(CampaignCanvasser).filter(CampaignCanvasser.id  == a.canvasser_id ).first()

		canvasser = db_session.query(Role).filter(Role.id == canvas.role_id).first()

		canvasser_name = db_session.query(User).filter(User.email == canvasser.email).first().name

		camp = db_session.query(Campaign).filter(canvas.campaign_name == Campaign.name).first()
		duration = camp.duration
		tup = (a.id, locationCount, duration, a.theDate,locations,canvasser_name,camp.name)
		assign_info.append(tup)

	if request.method == 'POST':
		assign_id = request.form['assignment']

		assignment = db_session.query(Assignment).filter(Assignment.id == int(assign_id)).first()

		locations = db_session.query(TaskLocation).filter(TaskLocation.assignment_id == int(assign_id)).all()

		###query for all results with the location###
		task_results = []
		for l in locations:
			task_results.append(l.taskLocation_relation)


		campaign_name = db_session.query(CampaignCanvasser).filter(CampaignCanvasser.id == assignment.canvasser_id).first().campaign_name

		campaign = db_session.query(Campaign).filter(Campaign.name == campaign_name).first()

		statistic = {}
		if assignment.done:
			result= []
			for l in locations:
				result.append(db_session.query(Result).filter(Result.taskLocation_id == l.id).first())
			
			sum_rating= 0
			answers = []
			question_length = 0
			
			for r in result:
				sum_rating += r.rating
				answers.append(r.answers.split('|')[:-1])
				question_length = len(r.answers.split('|')[:-1])

			questions = result[0].questions.split('|')[:-1]

			temq = []
			for q in questions:
				temq.append(q.rstrip())

			questions = temq
			print(questions)

			###fixing the answer list###
			answers_fix =[]
			for i in range(question_length):
				answers_fix.append([item[i] for item in answers])

			answers = []
			for af in answers_fix:
				yes = 0
				no = 0
				dontcare = 0
				for a in af:
					if a == "0":
						no+=1
					elif a == "1":
						yes+=1
					elif a == "2":
						dontcare+=1
				answers.append([yes,no,dontcare])

			avg_rating = sum_rating/len(result)

			######standard deviation#####
			one = 1/len(result)

			total = 0
			for r in result:
				total+=math.pow(r.rating-avg_rating,2)

			statistic['deviation'] = math.pow((one*total),0.5)
			#######



			statistic['avg_rating'] = avg_rating
			statistic['answers'] = answers #answer are in list format of [yes #, no #, dontcare #]
			statistic['questions'] = questions

		return render_template('manager_html/view_result.html', assign_info=assign_info, locations = locations, assignment = assignment, campaign = campaign,statistic = statistic,task_results = task_results)

	if assign_info == []:
		flash("You do not any results which are available to be viewed!")
		return redirect(url_for('manager.manPage'))
	return render_template('manager_html/view_result.html', assign_info=assign_info)

@bp.route('/view_assignment/<u_email>', methods=('GET', 'POST'))
def view_assignment(u_email):
	print("View Assignment")
	global view_all_camp_ass
	global view_ass_detail
	global view_camp_obj

	all_camp_ass ={} ## key= campaingn object; value = all_ass,
	all_ass = {} ## Key is One Assignment Object, Value = (user_obj, multiple taskLocation Objects)
	c_obj=None
	role_obj = db_session.query(Role).filter(Role.email == u_email, Role.role == "manager").first()

	''' Retrieve ll Campaigns'''
	all_camp = db_session.query(CampaignManager).filter(CampaignManager.role_id == role_obj.id).all()

	for ele in all_camp:
		camp = db_session.query(Campaign).filter(Campaign.name == ele.campaign_name).first()

		'''Retrieve all Campaign Canvasser'''
		all_camp_can =camp.campaigns_relation_1
		for instance in all_camp_can:
			## Get Assignments
			instance_role = db_session.query(Role).filter(Role.id ==instance.role_id).first()
			instance_user = db_session.query(User).filter(User.email == instance_role.email).first()
			ass = instance.canvasser_relation
			for e_ass in ass:
				all_ass[e_ass] = (instance_user, e_ass.assignment_relation_task_loc)
		all_camp_ass[camp] = all_ass

	ass_detail = {}

	if request.method == 'POST':
		camp = request.form['campaign_list']
		if (not camp) or (camp == 'null'):
			flash("You need to select one campaign to view detail")
			return render_template('manager_html/view_assignment.html', all_camp_ass=all_camp_ass, ass_detail=ass_detail,camp_obj=c_obj, index = 7)

		c_obj = db_session.query(Campaign).filter(Campaign.name == camp).first()
		if c_obj in all_camp_ass:
			ass_detail = all_camp_ass[c_obj]

		view_all_camp_ass=all_camp_ass
		view_ass_detail=ass_detail
		view_camp_obj=c_obj

	return render_template('manager_html/view_assignment.html', all_camp_ass=all_camp_ass, ass_detail=ass_detail, camp_obj=c_obj, index = 7, loc=[])


@bp.route('/view_assignment_id/<assigmentId>', methods=('GET', 'POST'))
def view_assignment_id(assigmentId):
	global view_all_camp_ass
	global view_ass_detail
	global view_camp_obj

	ass_id = int(assigmentId)
	loc_obj = db_session.query(TaskLocation).filter(TaskLocation.assignment_id == ass_id).all()

	loc = []
	for l in loc_obj:
		tup = (l.location, l.lat, l.lng)
		loc.append(tup)

	return render_template('manager_html/view_assignment.html', all_camp_ass=view_all_camp_ass, ass_detail=view_ass_detail, camp_obj=view_camp_obj, index = 7, loc= loc)