# Written by mcady#1738
import requests
import json
import time
import pandas
import numpy
import math

def calc_score(avg, std, title, score):
  score = score * 10
  z = (score - avg)/std
  return z


def create_dicts(avg, std, lists, scoreModifier, restrictions):
  uScoreDict = {}
  wScoreDict = {}
  ideeDict = {}
  for li in lists:
    for entry in li['entries']:
      title = entry['media']['title']['romaji']
      status = entry['status']
      airing = entry['media']['status']
      idee = entry['media']['id']
      score = float(entry['score']) * scoreModifier
      if score != 0 and (status not in restrictions):
        if score > 11:
            return create_dicts(avg, std, lists, 0.1, restrictions)
        uScoreDict[title] = score    
        wScoreDict[title] = calc_score(avg, std, title, score)
        ideeDict[title] = idee
  return (uScoreDict, wScoreDict, ideeDict)


def get_list_data(username, runAvg, runStd, restrictions):
  url='https://graphql.anilist.co'
  q = '''query ($name: String) {
    User(name: $name ) {
    
      statistics {
        anime {
          meanScore
          standardDeviation
        }
      }
    }
    MediaListCollection(userName: $name type: ANIME) {
      lists {
        entries {
          media {
            id
            status
            title {
              romaji
            }
          }
          status
          score
        }
      }
    }
  }'''

  v = { 'name': username}
  resp = requests.post(url, json={'query' : q, 'variables': v})
  jason = resp.json()
  try:
    avg = jason['data']['User']['statistics']['anime']['meanScore']
    print(avg)
    std = jason['data']['User']['statistics']['anime']['standardDeviation']
    print(std)
  except:
    print(username + ' fucked up')
    return
  if avg == 0:
    avg = float(input("enter average"))
    std = float(input("enter std"))
  lists = jason['data']['MediaListCollection']['lists']
  runAvg.append(avg)
  runStd.append(std)
  return create_dicts(avg, std, lists, 1, restrictions)


def compile_scores(username, restrictions, ideeDict, countDict, uScoreDict, wScoreDict, uDeviationDict, wDeviationDict, runAvg, runStd):
  ind_uScoreDict, ind_wScoreDict, ind_ideeDict = get_list_data(username, runAvg, runStd, restrictions)
  if ind_uScoreDict is not None:
    for showName in ind_uScoreDict:
      if showName in uScoreDict:
        ind_uScore, ind_wScore, run_uScore, run_wScore, run_uDeviation, run_wDeviation, = ind_uScoreDict[showName],ind_wScoreDict[showName], uScoreDict[showName], wScoreDict[showName], uDeviationDict[showName], wDeviationDict[showName]
        countDict[showName] += 1
        new_uScore = run_uScore + (ind_uScore - run_uScore) / countDict[showName]
        new_wScore = run_wScore + (ind_wScore - run_wScore) / countDict[showName]
        uDeviationDict[showName] = (run_uDeviation + (ind_uScore - run_uScore) * (ind_uScore - new_uScore))
        wDeviationDict[showName] = (run_wDeviation + (ind_wScore - run_wScore) * (ind_wScore - new_wScore))
        uScoreDict[showName] = new_uScore
        wScoreDict[showName] = new_wScore
      else:
        uScoreDict[showName] = ind_uScoreDict[showName]
        wScoreDict[showName] = ind_wScoreDict[showName]
        countDict[showName] = 1
        ideeDict[showName] = ind_ideeDict[showName]
        uDeviationDict[showName] = 0
        wDeviationDict[showName] = 0
    print('added ' + username)


def weight_scores(wScoreDict, countDict, uDeviationDict, wDeviationDict, groupSize):
  groupAvg = (sum(runAvg)/len(runAvg))/10
  groupStd = (sum(runStd)/len(runStd))/10
  for key in wScoreDict.keys():
    wScore = wScoreDict[key]
    count = countDict[key]
    uDeviation = uDeviationDict[key]
    wDeviation = wDeviationDict[key]
    countMult = 1
    if count <= math.floor(groupSize * .5):
      countMult = countMult * (.99)**(math.ceil(groupSize * .5) - count) # countMult = countMult * (.99)**(math.ceil(groupSize * .5) - count)
    if count <= math.floor(groupSize * .3):
      countMult = countMult * (.9)**(math.ceil(groupSize * .6) - count) # countMult = countMult * (.9)**(math.ceil(groupSize * .2) - count)
    if count <= math.floor(groupSize * .2):
      countMult = countMult * (.99)**(math.ceil(groupSize * .7) - count) # countMult = countMult * (.85)**(math.ceil(groupSize * .1) - count)
    uDeviationDict[key] = uDeviation / (count - 1) if count != 1 else 0
    wDeviationDict[key] = wDeviation / (count - 1) if count != 1 else 0
    wScoreDict[key] = (countMult * wScore * groupStd) + groupAvg


def make_list(ideeDict, uScoreDict, wScoreDict, countDict, uDeviationDict, wDeviationDict, minUsers):
  bigd = {ideeDict[key]: (key, uScoreDict[key], wScoreDict[key], countDict[key], uDeviationDict[key], wDeviationDict[key]) for key in ideeDict.keys() if countDict[key] >= minUsers}
  df = pandas.DataFrame(bigd).T
  df.columns = ['anime', 'unweighted avg', 'weighted avg', 'users seen', 'unweighted dev', 'weighted dev']
  df.to_excel(r'./anilist.xlsx')

names = [] #put anilist usernames here
groupSize = len(names)
minUsers = 2 #if you want a minimum amount of people to have seen as show put it here
restrictions = ["PLANNING", "NOT_YET_RELEASED"] #for if you wanted to include drops you can add that here

uScoreDict = {}
wScoreDict = {}
countDict = {}
ideeDict = {}
uDeviationDict = {}
wDeviationDict = {}
runAvg = []
runStd = []

for name in names:
  compile_scores(name, restrictions, ideeDict, countDict, uScoreDict, wScoreDict, uDeviationDict, wDeviationDict, runAvg, runStd)
  time.sleep(1)
while True:
  name = input("enter username")
  if name == 'done':
    break
  compile_scores(name, restrictions, ideeDict, countDict, uScoreDict, wScoreDict, uDeviationDict, wDeviationDict, runAvg, runStd)
  time.sleep(1)
weight_scores(wScoreDict, countDict, uDeviationDict, wDeviationDict, groupSize)
make_list(ideeDict, uScoreDict, wScoreDict, countDict, uDeviationDict, wDeviationDict, minUsers)
