from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
import cx_Oracle as db
import bcrypt as bc
from hashlib import sha1

# from .forms import SignInForm
# Create your views here.
ERROR = -1

PreventNull = lambda (check): '--' if check == '' else check
SQLSelectAddress = '''SELECT ADDR_ID 
						  FROM ADDRESS
						   WHERE STREET=:1 
						   AND STREET_NAME=:2
						   AND APT_NUM=:3
						   AND CITY=:4
						   AND STATE_NAME=:5
						   AND ZIPCODE=:6'''
SQLInsertAddress = '''INSERT INTO ADDRESS(STREET,STREET_NAME,APT_NUM,CITY,STATE_NAME,ZIPCODE) 
							SELECT :1,:2,:3,:4,:5,:6 FROM DUAL WHERE NOT EXISTS 
								(SELECT 1 FROM ADDRESS
						   		 WHERE STREET=:1 
	 						     AND STREET_NAME=:2
						   		 AND APT_NUM=:3
						   		 AND CITY=:4
						   		 AND STATE_NAME=:5
						   		 AND ZIPCODE=:6) '''
SQLInsertCustomerLives = '''INSERT INTO CUSTOMER_LIVES(IS_DEFAULT,CUSTOMER_ID,ADDR_ID) VALUES(:1,:2,:3) '''


def openDbConnection():
    try:
        conn = db.connect('vpolavarapu1/CS425IIT9@fourier.cs.iit.edu:1521/orcl.cs.iit.edu')
    except db.DatabaseError, exp:
        print exp
        return ERROR
    return conn


def index(request):
    context = {}
    if 'name' in request.session:
        context['toLoad'] = 'store/base_after_login.html'
        context['name'] = request.session['name']
    else:
        context['toLoad'] = 'store/base_not_logged_in.html'
        context['name'] = ''

    context['title'] = 'US Grocery Store'

    return render(request, 'store/index.html', context)


def signIn(request):
    return render(request, 'store/signIn.html', {'title': 'Store Sign in'})


def signUp(request):
    return render(request, 'store/signUp.html', {'title': 'Store Sign up'})


def signUpSuccess(request):
    return render(request, 'store/signUpSuccess.html', {'title': 'Success'})


def submitSignUp(request):
    SQLInsertLogIn = '''INSERT INTO LOG_IN_DETAILS(EMAIL,LOG_IN_PASSWORD) VALUES(:1,:2)'''
    SQLInsertCustomer = 'INSERT INTO CUSTOMER(CUSTOMER_NAME,BALANCE,EMAIL) VALUES (:1,:2,:3)'
    SQLSelectCustomer = 'SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL =:1'
    print request.POST['email']
    print request.POST['password']
    hashed = bc.hashpw(request.POST['password'].encode('utf-8'), bc.gensalt())

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLInsertLogIn, (request.POST['email'].lower(), hashed))
        curr.execute(SQLInsertCustomer, (request.POST['name'], 0, request.POST['email'].lower()))
        curr.execute(SQLInsertAddress, (
        PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
        request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
        request.POST['zipCode']))
        curr.execute(SQLSelectAddress, (
        PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
        request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
        request.POST['zipCode']))
        addrId = curr.fetchall()
        curr.execute(SQLSelectCustomer, (request.POST['email'],))
        custId = curr.fetchall()
        print custId, addrId
        curr.execute(SQLInsertCustomerLives, ('Y', custId[0][0], addrId[0][0]))
    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    conn.commit()
    conn.close()
    return redirect('/signUpSuccess')


@csrf_exempt
def validatePasswd(request):
    SQLSelectLogIn = 'SELECT LOG_IN_PASSWORD FROM LOG_IN_DETAILS WHERE EMAIL = :1'

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectLogIn, (request.POST['email'].lower(),))
        storedPasswd = curr.fetchall()
    except db.DatabaseError, exp:
        print exp
        conn.close()
        return HttpResponseNotFound('Execution failed, Try Later')

    if storedPasswd:
        storedPasswd = storedPasswd[0][0]
    else:
        return HttpResponse('No user found with credentials',status=422)

    storedPasswd = str(storedPasswd)
    print str(storedPasswd)
    conn.close()

    if bc.hashpw(request.POST['password'].encode('utf-8'), storedPasswd) == storedPasswd:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)



def logIn(request):
    response = validatePasswd(request);

    if response.status_code == 200:
        pass
    else:
        return response

    SQLSelectAllCustomer = 'SELECT CUSTOMER_ID, CUSTOMER_NAME, BALANCE, EMAIL FROM CUSTOMER WHERE EMAIL=:1'

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")


    try:
        curr = conn.cursor()
        curr.execute(SQLSelectAllCustomer, (request.POST['email'].lower(),))
        custId, custName, custBalance, custEmail = curr.fetchall()[0]
    except db.DatabaseError, exp:
        print exp
        conn.close()
        return HttpResponseNotFound('Execution failed, Try Later')

    request.session['name'] = custName
    request.session['email'] = custEmail
    request.session['custId'] = custId

    conn.close()
    return redirect('/')


def signOut(request):
    request.session.flush()
    return redirect('/')


def profile(request):
    context = {}

    SQLSelectCustomerLives = 'SELECT ADDR_ID FROM CUSTOMER_LIVES WHERE IS_DEFAULT = \'Y\' AND  CUSTOMER_ID = :1'
    SQLSelectCustomerBilled = 'SELECT ADDR_ID FROM CUSTOMER_BILLED_TO WHERE IS_DEFAULT = \'Y\' AND CUSTOMER_ID = :1'
    SQLSelectCustomerCard = 'SELECT CARD_ID FROM CUSTOMER_HAS_CARD WHERE CUSTOMER_ID = :1'
    SQLSelectCreditCard = 'SELECT CARD_NUM, EXP_MONTH, EXP_YEAR FROM CREDIT_CARD WHERE CARD_ID = :1'
    SQLSelectAddress = 'SELECT STREET, STREET_NAME, APT_NUM, CITY, STATE_NAME, ZIPCODE FROM ADDRESS WHERE ADDR_ID = :1'

    conn = openDbConnection()
    livesAtAddrId = ''
    billAtAddrId = ''

    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectCustomerLives, (request.session['custId'],))
        for data in curr.fetchall():
            livesAtAddrId = data[0]
            context['livesAtAddrId'] = data[0]

        curr.execute(SQLSelectCustomerBilled, (request.session['custId'],))
        for data in curr.fetchall():
            billAtAddrId = data[0]
            context['billAtAddrId'] = data[0]

        curr.execute(SQLSelectCustomerCard, (request.session['custId'],))
        for data in curr.fetchall():
            curr.execute(SQLSelectCreditCard, data)
            details = curr.fetchall()
            context['cardNum'], context['expMonth'], context['expYear'] = details[0]

        if livesAtAddrId:
            curr.execute(SQLSelectAddress, (livesAtAddrId,))
            for data in curr.fetchall():
                print data
                context['livesAtStreet'] = data[0]
                context['livesAtStreetName'] = data[1]
                context['livesAtAptNum'] = data[2]
                context['livesAtCity'] = data[3]
                context['livesAtState'] = data[4]
                context['livesAtZip'] = data[5]

        if billAtAddrId:
            curr.execute(SQLSelectAddress, (billAtAddrId,))
            for data in curr.fetchall():
                context['billAtStreet'] = data[0]
                context['billAtStreetName'] = data[1]
                context['billAtAptNum'] = data[2]
                context['billAtCity'] = data[3]
                context['billAtState'] = data[4]
                context['billAtZip'] = data[5]
    except db.DatabaseError, exp:
        print exp
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    context['name'] = request.session['name']
    context['title'] = 'Profile'

    conn.close()
    return render(request, 'store/profile.html', context)


def displayAddress(request):
    SQLSelectCustomerLives = 'SELECT ADDR_ID, IS_DEFAULT FROM CUSTOMER_LIVES WHERE CUSTOMER_ID = :1'
    SQLSelectAddress = 'SELECT STREET, STREET_NAME, APT_NUM, CITY, STATE_NAME, ZIPCODE FROM ADDRESS WHERE ADDR_ID = :1'

    listAddress = []
    context = {}
    request.session['addrId'] = {}

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectCustomerLives, (request.session['custId'],))
        for ix, data in enumerate(curr.fetchall()):
            livesAtAddrId, isDefaultAddr = data

            hashedAddrId = sha1(str(livesAtAddrId)).hexdigest()
            request.session['addrId'][hashedAddrId] = livesAtAddrId

            listAddress.append([hashedAddrId, isDefaultAddr])
            curr.execute(SQLSelectAddress, (livesAtAddrId,))
            data = curr.fetchall()[0]
            listAddress[ix].extend([data[0], data[1], data[2], data[3], data[4], data[5]])

        print listAddress

    except db.DatabaseError, exp:
        print exp
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    request.session.modified = True
    context['listAddress'] = listAddress
    context['title'] = 'View/Edit Address'
    context['name'] = request.session['name']
    conn.close()
    return render(request, 'store/shippingAddress.html', context)


@csrf_exempt
def addLivingAddress(request):
    SQLInsertCustomerLives = '''INSERT INTO CUSTOMER_LIVES(IS_DEFAULT,CUSTOMER_ID,ADDR_ID)
                                SELECT :1,:2,:3 FROM DUAL'''#WHERE NOT EXISTS (
                                  #SELECT 1 FROM CUSTOMER_LIVES WHERE :1=:1 AND CUSTOMER_ID = :2 AND ADDR_ID =:3
                                #)'''

    SQLSelectCustomerLives = 'SELECT ADDR_ID FROM CUSTOMER_LIVES WHERE IS_DEFAULT = \'Y\' AND  CUSTOMER_ID = :1'
    SQLUpdateCustomerLives = 'UPDATE CUSTOMER_LIVES SET IS_DEFAULT =:1 WHERE CUSTOMER_ID = :2 AND ADDR_ID = :3'
    print request.POST
    conn = openDbConnection()

    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLInsertAddress, (
        PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
        request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
        request.POST['zipCode']))
        curr.execute(SQLSelectAddress, (
        PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
        request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
        request.POST['zipCode']))
        newAddrId = curr.fetchall()
        #curr.execute(SQLInsertCustomerLives, ('Y', request.session['custId'], newAddrId[0][0]))

        if request.POST['setDefault'] == 'N':
            curr.execute(SQLInsertCustomerLives, ('N', request.session['custId'], newAddrId[0][0]))
        else:
            curr.execute(SQLSelectCustomerLives, (request.session['custId'],))
            oldAdrrdId = curr.fetchall()[0][0]
            curr.execute(SQLUpdateCustomerLives, ('N', request.session['custId'], oldAdrrdId))
            curr.execute(SQLInsertCustomerLives, ('Y', request.session['custId'], newAddrId[0][0]))

    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        if str(exp).startswith('ORA-00001:'):
            return HttpResponse("Data Already Exists",status=422)

        return HttpResponseNotFound("Execution Failed, Try later")

    conn.commit()
    conn.close()
    return HttpResponse(status=200)

@csrf_exempt
def setDefaultLiving(request):
    SQLSelectCustomerLives = 'SELECT ADDR_ID FROM CUSTOMER_LIVES WHERE IS_DEFAULT = \'Y\' AND  CUSTOMER_ID = :1'
    SQLUpdateCustomerLives = 'UPDATE CUSTOMER_LIVES SET IS_DEFAULT =:1 WHERE ADDR_ID = :2'

    conn = openDbConnection()

    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectCustomerLives, (request.session["custId"],))
        oldAddrId = curr.fetchall()[0][0]

        curr.execute(SQLUpdateCustomerLives, ('N', oldAddrId))
        curr.execute(SQLUpdateCustomerLives, ('Y', request.session['addrId'][request.POST['addrId']]))

    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        return HttpResponseNotFound("Execution Failed, Try later")

    conn.commit()
    conn.close()
    return  HttpResponse(status=200)

@csrf_exempt
def deleteLivingAddress(request):
    SQLDeleteCustomerLives = 'DELETE FROM CUSTOMER_LIVES WHERE CUSTOMER_ID=:1 AND ADDR_ID=:2'

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLDeleteCustomerLives,(request.session['custId'],request.session['addrId'][request.POST['addrId']]))
    except Exception, exp:
        print exp
        conn.rollback()
        conn.close()
        return HttpResponseNotFound("Execution Failed, Try later")
    conn.commit()
    conn.close()
    return  HttpResponse(status=200)

@csrf_exempt
def updateLivingAddress(request):
    SQLInsertCustomerLives = '''INSERT INTO CUSTOMER_LIVES(IS_DEFAULT, CUSTOMER_ID, ADDR_ID)
                                SELECT IS_DEFAULT,:1,:2 FROM CUSTOMER_LIVES WHERE ADDR_ID = :3 AND CUSTOMER_ID = :1'''
    SQLDeleteCustomerLives = 'DELETE FROM CUSTOMER_LIVES WHERE CUSTOMER_ID=:1 AND ADDR_ID=:2'
    SQLUpdateCustomerLives = 'UPDATE CUSTOMER_LIVES SET ADDR_ID=:1 WHERE CUSTOMER_ID=:2 AND ADDR_ID=:3'
    SQLUpdateCustomerLivesDef = '''UPDATE CUSTOMER_LIVES SET IS_DEFAULT= (SELECT IS_DEFAULT FROM CUSTOMER_BILLED_TO WHERE CUSTOMER_ID=:1 AND ADDR_ID=:2)
                                        WHERE ADDR_ID=:3 AND CUSTOMER_ID=:1 AND IS_DEFAULT<>\'Y\''''

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr=conn.cursor()
        curr.execute(SQLInsertAddress, (
            PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
            request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
            request.POST['zipCode']))
        curr.execute(SQLSelectAddress, (
            PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
            request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
            request.POST['zipCode']))
        newAddrId = curr.fetchall()[0][0]
        #curr.execute(SQLInsertCustomerLives, (request.session['custId'], newAddrId, request.session['addrId'][request.POST['addrId']] ))
        #curr.execute(SQLDeleteCustomerLives, (request.session['custId'], request.session['addrId'][request.POST['addrId']]))
        curr.execute(SQLUpdateCustomerLives,
                     (newAddrId, request.session['custId'], request.session['addrId'][request.POST['addrId']]))
    except db.IntegrityError, e:
        if ("%s" % e.message).startswith('ORA-00001:'):
            conn.rollback()
            conn.close()
            return HttpResponse("Trying to update to existing address", status=422)
            #curr.execute(SQLUpdateCustomerLivesDef,
            #             (request.session['custId'], request.session['addrId'][request.POST['addrId']], newAddrId))
            #curr.execute(SQLDeleteCustomerLives,
            #             (request.session['custId'], request.session['addrId'][request.POST['addrId']]))
        else:
            raise e
    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        return HttpResponseNotFound("Execution Failed, Try later")

    conn.commit()
    conn.close()
    return HttpResponse(status=200)


def displayBillingAddress(request):
    SQLSelectCustomerBillTo = 'SELECT ADDR_ID, IS_DEFAULT FROM CUSTOMER_BILLED_TO WHERE CUSTOMER_ID = :1'
    SQLSelectAddress = 'SELECT STREET, STREET_NAME, APT_NUM, CITY, STATE_NAME, ZIPCODE FROM ADDRESS WHERE ADDR_ID = :1'

    listAddress = []
    context = {}
    request.session['billAddrId'] = {}

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectCustomerBillTo, (request.session['custId'],))
        for ix, data in enumerate(curr.fetchall()):
            BillToAddrId, isDefaultAddr = data

            hashedAddrId = sha1(str(BillToAddrId)).hexdigest()
            request.session['billAddrId'][hashedAddrId] = BillToAddrId

            listAddress.append([hashedAddrId, isDefaultAddr])
            curr.execute(SQLSelectAddress, (BillToAddrId,))
            data = curr.fetchall()[0]
            listAddress[ix].extend([data[0], data[1], data[2], data[3], data[4], data[5]])

        print listAddress

    except db.DatabaseError, exp:
        print exp
        return HttpResponseNotFound('Execution Failed, Try Later')

    request.session.modified = True
    context['billAddress'] = listAddress
    context['title'] = 'View/Edit Address'
    context['name'] = request.session['name']
    return render(request, 'store/billingAddress.html', context)

@csrf_exempt
def addBillingAddress(request):
    SQLInsertCustomerBilledTo = '''INSERT INTO CUSTOMER_BILLED_TO(IS_DEFAULT,CUSTOMER_ID,ADDR_ID)
                                    SELECT :1,:2,:3 FROM DUAL ''' #WHERE NOT EXISTS (
                                    #  SELECT 1 FROM CUSTOMER_BILLED_TO WHERE CUSTOMER_ID = :2 AND ADDR_ID =:3
                                    #)'''

    SQLSelectCustomerBilledTo = 'SELECT ADDR_ID FROM CUSTOMER_BILLED_TO WHERE IS_DEFAULT = \'Y\' AND  CUSTOMER_ID = :1'
    SQLUpdateCustomerBilledTo = 'UPDATE CUSTOMER_BILLED_TO SET IS_DEFAULT =:1 WHERE CUSTOMER_ID = :2 AND ADDR_ID = :3'
    print request.POST
    conn = openDbConnection()

    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLInsertAddress, (
            PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
            request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
            request.POST['zipCode']))
        curr.execute(SQLSelectAddress, (
            PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
            request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
            request.POST['zipCode']))
        newAddrId = curr.fetchall()
        #curr.execute(SQLInsertCustomerBilledTo, ('N', request.session['custId'], newAddrId[0][0]))

        if request.POST['setDefault'] == 'N':
            curr.execute(SQLInsertCustomerBilledTo, ('N', request.session['custId'], newAddrId[0][0]))
        else:
            curr.execute(SQLSelectCustomerBilledTo, (request.session['custId'],))
            oldAdrrdId = curr.fetchall()
            if oldAdrrdId:
                curr.execute(SQLUpdateCustomerBilledTo, ('N', request.session['custId'], oldAdrrdId[0][0]))
            curr.execute(SQLInsertCustomerBilledTo, ('Y', request.session['custId'], newAddrId[0][0]))

    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        if str(exp).startswith('ORA-00001:'):
            return HttpResponse("Adding an exisiting address not allowed",status=422)
        return HttpResponseNotFound("Execution Failed, Try later")

    conn.commit()
    conn.close()
    return HttpResponse(status=200)

@csrf_exempt
def setDefaultBilling(request):
    SQLSelectCustomerBilledTo = 'SELECT ADDR_ID FROM CUSTOMER_BILLED_TO WHERE IS_DEFAULT = \'Y\' AND  CUSTOMER_ID = :1'
    SQLUpdateCustomerBilledTo = 'UPDATE CUSTOMER_BILLED_TO SET IS_DEFAULT =:1 WHERE ADDR_ID = :2'

    conn = openDbConnection()

    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectCustomerBilledTo, (request.session["custId"],))

        oldAddrId = curr.fetchall()
        if oldAddrId:
            curr.execute(SQLUpdateCustomerBilledTo, ('N', oldAddrId[0][0]))
        curr.execute(SQLUpdateCustomerBilledTo, ('Y', request.session['billAddrId'][request.POST['addrId']]))

    except Exception, exp:
        print exp
        conn.rollback()
        conn.close()
        return HttpResponseNotFound("Execution Failed, Try later")

    conn.commit()
    conn.close()
    return HttpResponse(status=200)

@csrf_exempt
def deleteBillingAddress(request):
    SQLDeleteCustomerBilledTo = 'DELETE FROM CUSTOMER_BILLED_TO WHERE CUSTOMER_ID=:1 AND ADDR_ID=:2'

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLDeleteCustomerBilledTo,
                     (request.session['custId'], request.session['billAddrId'][request.POST['addrId']]))
    except Exception, exp:
        print exp
        conn.rollback()
        conn.close()
        return HttpResponseNotFound("Execution Failed, Try later")
    conn.commit()
    conn.close()
    return HttpResponse(status=200)

@csrf_exempt
def updateBillingAddress(request):
    SQLInsertCustomerBilledTo = '''INSERT INTO CUSTOMER_BILLED_TO(IS_DEFAULT, CUSTOMER_ID, ADDR_ID)
                                    SELECT IS_DEFAULT,:1,:2 FROM CUSTOMER_BILLED_TO WHERE ADDR_ID = :3 AND CUSTOMER_ID = :1'''
    SQLDeleteCustomerBilledTo = 'DELETE FROM CUSTOMER_BILLED_TO WHERE CUSTOMER_ID=:1 AND ADDR_ID=:2'
    SQLUpdateCustomerBilledTo = 'UPDATE CUSTOMER_BILLED_TO SET ADDR_ID=:1 WHERE CUSTOMER_ID=:2 AND ADDR_ID=:3'
    SQLUpdateCustomerBilledDef = '''UPDATE CUSTOMER_BILLED_TO SET IS_DEFAULT= (SELECT IS_DEFAULT FROM CUSTOMER_BILLED_TO WHERE CUSTOMER_ID=:1 AND ADDR_ID=:2)
                                    WHERE ADDR_ID=:3 AND CUSTOMER_ID=:1 AND IS_DEFAULT <> \'Y\' '''
    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLInsertAddress, (
            PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
            request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
            request.POST['zipCode']))
        curr.execute(SQLSelectAddress, (
            PreventNull(request.POST.get('street').upper()), PreventNull(request.POST.get('streetName').upper()),
            request.POST['aptNo'].upper(), request.POST['city'].upper(), request.POST['state'].upper(),
            request.POST['zipCode']))
        newAddrId = curr.fetchall()[0][0]
        print request.POST
        curr.execute(SQLUpdateCustomerBilledTo,(newAddrId, request.session['custId'], request.session['billAddrId'][request.POST['addrId']] ))
        #curr.execute(SQLInsertCustomerBilledTo, (request.session['custId'], newAddrId, request.session['billAddrId'][request.POST['addrId']]))

    except db.IntegrityError, e:
        if ("%s" % e.message).startswith('ORA-00001:'):
            conn.rollback()
            conn.close()
            return HttpResponse("Trying to update to existing address", status=422)
            #curr.execute(SQLUpdateCustomerBilledDef,
            #             (request.session['custId'], request.session['billAddrId'][request.POST['addrId']], newAddrId))
            #curr.execute(SQLDeleteCustomerBilledTo,
            #             (request.session['custId'], request.session['billAddrId'][request.POST['addrId']]))
        else:
            raise e
    except Exception, exp:
        print exp
        conn.rollback()
        conn.close()
        return HttpResponseNotFound("Execution Failed, Try later")

    conn.commit()
    conn.close()
    return HttpResponse(status=200)


def diplaycards(request):
    SQLSelectCustomerCard = 'SELECT CUSTOMER_ID, CARD_ID FROM CUSTOMER_HAS_CARD WHERE CUSTOMER_ID = :1'
    SQLSelectCardDetails = 'SELECT CARD_NUM, EXP_MONTH, EXP_YEAR FROM CREDIT_CARD WHERE CARD_ID= :1'

    listCards = []
    context = {}
    request.session['cardId'] = {}

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectCustomerCard, (request.session['custId'],))
        for ix, data in enumerate(curr.fetchall()):
            custId, cardId = data

            hashedAddrId = sha1(str(cardId)).hexdigest()
            request.session['cardId'][hashedAddrId] = cardId

            listCards.append([hashedAddrId])
            curr.execute(SQLSelectCardDetails, (cardId,))
            data = curr.fetchall()[0]
            listCards[ix].extend([data[0], data[1], data[2]])

        print listCards

    except db.DatabaseError, exp:
        print exp
        return HttpResponseNotFound('Execution Failed, Try Later')

    request.session.modified = True
    context['cards'] = listCards
    context['title'] = 'View/Edit Cards'
    context['name'] = request.session['name']
    return render(request, 'store/userCards.html', context)

@csrf_exempt
def addNewCard(request):
    SQLInsertCardDetails = '''INSERT INTO CREDIT_CARD(CARD_NUM, OWNER_NAME, EXP_MONTH, EXP_YEAR, CVV)
                              SELECT :1,:2,:3,:4,:5 FROM DUAL WHERE NOT EXISTS
                              (SELECT 1 FROM CREDIT_CARD WHERE CARD_NUM=:1)'''
    SQLSelectCardDetails = "SELECT CARD_ID,CARD_NUM FROM CREDIT_CARD WHERE CARD_NUM=:1"
    SQLInsertCustomerCard = '''INSERT INTO CUSTOMER_HAS_CARD(CUSTOMER_ID, CARD_ID) VALUES (:1,:2)'''

    conn = openDbConnection()
    print request.POST
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLInsertCardDetails,(request.POST["cardNum"],request.POST["cardName"].upper(), request.POST["cardMonth"], request.POST["cardYear"], request.POST["cardCvv"]))
        curr.execute(SQLSelectCardDetails,(request.POST["cardNum"],))
        cardId = curr.fetchall()[0][0]
        curr.execute(SQLInsertCustomerCard,(request.session["custId"], cardId))

    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        if str(exp).startswith('ORA-00001:'):
            return HttpResponse("Data Already Exists", status=422)
        #raise
        return HttpResponseNotFound('Execution Failed, Try Later')

    conn.commit()
    conn.close()
    return HttpResponse(status=200)

@csrf_exempt
def updateCard(request):
    SQLInsertCardDetails = '''INSERT INTO CREDIT_CARD(CARD_NUM, OWNER_NAME, EXP_MONTH, EXP_YEAR, CVV)
                                  SELECT :1,:2,:3,:4,:5 FROM DUAL WHERE NOT EXISTS
                                  (SELECT 1 FROM CREDIT_CARD WHERE CARD_NUM=:1)'''
    SQLSelectCardDetails = "SELECT CARD_ID,CARD_NUM FROM CREDIT_CARD WHERE CARD_NUM=:1"
    SQLUpdateCustomerCard = '''UPDATE CUSTOMER_HAS_CARD SET CARD_ID = :1 WHERE CUSTOMER_ID =:2 AND CARD_ID = :3 '''

    conn = openDbConnection()
    print request.POST
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLInsertCardDetails,(request.POST["cardNum"],request.POST["cardName"].upper(), request.POST["cardMonth"], request.POST["cardYear"], request.POST["cardCvv"]))
        curr.execute(SQLSelectCardDetails,(request.POST["cardNum"],))
        cardId = curr.fetchall()[0][0]
        curr.execute(SQLUpdateCustomerCard,(cardId, request.session["custId"], request.session['cardId'][request.POST['cardId']]))

    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        if str(exp).startswith('ORA-00001:'):
            return HttpResponse("Data Already Exists", status=422)
        #raise
        return HttpResponseNotFound('Execution Failed, Try Later')

    conn.commit()
    conn.close()
    return HttpResponse(status=200)

@csrf_exempt
def deleteCard(request):
    SQLDeleteCustomerCard = 'DELETE FROM CUSTOMER_HAS_CARD WHERE CUSTOMER_ID =:1 AND CARD_ID =:2'
    conn = openDbConnection()
    print request.POST
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLDeleteCustomerCard,
                     (request.session["custId"], request.session['cardId'][request.POST['cardId']]))

    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        # raise
        return HttpResponseNotFound('Execution Failed, Try Later')

    conn.commit()
    conn.close()
    return HttpResponse(status=200)