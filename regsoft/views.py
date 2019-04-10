# Imports
from django.shortcuts import render
import pyrebase
import datetime
import requests
import pytz
from django.contrib import auth
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string


# Initialize Firebase
config = {
    'apiKey': "AIzaSyAqy5TutrzfZ6vq0P9b7Vz-UsH7gKeUfY0",
    'authDomain': "rmfwsa-678cd.firebaseapp.com",
    'databaseURL': "https://rmfwsa-678cd.firebaseio.com",
    'projectId': "rmfwsa-678cd",
    'storageBucket': "rmfwsa-678cd.appspot.com",
    'messagingSenderId': "564967817070"
}

# firebase.initializeApp(config);
firebase = pyrebase.initialize_app(config)
authorisation = firebase.auth()
db = firebase.database() # gets the database
currentDate = datetime.datetime.now().strftime("%d/%m/%Y") 
dayofweek = datetime.datetime.today().strftime("%A")
print(dayofweek)
print(currentDate)


def foodmenuAPIRequest():
	loginUrl = 'http://118.185.138.207:8088/mobapi/login'
	menuUrl = 'http://118.185.138.207:8088/mobapi/foodmenu'


	headers = {
	            'Host':'118.185.138.207:8088',
	            'User-Agent': 'Mozilla/5.0 (compatible; Rigor/1.0.0; http://rigor.com)',
	            'Content-Type': 'application/json',
	            }

	r = requests.post(loginUrl, data='BUAPI', headers = headers)
	loginResponse=json.loads(r.text)
	refreshtoken = loginResponse['refreshtoken']

	r1 = requests.post(menuUrl, data=refreshtoken, headers = headers)
	menuResponse=json.loads(r1.text)
	days = {'Mon':'Monday','Tue':'Tuesday','Wed':'Wednesday','Thu':'Thursday','Fri':'Friday','Sat':'Saturday','Sun':'Sunday'}
	vald = {'B':'breakfast', 'D':'dinner','L':'lunch'}
	lst = []
	dct = {}
	for i in menuResponse:
	   lst.append([days[i['MENUDAY']],{vald[i['MENUTYPE']]:i['MENU'].split('$')}])
	for i in lst:
	    dct[i[0]] = dct.get(i[0],[])
	    dct[i[0]] = dct[i[0]] + [i[1]] 
	return dct

def getbreakfastItems():
   
    breakfastItems = foodmenuAPIRequest()
    breakfastItems = breakfastItems[dayofweek][0]['breakfast']

    return breakfastItems

def getlunchItems():
   
    lunchItems = foodmenuAPIRequest()
    lunchItems = lunchItems[dayofweek][2]['lunch']

    return lunchItems

# def getsnacksItems():
   
#     snacksItems = foodmenuAPIRequest()
#     snacksItems = snacksItems[dayofweek][3]['snacks']

#     return snacksItems

def getdinnerItems():
   
    dinnerItems = foodmenuAPIRequest()
    dinnerItems = dinnerItems[dayofweek][1]['dinner']

    return dinnerItems


def postrating(request):
    if request.method == "POST" and request.is_ajax():
        response = json.loads(request.body.decode('utf-8'))
        response = {str(key):str(value) for key, value in response.items()}
        rating = response.get('rating')
        item_name = response.get('item')

        idtoken = request.session['uid']

        # to get account info
        a = authorisation.get_account_info(idtoken)
        a = a["users"][0]['localId']

        ratingID = get_random_string(8).lower()
        
        data = {        
            "date_submitted": currentDate,
            "item_name": item_name,
            "rating": rating
                   }
        # print(data)
        db.child('ratings').child(a).child(ratingID).set(data)
        return JsonResponse({"success": 1}, status = 200)
    return JsonResponse({"success": 0}, status = 400)

def signin(request):
    """ takes in email and password by the user"""
    return render(request, 'signin.html')

def index(request):

    breakfastItems = getbreakfastItems()
    lunchItems = getlunchItems()
    # snacksItems = getsnacksItems()
    dinnerItems = getdinnerItems()
    
    return render(request, 'index.html', {'breakfastItems':breakfastItems, 'lunchItems':lunchItems, 'dinnerItems':dinnerItems})


def postsign(request):
    """stores user email and password. redirects if it matches with entries in firebase, o/w error"""
    email = request.POST.get('email')
    passw = request.POST.get('pass')
    try:
        # user variable used for lo gin with email and pwd check teminal for user id/token
        # utilises authorisation variable
        user = authorisation.sign_in_with_email_and_password(email,passw)
    except:
        return render(request, "signin.html", {'msg':"Invalid credentials"})
        # sign in allowed only for users authenticated in firebase
    print(user) #prints everything, for specifics use user('attribute')
    # add user session
    session_id = user['idToken']
    request.session['uid'] = str(session_id) #str representation imp

    breakfastItems = getbreakfastItems()
    lunchItems = getlunchItems()
    # snacksItems = getsnacksItems()
    dinnerItems = getdinnerItems()
    breakfastItems = [slugify(item) for item in breakfastItems]
    lunchItems = [slugify(item) for item in lunchItems]
    # snacksItems = [slugify(item) for item in snacksItems]
    dinnerItems = [slugify(item) for item in dinnerItems]

    return render(request,"welcome.html", {"e":email, 'breakfastItems':breakfastItems, 'lunchItems':lunchItems, 'dinnerItems':dinnerItems})

def logout(request):
    """logout from current user session, utilises auth from django.contrib [ensure db rules]"""
    auth.logout(request)
    return render(request, "signin.html")

def signup(request):
    """ redirects to signup page"""
    return render(request, "signup.html")

def postsignup(request):
    """ create account, fetches unique userid, gets userdata, constructs database"""
    name = request.POST.get('name')
    email = request.POST.get('email')
    passw = request.POST.get('pass')
    # creates useraccount
    try:
        user = authorisation.create_user_with_email_and_password(email, passw)
        # grabs userdata
        uid = user['localId']
        data ={'name': name, 'status': '1'} # 1 means disabled, handled by the admin
        # database constructor(pushes data), make sure database rules are laid
        db.child("users").child(uid).child("details").set(data)

    except:
        return render(request, "signup.html",{"msg": "Unable to create account, please try again!"})

    return render(request, "signin.html")
# NOTE: This function will return EMAIL_EXIST error in case a username is already taken.

def create(request):
    """redirects to create.html, creates a new report"""
    return render(request, "create.html")

# Pushes user data into firebase

def check(request):
    """ Grabs data from firebase using ID and grabs user data"""
    

    idtoken = request.session['uid']

    # to get account info
    a = authorisation.get_account_info(idtoken)
    a = a["users"] # grabs user key form dict
    a = a[0] # grabs 1st list entry
    a = a['localId'] # grabs value from key stored inside 1st list entry stored inside user key
    # again we get a = localID of user

    # to retrieve time stamps we use shallow function (see docs)
    timestamps = db.child('users').child(a).child('reports').shallow().get().val()
    ## print(timestamps) # prints a dict, to get list we need to convert
    print("timestamps dict: " + str(timestamps)) # check

    # appends timestamps to the list
    timelist= []
    for i in timestamps:
        timelist.append(i)
    timelist.sort(reverse=True) # sorts in reverse order

    print("timestamps list: " + str(timelist)) # check

    # retrieves child data from list entries (work/progess)
    work = []
    for i in timelist:
        """ does not employ shallow as we don't want keys"""
        wor = db.child('users').child(a).child('reports').child(i).child('work').get().val()
        work.append(wor)

    print("work: " + str(work)) # check

    # timestamps conversion into date format and appending dates to a list
    date=[]
    for i in timelist:
        i = float(i) # need to convert it into flow before passing
        dat = datetime.datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%Y')
        date.append(dat)

    print("date: " + str(date)) # check

    # combine 3 lists via zip Function
    comb_list = zip(timelist, date, work)
    print("Combine List: "+ str(comb_list)) # check new list

    name = db.child('users').child(a).child('details').child('name').get().val()
    print(name)
    return render(request, "check.html", {'comb_list':comb_list, 'e': name})
    #

def postcheck(request):
    
    # fetches z from check (see url)
    time = request.GET.get('z')
    idtoken = request.session['uid']
    # to get account info
    a = authorisation.get_account_info(idtoken)
    a = a["users"] # grabs user key form dict
    a = a[0] # grabs 1st list entry
    a = a['localId'] # grabs value from key stored inside 1st list entry stored inside user key
    # again we get a = localID of user


    work = db.child("users").child(a).child('reports').child(time).child('work').get().val()
    progress = db.child("users").child(a).child('reports').child(time).child('progress').get().val()
    i = float(time)
    date = datetime.datetime.fromtimestamp(i).strftime("%H:%M %d-%m-%Y")
    name = db.child('users').child(a).child('details').child('name').get().val()

    return render(request, "postcheck.html", {'w':work, 'p':progress, 'd':date, 'e':name})
