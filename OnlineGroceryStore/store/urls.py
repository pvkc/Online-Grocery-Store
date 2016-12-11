from django.conf.urls import url
from . import views

urlpatterns = [url(r'^signIn$', views.signIn, name='signIn'),
               url(r'staffSignIn', views.staffSignIn, name='staffSignIn'),
               url(r'^signUp$', views.signUp, name='signUp'),
               url(r'^submitSignUp$', views.submitSignUp, name='submitSignUp'),
               url(r'^signUpSuccess$', views.signUpSuccess, name='signUpSuccess'),
               url(r'^validate$', views.validatePasswd, name='validatePasswd'),
               url(r'^validateStaff$', views.validateStaff, name='validateStaff'),
               url(r'validateEmail$', views.validateEmail, name = 'validateEmail'),
               url(r'^profile$', views.profile, name='profile'),
               url(r'^staffHome$', views.staffHome, name='staffHome'),
               url(r'^signOut$', views.signOut, name='signOut'),
               url(r'^displayShippingAddress$', views.displayAddress, name='displayShippiningAddress'),
               url(r'^displayBillingAddress$', views.displayBillingAddress, name='displayBillingAddress'),
               url(r'^displayCards', views.diplaycards, name='displayCards'),
               url(r'^displayShoppingCart$', views.displayShoppingCart, name='displayShoppingCart'),
               url(r'^addLivingAddress$', views.addLivingAddress, name='addLivingAddress'),
               url(r'^addBillingAddress$', views.addBillingAddress, name='addBillingAddress'),
               url(r'^addNewCard$', views.addNewCard, name="addNewCard"),
               url(r'^addProduct$', views.addProduct, name="addProduct"),
               url(r'^addStockWHouse$', views.addStock, name='addStock'),
               url(r'^addToCart$',views.addToCart, name='addToCart'),
               url(r'^setDefaultBilling$', views.setDefaultBilling, name = 'setDefaultBilling'),
               url(r'^setDefaultLiving$', views.setDefaultLiving, name='setDefaultLiving'),
               url(r'^deleteLivingAddress$', views.deleteLivingAddress, name = 'deleteLivingAddress'),
               url(r'^deleteBillingAddress$', views.deleteBillingAddress, name='deleteBillingAddress'),
               url(r'^deleteCard$',views.deleteCard, name = 'deleteCard'),
               url(r'^deleteProduct$', views.deleteProduct, name='delteProduct'),
               url(r'^deleteFromCart$', views.deleteFromCart, name='deleteFromCart'),
               url(r'^updateLivingAddress$', views.updateLivingAddress, name = 'updateLivingAddress'),
               url(r'^updateBillingAddress$', views.updateBillingAddress, name = 'updateBillingAddress'),
               url(r'^updateProduct$', views.updateProduct, name='updateProduct'),
               url(r'^updateCard$', views.updateCard, name = 'updateCard'),
               url(r'^updateCart$', views.updateCart, name='updateCart'),
               url(r'^logIn$', views.logIn, name='logIn'),
               url(r'staffLogin$', views.staffLogIn, name='staffLogIn'),
               url(r'searchProduct$', views.searchProduct, name='searchProduct'),
               url(r'^$', views.index, name='index'),
               ]
