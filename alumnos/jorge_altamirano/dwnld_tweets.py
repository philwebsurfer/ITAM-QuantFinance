#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2019 phil_websurfer
import sys, datetime, re, requests
import numpy as np
import bs4 
from bs4 import BeautifulSoup
from dateutil import parser #esta lib es más útil que la de Python para interpretar fechas parciales, como las de Twitter

def extract_tweets(soup, file, i, year, silent=False):
    tweets = soup.find_all("table", attrs={"class": "tweet"})
    # soup.find_all("div", attrs={"class": "tweet-text"})
    # tweet = tweets[0]
    for tweet in tweets:
        tweet_text = tweet.find_all('div', attrs={'class': 'tweet-text'})
        tweet_date = tweet.find_all("td", attrs={'class': 'timestamp'})
        for text in tweet_text:
            if type(text) == bs4.element.Tag:
                txt = re.sub("(eleconomista\.com\.mx|pic\.twitter\.com|bit\.ly|bitly\.com)/[^ ]*", " ", text.text).strip()
                txt = re.sub("(\||\n)", " ", txt)
                file.write(txt + "|")
        for date in tweet_date:
            if type(date) == bs4.element.Tag:
                date = date.text.strip()
                if re.match("[0-9]*[smh]$", date, re.IGNORECASE) is not None: #detectar si son horas, poner fecha actual
                    date = str(datetime.datetime.now())[0:10] + ' 00:00:00'
                else:
                    if len(date) > 6: #detectamos si es una fecha corta (Mar 18) y que no corte el día
                        date = re.sub(year[-2:] + "$", "", date)
                    date = str(parser.parse(date + " " + year) )
                file.write(date + "|%s"%i + "\n")


def get_tweets(query="bolsa OR IPC OR BMV", newspaper="elfinanciero_mx", year="2018", filename="file", silent=False):
    q = 'https://mobile.twitter.com/search?q=' + query + \
          '%20from%3A' + newspaper + \
          '%20since%3A'+year+'-01-01%20until%3A'+year+'-12-31&src=typd&lang=en'

    with open("%s.%s.csv"%(filename,year), "wt") as file:
        i = 0
        q = 'https://mobile.twitter.com/search?q=' + query + \
        '%20from%3A' + newspaper + '%20since%3A' + year + \
        '-01-01%20until%3A' + year +'-12-31&src=typd&lang=en'
        file.write("tweet|time|page\n") #header
        while(True): #loop para extraer todas las páginas 
            if silent == False:
                print("  Downloading page %d..."%(i+1))
            try:
                response = requests.get(q)
            except:
                raise Exception("Error al obtener página de resultados.")
            if response.status_code != 200:
                print(response.text)
                raise Exception("Error (!= 200) al obtener página de resultados.")
            
#             with open("%s_%d.html"%(query,i), 'w') as html:
#                html.write(response.text)
            
            soup = BeautifulSoup(response.text, 'lxml') #abre la primera página de búsqueda de twitter
            extract_tweets(soup, file, i, year)

            nx = soup.find("a", text=" Load older Tweets ")
            if nx != None and nx.has_attr('href'):
                q = "https://mobile.twitter.com" + nx.get_attribute_list('href')[0]
            else:
                break
            i += 1
    if silent == False:
        print("  Done!")

def main(argv):
    if len(argv) <= 4:
        print('Usage: %s "query [OR query2]" "twitter_profile" "year" "filename.txt"'%argv[0])
        print("\n\nParameters:\nquery: twitter query")
        print("twitter_profile: the twitter profile without the at sign")
        print("year: year which you need to download. E.g., 2019")
        print("filename: may or may not include a full or relative path with or w/o directory, and the output file\n")
        print("Advice: use quoted text for each one of the params.")
        return 1
    try:
       query=argv[1]
       source=argv[2]
       year=argv[3]
       filename=argv[4]
       get_tweets(query=query, newspaper=source, year=year, filename=filename)
       return 0
    except Exception as e:
        print(e)
        return 1

if __name__ == "__main__":
    main(sys.argv)
