from django.conf.urls import url
from . import views

urlpatterns = [url(r'^signIn$', views.signIn, name='signIn'),
               url(r'^signUp$', views.signUp, name='signUp'),
               url(r'^submitSignUp$', views.submitSignUp, name='submitSignUp'),
               url(r'^signUpSuccess$', views.signUpSuccess, name='signUpSuccess'),
               url(r'^validate$', views.validatePasswd, name='validatePasswd'),
               url(r'^profile$', views.profile, name='profile'),
               url(r'^signOut$', views.signOut, name='signOut'),
               url(r'^displayShippingAddress$', views.displayAddress, name='displayShippiningAddress'),
               url(r'^displayBillingAddress$', views.displayBillingAddress, name='displayBillingAddress'),
               url(r'^displayCards', views.diplaycards, name='displayCards'),
               url(r'^addLivingAddress$', views.addLivingAddress, name='addLivingAddress'),
               url(r'^addBillingAddress$', views.addBillingAddress, name='addBillingAddress'),
               url(r'^setDefaultBilling$', views.setDefaultBilling, name = 'setDefaultBilling'),
               url(r'^setDefaultLiving$', views.setDefaultLiving, name='setDefaultLiving'),
               url(r'^deleteLivingAddress$', views.deleteLivingAddress, name = 'deleteLivingAddress'),
               url(r'^deleteBillingAddress$', views.deleteBillingAddress, name='deleteBillingAddress'),
               url(r'^updateLivingAddress$', views.updateLivingAddress, name = 'updateLivingAddress'),
               url(r'^updateBillingAddress$', views.updateBillingAddress, name = 'updateBillingAddress'),
               url(r'^logIn$', views.logIn, name='logIn'),
               url(r'^$', views.index, name='index'),
               ]