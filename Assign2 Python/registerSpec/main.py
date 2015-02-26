
#   10% of final grade.
#   Due Wed. 4th March 2015 - end of the day.
#   All code in Python, GAE, and webapp2.
#   Deploy on GAE.


import os
import cgi
import webapp2
import jinja2
import random
from google.appengine.api import mail
from google.appengine.api import users
from webapp2_extras import sessions
from google.appengine.ext import ndb
from gaesessions import get_current_session


class UserDetail(ndb.Model):
    userid = ndb.StringProperty()
    email = ndb.StringProperty()
    passwd = ndb.StringProperty() 
    passwd2 = ndb.StringProperty()


class confirmedAccounts(ndb.Model):
    userid = ndb.StringProperty()
    email = ndb.StringProperty()
    passwd = ndb.StringProperty() 
    #passwd2 = ndb.StringProperty()
    changeNumber = ndb.StringProperty()


JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)

class ResetHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA.get_template('reset.html')
        self.response.write(template.render({ 'the_title': 'Reset Your Password'}) )


    def post(self):
        user_address = cgi.escape(self.request.get('email'))
        user_id = cgi.escape(self.request.get('userid'))
        number= random.randrange(1,10000000)
        
        stringNum = str(number)



        print "the user name is ",user_id
        print "the email address ", user_address

        sender_address = "Example.com Support <support@example.com>"
        subject = "Password reset"
        body = """                To reset your password, click the link below, \n
                Enter the following number when prompted """+stringNum+"""

                http://localhost:8080/changepassword?type="""+user_id

        query=ndb.gql("SELECT * FROM confirmedAccounts where userid = :1 ",user_id)
        row=query.get()
        row.changeNumber=stringNum
        row.put()


        mail.send_mail(sender_address, user_address, subject, body)
        emailSentPage = JINJA.get_template('resetEmail.html')
        self.response.write(emailSentPage.render({ 'the_email': user_address }) )

class ChangePassHandler(webapp2.RequestHandler):
    def get(self):
         
        print "get in ChangePassHandler"
        userid =self.request.get('type')
        print userid

        template = JINJA.get_template('changePass.html')
        self.response.write(template.render({ 'the_title': 'Change Your Password'}) )
        
        

       

    def post(self):
        print "POST in ChangePassHandler"
        
        newpasswsd = self.request.get('newpasswd')
        num = self.request.get('number')
        userid = self.request.get('userid')
        
       

       
        query=ndb.gql("SELECT * FROM confirmedAccounts where userid=:1 AND changeNumber=:2 ",userid, num)
        row=query.fetch()

        for i in row:
            print "this" ,i.passwd
            i.passwd= newpasswsd
            i.changeNumber = ""
            i.put()
            template = JINJA.get_template('changeSuccess.html')
            self.response.write(template.render({ 'the_title': 'Password Successfully changed'}) )


        
        

        



class LoginHandler(webapp2.RequestHandler):
    def get(self):
        
        template = JINJA.get_template('login.html')
        self.response.write(template.render({ 'the_title': 'Login page'}) )
        print "made it to log in get"
    def post(self):
        
        userid = self.request.get('userid')
        passwd = self.request.get('passwd')

        session = get_current_session()
        session['userid'] = userid

        queryCnames = ndb.gql("SELECT * FROM confirmedAccounts  WHERE userid = :1",  userid  )
        cNames = queryCnames.fetch()

        if cNames ==[]:
            template = JINJA.get_template('login.html')
            self.response.write(template.render({ 'the_title': 'Please Login','UserNameError': 'Please enter a valid username' }) )

        else:
            for i in cNames:
               
                if userid == i.userid and passwd == i.passwd :

                    session = get_current_session()
                    session['userid'] = self.request.get('userid')
                    self.redirect('/page1')

                elif passwd != i.passwd:
                    template = JINJA.get_template('login.html')
                    self.response.write(template.render({ 'the_title': 'Please Login','wrongPassword': 'Your password was incorrect' }) )




                    
        # Check that a login and password arrived from the FORM.
        # Lookup login ID in "confirmed" datastore.
        # Check for password match.
        # Set the user as logged in and let them have access to /page1, /page2, and /page3.  SESSIONs.
        # What if the user has forgotten their password?  Provide a password-reset facility/form.
       

# We need to provide for LOGOUT.

class Page1Handler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        #session.clear()

        if session.get('userid') == None:
            template = JINJA.get_template('login.html')
            self.response.write(template.render({ 'the_title': 'Login page'}) )
        else:
            template = JINJA.get_template('page1.html')
            self.response.write(template.render({ 'the_title': ' Page 1'}) )

    
class Page2Handler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.get('userid') == None:
            

            template = JINJA.get_template('login.html')
            self.response.write(template.render({ 'the_title': 'Login page'}) )
        else:
            template = JINJA.get_template('page2.html')
            self.response.write(template.render({ 'the_title': ' Page 2'}) )


class Page3Handler(webapp2.RequestHandler):
    def get(self):

        session = get_current_session()
        
        if session.get('userid') == None:
            template = JINJA.get_template('login.html')
            self.response.write(template.render({ 'the_title': 'Login page'}) )
        else:
            template = JINJA.get_template('page3.html')
            self.response.write(template.render({ 'the_title': ' Page 3'}) )

class LogoutHandler(webapp2.RequestHandler):

    def post(self):
        session = get_current_session()
        session.terminate()
        template = JINJA.get_template('login.html')
        self.response.write(template.render({ 'the_title': 'Login page'}) )
        print "Logged out"




class confirmHandler(webapp2.RequestHandler):
    def get(self):
        userid = self.request.get('type')
        
        print('confirm handler')
        
        print("ID from email ",userid)

        query = ndb.gql("SELECT * FROM UserDetail  WHERE userid = :1",  userid )
        ret = query.fetch()

        queryCnames = ndb.gql("SELECT * FROM confirmedAccounts  WHERE userid = :1",  userid )
        cNames = queryCnames.fetch()
        if cNames == []:
            for i in ret:
                person = confirmedAccounts()
                person.userid = userid
                person.email  = i.email
                person.passwd =i.passwd
                person.changeNumber =""
                person.put()
        self.redirect('/login')
       
class RegisterHandler(webapp2.RequestHandler):
    def get(self):
       
        template = JINJA.get_template('reg.html')
        self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page' }) )
       

    def post(self):
        
        userid = cgi.escape(self.request.get('userid'))
        email = cgi.escape(self.request.get('email') )
        passwd = cgi.escape(self.request.get('passwd'))
        passwd2 = cgi.escape(self.request.get('passwd2'))
        user_address = cgi.escape(self.request.get('email'))

        query = ndb.gql("SELECT * FROM UserDetail  WHERE userid = :1",  userid )
        ret = query.fetch()
        
        

        if userid =="":
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','UserNameError': 'Invalid User name' }) )

        elif passwd =="":
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','emptyPassword': 'Please Enter a password' }) )

        elif passwd2 =="":
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','emptyPassword2': 'Please enter your password a second time' }) )


        elif passwd != passwd2:
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','passwordMismatch': 'The passwords do not match' }) )

        elif email=="":
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','invalidEmail': 'Please enter an email address' }) )

        elif len(ret) > 0:
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','userNameUsed': 'The username name is unavailable' }) )


        else:

            #self.redirect('/processreg')
            user_address = cgi.escape(self.request.get('email'))

            sender_address = "Example.com Support <support@example.com>"
            subject = "Confirm your registration"
            body = """Thank you for creating an account! Please confirm your email address by \n clicking on the link below and logging into your account:
                      http://localhost:8080/confirm?type="""+userid 

            mail.send_mail(sender_address, user_address, subject, body)

            print("Commit to Database")
            person = UserDetail()

            person.userid = cgi.escape(self.request.get('userid'))
            person.email = cgi.escape(self.request.get('email') )
            person.passwd = cgi.escape(self.request.get('passwd'))
            person.passwd2 = cgi.escape(self.request.get('passwd2'))
            person.put()


            emailSentPage = JINJA.get_template('emailSent.html')
            self.response.write(emailSentPage.render({ 'the_email': email }) )

        # Check if the data items from the POST are empty.
        # Check if passwd == passwd2.
        # Does the userid already exist in the "confirmed" datastore or in "pending"?
        # Is the password too simple?
        
        # Add registration details to "pending" datastore.
        # Send confirmation email.

        # Can GAE send email?
        # Can my GAE app receive email?

        # This code needs to move to the email confirmation handler.
       



        

app = webapp2.WSGIApplication([
    ('/register', RegisterHandler),
    ('/processreg', RegisterHandler),
    ('/confirm',confirmHandler),
    ('/', LoginHandler),
    ('/login', LoginHandler),
    ('/processlogin', LoginHandler),
    
    # Next three URLs are only available to logged-in users.
    ('/page1', Page1Handler),
    ('/page2', Page2Handler),
    ('/page3', Page3Handler),
    ('/logout',LogoutHandler),
    ('/resetpassword',ResetHandler),
    ('/changepassword',ChangePassHandler),

], debug=True)
