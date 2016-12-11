from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
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
    SQLSelectCustAddress = '''SELECT ADDR_ID FROM CUSTOMER_LIVES WHERE CUSTOMER_ID=:1 AND IS_DEFAULT='Y' '''
    SQLSelectStateOfAddr = '''SELECT STATE_NAME FROM ADDRESS WHERE ADDR_ID=:1'''
    SQLSelectProductFromState = '''SELECT P.PRODUCT_ID, P.PRODUCT_NAME, P.PRODUCT_CATEGORY, P.PRODUCT_SIZE, P.ADDITIONAL_INFO, P.IMAGE_LOCATION, PP.STATE_NAME, PP.PRICE, PP.PRICE_UNIT
                              FROM PRODUCT P, PRODUCT_PRICE PP WHERE PP.PRODUCT_ID = P.PRODUCT_ID AND PP.STATE_NAME=:1 '''
    conn = openDbConnection()
    listProduct = []

    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    if 'name' in request.session:
        context['toLoad'] = 'store/base_after_login.html'
        context['name'] = request.session['name']

        try:
            curr = conn.cursor()
            curr.execute(SQLSelectCustAddress, (request.session['custId'],))
            addrId = curr.fetchall()[0][0]
            curr.execute(SQLSelectStateOfAddr, (addrId,))
            state = curr.fetchall()[0][0]
            curr.execute(SQLSelectProductFromState,(state,))
            for data in curr.fetchall():
                listProduct.append(data)


        except db.DatabaseError, exp:
            print exp
            conn.close()
            return HttpResponseNotFound('Execution failed, Try Later')

    else:
        context['toLoad'] = 'store/base_not_logged_in.html'
        context['name'] = ''
        state = 'IL'

        try:
            curr = conn.cursor()
            curr.execute(SQLSelectProductFromState, (state,))
            for data in curr.fetchall():
                listProduct.append(data)
        except db.DatabaseError, exp:
            print exp
            conn.close()
            return HttpResponseNotFound('Execution failed, Try Later')

    context['indexListProduct'] = listProduct
    context['title'] = 'US Grocery Store'
    context['state'] = state

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
        curr.execute(SQLSelectCustomer, (request.POST['email'].lower(),))
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
        return HttpResponse('No user found with credentials', status=422)

    storedPasswd = str(storedPasswd)
    print str(storedPasswd)
    conn.close()

    if bc.hashpw(request.POST['password'].encode('utf-8'), storedPasswd) == storedPasswd:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=422)


def logIn(request):
    response = validatePasswd(request)

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
                                SELECT :1,:2,:3 FROM DUAL'''  # WHERE NOT EXISTS (
    # SELECT 1 FROM CUSTOMER_LIVES WHERE :1=:1 AND CUSTOMER_ID = :2 AND ADDR_ID =:3
    # )'''

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
        # curr.execute(SQLInsertCustomerLives, ('Y', request.session['custId'], newAddrId[0][0]))

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
            return HttpResponse("Data Already Exists", status=422)

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
    return HttpResponse(status=200)


@csrf_exempt
def deleteLivingAddress(request):
    SQLDeleteCustomerLives = 'DELETE FROM CUSTOMER_LIVES WHERE CUSTOMER_ID=:1 AND ADDR_ID=:2'

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLDeleteCustomerLives,
                     (request.session['custId'], request.session['addrId'][request.POST['addrId']]))
    except Exception, exp:
        print exp
        conn.rollback()
        conn.close()
        return HttpResponseNotFound("Execution Failed, Try later")
    conn.commit()
    conn.close()
    return HttpResponse(status=200)


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
        # curr.execute(SQLInsertCustomerLives, (request.session['custId'], newAddrId, request.session['addrId'][request.POST['addrId']] ))
        # curr.execute(SQLDeleteCustomerLives, (request.session['custId'], request.session['addrId'][request.POST['addrId']]))
        curr.execute(SQLUpdateCustomerLives,
                     (newAddrId, request.session['custId'], request.session['addrId'][request.POST['addrId']]))
    except db.IntegrityError, e:
        if ("%s" % e.message).startswith('ORA-00001:'):
            conn.rollback()
            conn.close()
            return HttpResponse("Trying to update to existing address", status=422)
            # curr.execute(SQLUpdateCustomerLivesDef,
            #             (request.session['custId'], request.session['addrId'][request.POST['addrId']], newAddrId))
            # curr.execute(SQLDeleteCustomerLives,
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
                                    SELECT :1,:2,:3 FROM DUAL '''  # WHERE NOT EXISTS (
    #  SELECT 1 FROM CUSTOMER_BILLED_TO WHERE CUSTOMER_ID = :2 AND ADDR_ID =:3
    # )'''

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
        # curr.execute(SQLInsertCustomerBilledTo, ('N', request.session['custId'], newAddrId[0][0]))

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
            return HttpResponse("Adding an exisiting address not allowed", status=422)
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
        curr.execute(SQLUpdateCustomerBilledTo,
                     (newAddrId, request.session['custId'], request.session['billAddrId'][request.POST['addrId']]))
        # curr.execute(SQLInsertCustomerBilledTo, (request.session['custId'], newAddrId, request.session['billAddrId'][request.POST['addrId']]))

    except db.IntegrityError, e:
        if ("%s" % e.message).startswith('ORA-00001:'):
            conn.rollback()
            conn.close()
            return HttpResponse("Trying to update to existing address", status=422)
            # curr.execute(SQLUpdateCustomerBilledDef,
            #             (request.session['custId'], request.session['billAddrId'][request.POST['addrId']], newAddrId))
            # curr.execute(SQLDeleteCustomerBilledTo,
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
        curr.execute(SQLInsertCardDetails, (
        request.POST["cardNum"], request.POST["cardName"].upper(), request.POST["cardMonth"], request.POST["cardYear"],
        request.POST["cardCvv"]))
        curr.execute(SQLSelectCardDetails, (request.POST["cardNum"],))
        cardId = curr.fetchall()[0][0]
        curr.execute(SQLInsertCustomerCard, (request.session["custId"], cardId))

    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        if str(exp).startswith('ORA-00001:'):
            return HttpResponse("Data Already Exists", status=422)
        # raise
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
        curr.execute(SQLInsertCardDetails, (
        request.POST["cardNum"], request.POST["cardName"].upper(), request.POST["cardMonth"], request.POST["cardYear"],
        request.POST["cardCvv"]))
        curr.execute(SQLSelectCardDetails, (request.POST["cardNum"],))
        cardId = curr.fetchall()[0][0]
        curr.execute(SQLUpdateCustomerCard,
                     (cardId, request.session["custId"], request.session['cardId'][request.POST['cardId']]))

    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        if str(exp).startswith('ORA-00001:'):
            return HttpResponse("Data Already Exists", status=422)
        # raise
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


@csrf_exempt
def validateEmail(request):
    SQLSelectCustomer = 'SELECT 1 FROM CUSTOMER WHERE EMAIL=:1'
    conn = openDbConnection()
    # print request.POST
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectCustomer, (request.POST['email'].lower(),))
        data = curr.fetchall()
    except db.DatabaseError, exp:
        print exp
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    conn.close()

    if data:
        return HttpResponse('Email registered', status=422)
    else:
        return HttpResponse(status=200)


def staffSignIn(request):
    return render(request, 'store/staffSignIn.html', {'title': 'Staff Sign in'})


def staffLogIn(request):
    SQLSelectStaff = 'SELECT STAFF_ID,STAFF_NAME FROM STAFF WHERE STAFF_ID=:1'
    response = validateStaff(request)
    if response.status_code == 200:
        pass
    else:
        return HttpResponse(status=422)

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectStaff, (request.POST['staffId'],))
        staffId, staffName = curr.fetchall()[0]
    except db.DatabaseError, exp:
        print exp
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    request.session['name'] = staffName
    request.session['staffId'] = staffId
    conn.close()
    return redirect('/staffHome')


@csrf_exempt
def validateStaff(request):
    SQLSelectStaff = 'SELECT STAFF_ID, STAFF_PASSWORD FROM STAFF WHERE STAFF_ID =:1'

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    staffId, storedPasswd = '', ''
    try:
        curr = conn.cursor()
        curr.execute(SQLSelectStaff, (request.POST['staffId'],))
        data = curr.fetchall()
        if data:
            staffId, storedPasswd = data[0]
            storedPasswd = str(storedPasswd)

    except db.DatabaseError, exp:
        print exp
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    conn.close()
    if bc.hashpw(request.POST['password'].encode('utf-8'), storedPasswd) == storedPasswd:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=422)


def staffHome(request):
    SQLSelectProduct = '''SELECT P.PRODUCT_ID, P.PRODUCT_NAME, P.PRODUCT_CATEGORY, P.PRODUCT_SIZE, P.ADDITIONAL_INFO, P.IMAGE_LOCATION, PP.STATE_NAME, PP.PRICE, PP.PRICE_UNIT
                          FROM PRODUCT P, PRODUCT_PRICE PP WHERE PP.PRODUCT_ID = P.PRODUCT_ID '''

    # SQLSelectWareHouse = '''SELECT WH.WAREHOUSE_ID, SUM(SWH.NUMBER_OF_ITEMS*P.PRODUCT_SIZE)  --WH.STORAGE_CAPACITY, WH.ADDR_ID,
    #                        --SWH.PRODUCT_ID, SWH.NUMBER_OF_ITEMS,
    #                        --P.PRODUCT_NAME, P.PRODUCT_SIZE
    #                        FROM WAREHOUSE WH INNER JOIN STOCK_IN_WAREHOUSE SWH ON WH.WAREHOUSE_ID = SWH.WAREHOUSE_ID
    #                        INNER JOIN PRODUCT P ON SWH.PRODUCT_ID = P.PRODUCT_ID
    #                         GROUP BY WH.WAREHOUSE_ID'''

    SQLSelectWHouse = '''SELECT WH.WAREHOUSE_ID, (WH.STORAGE_CAPACITY - T1.USED) AS REM_CAPCITY, AD.STREET,
                         AD.STREET_NAME, AD.APT_NUM, AD.CITY,AD.STATE_NAME, AD.ZIPCODE
                          FROM WAREHOUSE WH,ADDRESS AD,
                          (
                            SELECT WH.WAREHOUSE_ID, SUM(SWH.NUMBER_OF_ITEMS*P.PRODUCT_SIZE) AS USED
                            FROM WAREHOUSE WH INNER JOIN STOCK_IN_WAREHOUSE SWH ON WH.WAREHOUSE_ID = SWH.WAREHOUSE_ID
                            INNER JOIN PRODUCT P ON SWH.PRODUCT_ID = P.PRODUCT_ID
                            GROUP BY WH.WAREHOUSE_ID
                          ) T1
                          WHERE WH.WAREHOUSE_ID = T1.WAREHOUSE_ID
                          AND WH.ADDR_ID = AD.ADDR_ID'''

    SQLSelectPName = 'SELECT PRODUCT_ID, PRODUCT_NAME FROM PRODUCT'

    listProduct = []
    listWareHouse = []
    listPName = []

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")
    try:
        curr = conn.cursor()
        curr.execute(SQLSelectProduct)
        for ix, data in enumerate(curr.fetchall()):
            listProduct.append([data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]])

        curr.execute(SQLSelectWHouse)
        for ix,data in enumerate(curr.fetchall()):
            listWareHouse.append(data)

        curr.execute(SQLSelectPName)
        for data in curr.fetchall():
            listPName.append(data)


    except db.DatabaseError, exp:
        print exp
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    context = {}
    context['title'] = 'Staff'
    context['name'] = request.session['name']
    context['product'] = listProduct
    context['listWareHouse'] = listWareHouse
    context['listPName'] = listPName
    #print context
    conn.close()
    return render(request, 'store/staffHomePage.html', context)


@csrf_exempt
def addProduct(request):
    SQLInsertProduct = '''INSERT INTO PRODUCT(PRODUCT_NAME,PRODUCT_CATEGORY,PRODUCT_SIZE,ADDITIONAL_INFO,IMAGE_LOCATION)
                          SELECT :1,:2,:3,:4,:5 FROM DUAL WHERE NOT EXISTS(SELECT 1 FROM PRODUCT WHERE PRODUCT_NAME=:1)'''
    SQLSelectProduct = 'SELECT PRODUCT_ID FROM PRODUCT WHERE PRODUCT_NAME=:1'
    SQLInsertProductPrice = '''INSERT INTO PRODUCT_PRICE(STATE_NAME, PRICE, PRICE_UNIT, PRODUCT_ID) VALUES(:1,:2,:3,:4)'''

    print request.POST

    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")
    try:
        curr = conn.cursor()

        curr.execute(SQLInsertProduct,
                     (request.POST['pname'].title(), request.POST['pcategory'].title(), request.POST['psize'],
                      request.POST['padditionalinfo'].title(), request.POST['pimagelocation']))

        curr.execute(SQLSelectProduct, (request.POST['pname'].title(),))
        productId = curr.fetchall()[0][0]

        curr.execute(SQLInsertProductPrice,
                     (request.POST['pstate'], request.POST['pprice'], request.POST['priceunit'], productId))
    except db.DatabaseError, exp:
        print exp
        if str(exp).startswith('ORA-00001:'):
            conn.close()
            return HttpResponse("Data Already Exists", status=422)

        return HttpResponseNotFound('Execution Failed, Try Later')

    conn.commit()
    conn.close()
    return HttpResponse(status=200)


@csrf_exempt
def updateProduct(request):
    SQLUpdateProduct = "UPDATE PRODUCT SET PRODUCT_NAME=:1, PRODUCT_CATEGORY=:2, PRODUCT_SIZE=:3, ADDITIONAL_INFO=:4, IMAGE_LOCATION=:5 WHERE PRODUCT_NAME=:1"
    SQLUpdateProductPrice = "UPDATE PRODUCT_PRICE SET PRICE=:1, PRICE_UNIT=:2, STATE_NAME=:3 WHERE STATE_NAME=:4 AND PRODUCT_ID=:5"

    print request.POST
    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")
    try:
        curr = conn.cursor()

        curr.execute(SQLUpdateProduct,
                     (request.POST['pname'].title(), request.POST['pcategory'].title(), request.POST['psize'],
                      request.POST['padditionalinfo'].title(), request.POST['pimagelocation']))

        curr.execute(SQLUpdateProductPrice,
                     (request.POST['pprice'], request.POST['priceunit'], request.POST['pstate'],
                      request.POST['oldPState'], request.POST['pId']))
    except db.DatabaseError, exp:
        print exp
        if str(exp).startswith('ORA-00001:'):
            return HttpResponse("Data Already Exists", status=422)
        conn.rollback()
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    conn.commit()
    conn.close()
    return HttpResponse(status=200)


@csrf_exempt
def deleteProduct(request):
    SQLDeleteProductPrice = 'DELETE FROM PRODUCT_PRICE WHERE STATE_NAME=:1 AND PRODUCT_ID=:2'
    SQLDeleteProduct = '''DELETE FROM PRODUCT P WHERE PRODUCT_ID=:1 AND
                          NOT EXISTS(SELECT 1 FROM PRODUCT_PRICE PP WHERE P.PRODUCT_ID = PP.PRODUCT_ID) AND
                          NOT EXISTS(SELECT 1 FROM STOCK_IN_WAREHOUSE SWH WHERE SWH.PRODUCT_ID = P.PRODUCT_ID) AND
                          NOT EXISTS(SELECT 1 FROM CART_CONTAINS CC WHERE CC.PRODUCT_ID = P.PRODUCT_ID) AND
                          NOT EXISTS(SELECT 1 FROM SUPPLIER_SELLS SS WHERE SS.PRODUCT_ID = P.PRODUCT_ID) AND
                          NOT EXISTS(SELECT 1 FROM ORDER_CONTAINS OC WHERE OC.PRODUCT_ID = P.PRODUCT_ID)'''

    print request.POST
    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")
    try:
        curr = conn.cursor()
        curr.execute(SQLDeleteProductPrice,
                     (request.POST['pstate'], request.POST['pId']))
        curr.execute(SQLDeleteProduct, (request.POST['pId'],))

    except db.DatabaseError, exp:
        print exp
        if str(exp).startswith('ORA-00001:'):
            return HttpResponse("Data Already Exists", status=422)
        conn.rollback()
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    conn.commit()
    conn.close()
    return HttpResponse(status=200)

@csrf_exempt
def addStock(request):
    SQLSelectWHouse = '''SELECT WH.WAREHOUSE_ID, (WH.STORAGE_CAPACITY - T1.USED) AS REM_CAPCITY
                          FROM WAREHOUSE WH,
                          (
                            SELECT WH.WAREHOUSE_ID, SUM(SWH.NUMBER_OF_ITEMS*P.PRODUCT_SIZE) AS USED
                            FROM WAREHOUSE WH INNER JOIN STOCK_IN_WAREHOUSE SWH ON WH.WAREHOUSE_ID = SWH.WAREHOUSE_ID
                            INNER JOIN PRODUCT P ON SWH.PRODUCT_ID = P.PRODUCT_ID
                            GROUP BY WH.WAREHOUSE_ID
                          ) T1
                          WHERE WH.WAREHOUSE_ID = T1.WAREHOUSE_ID
                          AND WH.WAREHOUSE_ID=:1'''

    SQLSelectProduct = '''SELECT PRODUCT_ID, PRODUCT_SIZE*:1 FROM PRODUCT WHERE PRODUCT_ID=:2'''

    SQLInsertStockWHouse = '''INSERT INTO STOCK_IN_WAREHOUSE(NUMBER_OF_ITEMS, WAREHOUSE_ID, PRODUCT_ID)
                           SELECT :1,:2,:3 FROM DUAL'''
    SQLUpdateStockWHouse = '''UPDATE STOCK_IN_WAREHOUSE SET NUMBER_OF_ITEMS= NUMBER_OF_ITEMS +:1 WHERE PRODUCT_ID=:2 AND WAREHOUSE_ID=:3'''
    print request.POST
    conn = openDbConnection()
    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    try:
        curr = conn.cursor()

        curr.execute(SQLSelectProduct, (request.POST['quantity'], request.POST['pId']))
        for data in curr.fetchall():
            reqCapacity = data[1]

        curr.execute(SQLSelectWHouse, (request.POST['wId'],))
        for data in curr.fetchall():
            remainingCap = data[1]

        if reqCapacity > remainingCap:
            conn.close()
            return HttpResponse(status=422)

        curr.execute(SQLUpdateStockWHouse,
                     (request.POST['quantity'], request.POST['pId'], request.POST['wId']))
    except db.DatabaseError, exp:
        print exp
        conn.rollback()
        conn.close()
        return HttpResponseNotFound('Execution Failed, Try Later')

    try:
        curr.execute(SQLInsertStockWHouse, (request.POST['quantity'],request.POST['wId'],request.POST['pId']))

    except db.DatabaseError, exp:
        print exp
        if str(exp).startswith('ORA-00001:'):
            pass
        else:
            conn.rollback()
            conn.close()
            return HttpResponseNotFound('Execution Failed, Try Later')

    conn.commit()
    conn.close()
    return HttpResponse(status=200)

@csrf_exempt
def searchProduct(request):
    SQLSelectProductFromState = '''SELECT P.PRODUCT_ID, P.PRODUCT_NAME, P.PRODUCT_CATEGORY, P.PRODUCT_SIZE, P.ADDITIONAL_INFO, P.IMAGE_LOCATION, PP.STATE_NAME, PP.PRICE, PP.PRICE_UNIT
                                 FROM PRODUCT P, PRODUCT_PRICE PP WHERE PP.PRODUCT_ID = P.PRODUCT_ID AND PP.STATE_NAME=:1 AND LOWER(P.PRODUCT_NAME) LIKE :2'''
    conn = openDbConnection()
    listProduct = []

    if conn == ERROR:
        return HttpResponseNotFound("DB down, Try Later")

    context = {}
    #context['toLoad'] = 'store/base_after_login.html'
    if request.session.get('name',[]):
        context['name'] = request.session['name']
    else:
        context['name'] = ''

    try:
        curr = conn.cursor()
        curr.execute(SQLSelectProductFromState,(request.POST['state'], '%'+request.POST['searchText'].lower()+'%'))
        for data in curr.fetchall():
            listProduct.append(data)


    except db.DatabaseError, exp:
        print exp
        conn.close()
        return HttpResponseNotFound('Execution failed, Try Later')


    context['indexListProduct'] = listProduct
    context['state'] = request.POST['state']

    return HttpResponse(render_to_string ('store/searchResults.html', context))