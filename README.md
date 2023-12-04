# Basketball League Management System
Welcome to the basketball league management system. This application is developed using **Python 3.11.0**.

Please see below how to setup and run the application. 
Future improvements to the application are mentioned at the end.
## Setup
Clone the code, cd inside the root of this project and run:

`python manage.py makemigrations BasketballLeagueManagementSystem`  

`python manage.py migrate`  


Then run the management command to populate the database with seed data as below:

`python manage.py populate_db`
## Run Application
First create a virtual environment and install all the dependency requirements from **requirements.txt** file.
To run the application, cd inside the root of this project and run: 

`python manage.py runserver`  

The root URL of the application by default will be http://localhost:8000. 
To get a better idea of the data of users, players, coaches and games to test the application endpoints, 
check the JSON files and the **populate_db.py** file in the **management/commands** directory.
### Login
**Method**: `POST`  
**Endpoint**: `/login`  
**Payload**: `{
    "username": "kenzo.patterson",
    "password": "kenzo.patterson"
}`  
**Sample Response**: `{
    "token": "53dbbbdb2b8c2cca9410ca89c9d2ebbc3afd36ad"
}`  

Use this token for authorization and logging out. Add this token in the headers of the 
request for all other endpoints:  
`Authorization: Token 53dbbbdb2b8c2cca9410ca89c9d2ebbc3afd36ad`  

Above example is for league admin who has permissions to execute all endpoints.
### Logout
Accessible to all logged-in users.  

**Method**: `POST`  
**Endpoint**: `/logout`   
**Sample Response**: `{
    "success": "Successfully logged out"
}`  
### View Scoreboard
Accessible to all logged-in users. 

**Method**: `GET`  
**Endpoint**: `/scoreboard`   
**Sample Response**: `[
    {
        "team1": "Thunder Hawks",
        "team1Score": 102,
        "team2": "Eclipse Titans",
        "team2Score": 78,
        "winner": "Thunder Hawks",
        "type": "QUALIFIERS"
    },
    ...
]`  
### View Team Details
Accessible to all logged-in coaches and league admin. Coach cannot view other team's data.

**Method**: `GET`  
**Endpoint**: `/teams/{team_id}`  
**Sample Response**: `{
    "team": "Thunder Hawks",
    "avgScore": 102,
    "players": [
        "Liam Thompson",
        "Ethan Brooks",
        "Benjamin Hayes",
        "Oliver Richardson",
        "William Harrison",
        "James Cooper",
        "Lucas Parker",
        "Henry Sullivan",
        "Alexander Mitchell",
        "Michael Nelson"
    ]
}`    

`percentile` is an optional query parameter (should be between **0** and **100**):   

**Endpoint**: `/teams/{team_id}?percentile=90`  
**Sample Response**: `{
    "team": "Thunder Hawks",
    "percentile": 90,
    "percentileScore": 31,
    "playersInPercentile": [
        {
            "name": "William Harrison",
            "avgScore": 33
        }
    ]
}`
### View Player Details
Accessible to all logged-in users. Coach cannot view other team player's data. Player can view only his data.

**Method**: `GET`  
**Endpoint**: `/players/{player_id}`  
**Sample Response**: `{
    "name": "Liam Thompson",
    "height": "5'11\"",
    "numberOfGamesPlayed": 3,
    "avgScore": 11
}`
### View User Statistics
Accessible to all logged-in league admin only. `timeSpentOnline` is in seconds.

**Method**: `GET`  
**Endpoint**: `/stats`  
**Sample Response**: `[
    {
        "name": "Kenzo Patterson",
        "username": "kenzo.patterson",
        "isLoggedIn": "True",
        "loggedInCount": "7",
        "timeSpentOnline": "5507"
    },
    ...
]`
## Future Improvements
* User sign up
* Create, update and delete operations on games and teams
* Auditing application events
* Application logging
* Token expiry and refresh tokens to reduce login attempts
* Handle user authorization in middleware
* Appropriate response for non-existent teams and players
* Integration tests (missing due to time constraints)


