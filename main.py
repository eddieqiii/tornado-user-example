import auth
import exceptions
import tornado.ioloop
import tornado.web
import tornado.escape

# Create the IOLoop
currentLoop = tornado.ioloop.IOLoop()
currentLoop.make_current()

# Handle root requests
class RootHandler(tornado.web.RequestHandler):
	async def get(self):
		self.redirect("/auth")

# Handle authentication
class AuthenticationHandler(tornado.web.RequestHandler):
	async def get(self):
		# Check if user is already authenticated
		authed = self.get_cookie("authenticated")
		if authed == "true":
			self.redirect("/profile")
			return

		self.render("login.html")

	async def post(self):
		async def login_error(errormsg):
			# we await reqhandler.render so tornado does not complain
			# about calling things after .finish()
			await self.render("loginerror.html", message=errormsg)
			return

		loginDetails = { "username": None, "password": None }

		# Check username
		try:
			loginDetails["username"] = self.get_argument("username")
			if loginDetails["username"] == "":
				raise exceptions.MissingFieldException()
		except:
			await login_error("No u sername was provided")
			return

		# Check/get password
		try:
			loginDetails["password"] = self.get_argument("password")
			if loginDetails["password"] == "":
				raise exceptions.MissingFieldException()
		except:
			await login_error("No password was provided")
			return

		# Authenticate user
		try:
			result = await auth.authenticate(loginDetails)
		except exceptions.UserNonexistantException:
			await login_error("Incorrect details")
			return

		# Set cookies
		# very secure, please do not hack thank you
		self.set_cookie("authenticated", "true")
		unameCookie = tornado.escape.url_escape(loginDetails["username"])
		self.set_cookie("username", unameCookie)
		self.redirect("/profile")
		return

# Handle profile page
class ProfileHandler(tornado.web.RequestHandler):
	async def get(self):
		# Check if user is authenticated
		authed = self.get_cookie("authenticated")
		if authed != "true":
			self.redirect("/")
			return

		# Retrieve user details
		try:
			user = self.get_cookie("username")
			if user == None:
				raise exceptions.UserNonexistantException()

			user = tornado.escape.url_unescape(user)
			userDetails = await auth.details(user)

			self.render("profile.html",
				username=userDetails[0],
				password=userDetails[1],
				age=str(userDetails[2])
			)
			return
		except exceptions.UserNonexistantException:
			# If user does not exist, log out
			self.redirect("/logout")
			return

# Handle registration
class RegistrationHandler(tornado.web.RequestHandler):
	async def get(self):
		self.render("register.html")
	async def post(self):
		async def reg_error(msg):
			await self.render("registermsg.html", message=msg)
			return

		regDetails = { "username": None, "password": None }

		# Check username
		try:
			regDetails["username"] = self.get_argument("username")
			if regDetails["username"] == "":
				raise exceptions.MissingFieldException()
		except:
			await reg_error("No u sername was provided")
			return

		# Check/get password
		try:
			regDetails["password"] = self.get_argument("password")
			if regDetails["password"] == "":
				raise exceptions.MissingFieldException()
		except:
			await reg_error("No password was provided")
			return

		# Check/get age
		try:
			regDetails["age"] = self.get_argument("age")
			if regDetails["age"] == "":
				raise exceptions.MissingFieldException()
			else:
				regDetails["age"] = int(regDetails["age"])
		except:
			await reg_error("No age was provided")
			return

		# Register user
		try:
			await auth.register(regDetails)

			await reg_error("Successful registration")
			return
		except exceptions.UserExistsException:
			await reg_error("User already exists")
			return

# Handle logout
class LogoutHandler(tornado.web.RequestHandler):
	async def get(self):
		self.clear_cookie("username")
		self.clear_cookie("authenticated")
		self.redirect("/")

# Create application
app = tornado.web.Application([
	(r"/", RootHandler),
	(r"/auth", AuthenticationHandler),
	(r"/profile", ProfileHandler),
	(r"/logout", LogoutHandler),
	(r"/register", RegistrationHandler)
], static_path="./static", template_path="./views")
app.listen(8080)
print("Listening on port 8080")

# Start the IOLoop
currentLoop.start()
