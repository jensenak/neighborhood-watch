import mechanicalsoup
import psycopg2
import psycopg2.extras
import json
from time import sleep, time
from bottle import route, post, delete, run, request

conn = psycopg2.connect("dbname='hood' user='neighbor' host='localhost' password='french fries'")

#===============================================================================
# ROUTING SECTION
#===============================================================================
@route('/houses')
def list_houses():
    return getHouses()

@route('/house/<house>')
def get_house(house):
    return getHouse(house)

@post('/house/new')
def new_house():
    return addHouse(request.json['address'])

@delete('/house/<house>')
def del_house(house):
    removeHouse(house)

#===============================================================================
# DATABASE FUNCTIONS
#===============================================================================
def getHouses():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""SELECT DISTINCT ON (houses.id) *
                     FROM houses INNER JOIN history
                     ON history.house = houses.id
                     ORDER BY houses.id, history.timestamp DESC""")
    resp = cur.fetchall()
    result = []
    for r in resp:
        result.append(dict(r))

    return {"houses":result}

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
                   VALUES (%s, %s) RETURNING id""", (addr, photo))
    conn.commit()
    return {"house":cur.fetchone()[0]}

def addHistory(house, result, price):
    now = int(time())
    cur = conn.cursor()
    cur.execute("""INSERT INTO history (result, price, house, "timestamp")
                     VALUES (%s, %s, %s, %s)""", (result, price, house, now))
    conn.commit()

def removeHouse(house):
    cur = conn.cursor()
    cur.execute("""DELETE FROM history WHERE house = %s""", (house,))
    conn.commit()
    cur.execute("""DELETE FROM houses WHERE id = %s RETURNING photo""", (house,))
    ph = cur.fetchone()[0]
    conn.commit()
    if ph != 1:
        cur.execute("""DELETE FROM photos WHERE id = %s""", (ph,))
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
    for house, addr in getAddrs():
        sleep(5)
        status, price = pollZillow(addr)
        addHistory(house, status, price)

@route('/run/<house>')
def updateOne(house):
    addr = getHouse(house)['house'][1]
    status, price = pollZillow(addr)
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

run(host='localhost', port=8585)
