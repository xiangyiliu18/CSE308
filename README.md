# CSE308 Stony Brook
Project for Course CSE 308
> ### Overview
---
- Super Canvasser helps organizations run door-to-door canvassing campaigns (salescampaign, fund-raising campaign, election campaign, opinion poll, etc.).
- The system supports three roles: 
  - **Campaign Managers**: who manage the information associated with campaigns; 
  - **Canvassers**: who visit the locations in campaigns on assigned dates;
  - **System Administrator**s, who manage user accounts
This is a admin, manager, canvasser system for survey and questionnaire management.

> ### Functionalities for different roles
---
- **Campaign Managers**
  - Create, View and Edit campaigns
  - Create and View canvassing assignment
  - View campaign results via map and statistical summary
- **Canvassers**
  - Edit own availability
  - View upcomming canvassing assignments
  - Canvass
    - Displaying the address with travel directions to next location
    - Supporting to change the next location to be visted manually
- **System Administrator**
  - Edit Users Data
  - Edit global parameters which are used to compute assignments

> ### Techs used
---
- Back-End: Python, Flask
- DataBase: MySQL
- Front-End: HTML/CSS, jQuery, JavaScript
- Version Control: Git
- Others: gunicorn, sqlalchemy,pymysql, ortools, googlemaps
