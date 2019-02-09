from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


# session.delete()
# row = session.query(Restaurant).first()
# newRestaurant = session.query(Restaurant).filter_by(name="new restaurant").one()
# session.delete(newRestaurant)

db = 'sqlite:///restaurantmenu.db'
engine = create_engine(db)
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				# session = db_setup(db)

				output = ""
				output += "<html><body>"
				output += "<h1><a href='/restaurants/new'>Make New Restaurant</a></h1>"
				output += "<h1>Restaurants<h1>"
				
				restaurants = session.query(Restaurant).all()
				for restaurant in restaurants:
					output += "<p><h2>%s</h2>" % str(restaurant.name)
					output += "<a href='/restaurants/%s/edit'>Edit</a></br>" % restaurant.id
					output += "<a href='/restaurants/%s/delete'>Delete</a></br></p>" % restaurant.id

				output += "</body></html>"
				self.wfile.write(output)
				return

			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()

				# create form
				output = ""
				output += "<html><body>"
				output += "<h1>New Restaurant</h1>"
				output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Enter Restaurant Name?</h2><input name="new_restaurant" type="text" ><input type="submit" value="Create"> </form>'''
				output += "<a href='/restaurants'>Back to restaurant list</a>"
				output += "</body></html>"
				self.wfile.write(output)
				return

			if self.path.endswith("/edit"):   # how to recognize the right item?
				id_to_update = self.path.split('/')[2]
				rest_object = session.query(Restaurant).filter_by(id = id_to_update).one()
				if rest_object != []:
					self.send_response(200)
					self.send_header('Content-type','text/html')
					self.end_headers()

					# create form to collect new name
					output = ""
					output += "<html><body>"
					output += "<h1>Update Name</h1>"
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % id_to_update
					output += "<input name='updated_name' placeholder='%s' type='text' ><input type='submit' value='Rename'> </form>" % rest_object.name
					output += "<a href='/restaurants'>Back to restaurant list</a>"
					output += "</body></html>"
					self.wfile.write(output)
				
				else: 
					output = ""
					output += "<html><body>"
					output += "<p>Restaurant Not Found</h1>"
					output += "<a href='/restaurants'>Back to restaurant list</a>"
					output += "</body></html>"
					self.wfile.write(output)
				return

			if self.path.endswith("/delete"):   # how to recognize the right item?
				id_to_delete = self.path.split('/')[2]
				rest_object = session.query(Restaurant).filter_by(id = id_to_delete).one()
				if rest_object != []:
					self.send_response(200)
					self.send_header('Content-type','text/html')
					self.end_headers()

					# create confirmation page
					output = ""
					output += "<html><body>"
					output += "<p>Really Delete %s ?!</p>" % rest_object.name
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % id_to_delete
					output += "<input type='submit' value='Delete'> </form>"
					output += "<a href='/restaurants'>Back to restaurant list</a>"
					output += "</body></html>"
					self.wfile.write(output)
				
				else: 
					output = ""
					output += "<html><body>"
					output += "<p>Restaurant Not Found</h1>"
					output += "<a href='/restaurants'>Back to restaurant list</a>"
					output += "</body></html>"
					self.wfile.write(output)
				return

		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('new_restaurant')
				
				# add to database
				newRestaurant = Restaurant(name = messagecontent[0])
				session.add(newRestaurant)
				session.commit()

				# check your work
				# check = session.query(Restaurant).filter_by(name = newRestaurant.name).one()

				# confirm for user
				# output = ""
				# output += "<html><body>"
				# output += "Restaurant %s created" % check.name
				# output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Enter Restaurant Name?</h2><input name="new_restaurant" type="text" ><input type="submit" value="Create"> </form>'''
				# output += "<a href='/restaurants'>Back to restaurant list</a>"
				# output += "</body></html>"
				# self.wfile.write(output)
				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()
				return

			if self.path.endswith("/edit"):
				id_to_update = self.path.split('/')[2]
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('updated_name')
				
				# update database
				restaurant_to_update = session.query(Restaurant).filter_by(id = id_to_update).one()
				restaurant_to_update.name = messagecontent[0]
				session.add(restaurant_to_update)
				session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()
				return
				
			if self.path.endswith("/delete"):
				id_to_delete = self.path.split('/')[2]
				
				# update database
				restaurant_to_delete = session.query(Restaurant).filter_by(id = id_to_delete).one()
				session.delete(restaurant_to_delete)
				session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()
				return

		except:
			pass

def db_setup(db):
	engine = create_engine(db)
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	return session

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
		main()

