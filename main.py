import mechanicalsoup
import psycopg2
from time import sleep
from datetime import datetime, timedelta
from bottle import route, post, run, template, request

conn = psycopg2.connect("dbname='hood' user='neighbor' host='localhost' password='french fries'")

#===============================================================================
# ROUTING SECTION
#===============================================================================
@route('/houses')
def list_houses():
    getHouses()

@route('/house/<house>')
def get_house(house):
    getHouse(house)

@post('/house/new')
def new_house():
    return addHouse(request.json['address'])

#===============================================================================
# DATABASE FUNCTIONS
#===============================================================================
def getHouses():
    cur = conn.cursor()
    cur.execute("""SELECT DISTINCT ON (houses.id) *
                     FROM houses INNER JOIN history
                     ON history.house = houses.id
                     ORDER BY houses.id, history.last DESC""")
    return cur.fetchall()

def getAddrs():
    cur = conn.cursor()
    cur.execute("SELECT id, addr FROM houses")
    return cur.fetchall()

def getHouse(house):
    cur = conn.cursor()
    h = {}
    cur.execute("SELECT * FROM houses WHERE id = %s", (house,))
    h['house'] = cur.fetchone()
    cur.execute("SELECT * FROM photos WHERE id = %s", (h['house'][2],))
    h['photo'] = cur.fetchone()
    cur.execute("SELECT * FROM history WHERE house = %s", (house, ))
    h['history'] = cur.fetchall()
    return h

def addHouse(addr, photo=1):
    cur = conn.cursor()
    cur.execute("""INSERT INTO houses (addr, photo)
                   VALUES (%s, %s)""", (addr, photo))

def addHistory(house, result, price):
    now = datetime.utcnow()
    cur = conn.cursor()
    cur.execute("""INSERT INTO history (last, result, price, house)
                     VALUES (%s, %s, %s, %s)""", (now, result, price, house))
    conn.commit()

#===============================================================================
# NOTIFY FUNCTIONS
#===============================================================================
def notify():
    pass

#===============================================================================
# MECHANICAL FUNCTIONS
#===============================================================================
@route('/run')
def runUpdates():
    print("Initializing...")
    for house, addr in getAddrs():
        sleep(5)
        print("House {}".format(house))
        status, price = pollZillow(addr)
        print("--> {} {}".format(status, price))
        addHistory(house, status, price)

def pollZillow(address):
    browser = mechanicalsoup.Browser()

    home = browser.get("http://zillow.com/homes")

    search = home.soup.select(".zsg-searchbox")[0]
    search.select("#citystatezip")[0]['value'] = address
    result = browser.submit(search, home.url)
    status = result.soup.select("#listing-icon")[0]['class'][1]
    price = result.soup.select(".main-row > span")[0].string
    return (status, price)

run(host='localhost', port=8080)
