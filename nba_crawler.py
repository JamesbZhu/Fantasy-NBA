from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import sqlite3
import numpy as np

conn = sqlite3.connect('/Users/jameszhu/desktop/DFS/nba_database.db')
c = conn.cursor()

def getPlayers(link):
	req = requests.get(link)
	soup = BeautifulSoup(req.content, "lxml")
	players = []
	for a in soup.findAll('th'):
		if len(a.get_text()) > 5:
			players.append(a.get_text())
	players = players[2::]
	return players 

def getHeaders(link): 
	
	req = requests.get(link)
	soup = BeautifulSoup(req.content, "lxml")
	header = [th.getText() for th in soup.findAll('tr', limit=2)[1].findAll('th')]
	header = header[1::]
	return header

def getBoxScore(link):
	req = requests.get(link)
	soup = BeautifulSoup(req.content, "lxml")
	data_rows = soup.findAll('tr')[2:]
	player_data = [[td.getText() for td in data_rows[i].findAll('td')] for i in range(len(data_rows))]
	return player_data

r = requests.get("http://www.basketball-reference.com/boxscores/")
soup = BeautifulSoup(r.content, "lxml")

games = [] 
links = []

for a in soup.findAll('a', href=re.compile('/boxscores/2.*\.html')):
	games.append(a['href'])

link = list(set(games))

for i in link:
	links.append("http://www.basketball-reference.com{}".format(i))

for i in links:
	player_data = getBoxScore(i)
	header = getHeaders(i)
	players = getPlayers(i)
	df = pd.DataFrame(player_data, columns = header, index = players)
	StdBoxScore = pd.DataFrame()
	#AdvBoxScore = pd.DataFrame()
	advanced = np.where(df.index.values == "Advanced Box Score Stats")[0]
	basic = np.where(df.index.values == "Basic Box Score Stats")[0]
	stdBoxScore = pd.concat([df[0:advanced[0]],df[basic[0]:advanced[1]]])
	#advBoxScore = pd.concat([df[advanced[0]:basic[0]],df[advanced[1]:len(df)]])
	stdBoxScore.to_sql('nba_data', conn, if_exists='append')
'''
c.execute(
CREATE TABLE "nba_data" (
"index" TEXT,
  "MP" TEXT,
  "FG" TEXT,
  "FGA" TEXT,
  "FG%" TEXT,
  "3P" TEXT,
  "3PA" TEXT,
  "3P%" TEXT,
  "FT" TEXT,
  "FTA" TEXT,
  "FT%" TEXT,
  "ORB" TEXT,
  "DRB" TEXT,
  "TRB" TEXT,
  "AST" TEXT,
  "STL" TEXT,
  "BLK" TEXT,
  "TOV" TEXT,
  "PF" TEXT,
  "PTS" TEXT
);
)
'''
conn.commit()
conn.close




