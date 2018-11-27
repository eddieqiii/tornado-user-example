import exceptions
import bcrypt
import sqlite3

# please do not attempt sql injection on this
# or i will call the police
db = sqlite3.connect("data/users.sqlite")
cursor = db.cursor()

async def authenticate(details):
	# details is a dict with fields username, password
	cursor.execute("SELECT password FROM users WHERE username = ?", [details["username"]])
	hashed = cursor.fetchone()
	if hashed == None:
		raise exceptions.UserNonexistantException()

	# Check password
	encpw = details["password"].encode("utf-8")
	result = bcrypt.checkpw(encpw, hashed[0])
	return result

async def register(details):
	# Check if user exists
	cursor.execute("SELECT username FROM users WHERE username = ?", [details["username"]])
	results = cursor.fetchall()
	if results != []:
		raise exceptions.UserExistsException

	# Hash password
	oldPw = details["password"].encode("utf-8")
	details["password"] = bcrypt.hashpw(oldPw, bcrypt.gensalt())

	# Insert into database
	cursor.execute("INSERT INTO users VALUES (?, ?, ?)", [
		details["username"],
		details["password"],
		details["age"]
	])

	# Commit changes
	db.commit()

	return

async def details(user):
	#return {"username": "Big Man", "password": "bigboy47", "age": 47}
	# Get user details
	cursor.execute("SELECT * FROM users WHERE username = ?", [user])
	details = cursor.fetchone()
	if details == None:
		raise exceptions.UserNonexistantException()

	return details
