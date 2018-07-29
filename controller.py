import os
import tornado.ioloop
import tornado.web
import tornado.log
import time
from datetime import datetime, date, timedelta
import requests
# import queries
import json

from jinja2 import \
    Environment, PackageLoader, select_autoescape

ENV = Environment(
    loader=PackageLoader('monitor', 'templates'),
    autoescape=select_autoescape(['html', 'xml']))

# since the sensors were removed, the database is unavailable now.
# have to use data imported from json file in stead
datafile = []
with open('./monitor/static/json/api_data_final.json', 'r') as f:
    datafile = json.load(f)
    
class TemplateHandler(tornado.web.RequestHandler):
    def render_template(self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))
        
    def get(self):
        self.set_header('Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
      
    # def initialize(self):
    #     self.session = queries.Session(os.environ.get('DATABASE_URL'))
    # def initialize(self):
    #     self.session = queries.Session('postgresql://postgres@localhost:5432/home_mon')
        
class MainHandler(TemplateHandler):
    def get(self):
        super().get()
# the api fetching sensor data is unavailable now, thus this handler will use data from json file directly in stead of 
    # api request setup
        # url = "https://api.thingspeak.com/channels/484266/feeds/last.json"
        # api_key = os.environ.get('ThingSpeak_API_KEY')
        # timezone = "America/Chicago"
        # payload = {'api_key': api_key, 'timezone': timezone}
        # r = requests.get(url, params=payload)
        appid = os.environ.get('OpenWeather_APPID')
        weather_url = 'http://api.openweathermap.org/data/2.5/weather'
        weather_payload = {'q': 'Houston', 'appid': appid, 'units': 'imperial'}
        r_weather = requests.get(weather_url, params=weather_payload)       
        local_weather = r_weather.json()['main']['temp']
        latestData = [data for data in datafile if data['created'].split("T")[0] == "2018-05-05"][-1]
        self.render_template("main.html", {'response': latestData, 'local_weather': local_weather, 'current_date': '2018-05-05'})

# after searching online, I've found dynamic SQL query is risky and a bad practice, so not use here
class DetailHandler(TemplateHandler):
    def get(self, slug, date):
        super().get()
        fieldTemp = "{}_temp".format(slug)
        fieldHumi = "{}_humidity".format(slug)
        fmt = '%Y-%m-%d'       
        ts = time.strptime(date, fmt)
        dt = datetime.fromtimestamp(time.mktime(ts))
        yesterday = (dt - timedelta(1)).strftime(fmt)
        tomorrow = (dt + timedelta(1)).strftime(fmt)
        temps = [data[fieldTemp] for data in datafile if data['created'].split("T")[0] == date]
        humis = [data[fieldHumi] for data in datafile if data['created'].split("T")[0] == date]
            # details = self.session.query('''SELECT created::time, bedroom_temp, bedroom_humidity FROM home_mon WHERE created::date = %(date)s ORDER BY created ASC ''', {'date': date})
        # elif slug == 'livingroom':
            # details = self.session.query('''SELECT created::time, livingroom_temp, livingroom_humidity FROM home_mon WHERE created::date = %(date)s ORDER BY created ASC ''', {'date': date})
        # elif slug == 'office':
            # details = self.session.query('''SELECT created::time, office_temp, office_humidity FROM home_mon WHERE created::date = %(date)s ORDER BY created ASC ''', {'date': date})
        # elif slug == 'kitchen':
            # details = self.session.query('''SELECT created::time, kitchen_temp, kitchen_humidity FROM home_mon WHERE created::date = %(date)s ORDER BY created ASC ''', {'date': date})
        # details.free()
        # temps = []
        # humis = []
        # for detail in details:
        #     temps.append(float(detail[fieldTemp]))
        #     humis.append(float(detail[fieldHumi]))
        self.render_template("detail_template.html", {'slug': slug, 'temps': temps, 'humis': humis, 'date': date, 'yesterday': yesterday, 'tomorrow': tomorrow, 'current_date': date})
    

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/detail/(.*?)/(.*)", DetailHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
        {'path': 'monitor/static'})
        ],
        autoreload=True)

if __name__ == "__main__":
    tornado.log.enable_pretty_logging()
    app = make_app()
    PORT = int(os.environ.get('PORT', '2000'))
    app.listen(PORT)
    print('starting... at PORT {}'.format(PORT))
    tornado.ioloop.IOLoop.current().start()
