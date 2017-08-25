#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twython import TwythonStreamer
import string
from multiprocessing import Process, Pipe
from threading import Thread
import logging
import csv
import sys
from _thread import start_new_thread
import datetime
from textblob import TextBlob
import re
import time
APP_KEY = ''
APP_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''

crypto_list = {
'bitcoin_acronyms' : ['btc','bitcoin','xbt'],
'ethereum_acronyms' : ['eth','ethereum','ether'],
'district0x_acronyms' : ['dnt','district0x'],
'omisego_acronyms' : ['omg','omisego'],
'litecoin_acronyms' : ['ltc','litecoin'],



}


bitcoin_acronyms = ['btc','bitcoin','xbt']
ethereum_acronyms = ['eth','ethereum','ether']
district_acronyms = ['dnt', 'district0x']

def clean_tweet(tweet):
	'''
	Utility function to clean tweet text by removing links, special characters
	using simple regex statements.
	'''
	return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
 

def get_tweet_sentiment(tweet):
	'''
	Utility function to classify sentiment of passed tweet
	using textblob's sentiment method
	'''
	# create TextBlob object of passed tweet text
	analysis = TextBlob(tweet)
	# set sentiment
	if analysis.sentiment.polarity > 0:
		return 'positive'
	elif analysis.sentiment.polarity == 0:
		return 'neutral'
	else:
		return 'negative'

class MyStreamer(TwythonStreamer):

	hot  = ['buy','up'	,'increase ','rise' ,'expand' , 'hold', 'hodl', 'moon','pump','bull','bullish','uptrend','rally']
	cold = ['sell','down','decrease','bear','bearish','dump','downtrend','sell','dip']
	count = 0.0
	heat = 0.0
	sentiment_count = 0.0
	def __init__(self,APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET,currency):
		super(self.__class__,self).__init__(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
		self.currency_name = currency[0]

	# def __init__(self, APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET,currency):
	# 	super().__init__(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET,currency)
	# 	self.currency_name = currency[0]

	def on_success(self, data):
		if 'text' in data.keys(): 
			# print (data['text'],data["retweet_count"])
			results = []
			tweet = data['text']
			tweet = tweet.encode('utf-8')
			tweet = tweet.translate(None, string.punctuation)
			tweet = clean_tweet(tweet)
			sentiment = get_tweet_sentiment(tweet)

			if sentiment == 'positive':
				self.sentiment_count += 1
			elif sentiment == 'negative':
				self.sentiment_count -= 1


			self.count += 1

			if any(element in tweet.lower().split(' ') for element in self.hot):
				self.heat +=1
			elif any(element in tweet.lower().split(' ') for element in self.cold):
				self.heat -=1

			if self.count >= 10 :
				print (self.currency_name)

				self.heatness = float(self.heat/self.count)
				current_date = datetime.datetime.now()
				current_date = current_date.strftime('%d/%m/%y %H:%S')
				self.sentiment_value = float(self.sentiment_count/self.count)
				results.append([self.currency_name,current_date,self.heatness,self.sentiment_value])

				with open('output.csv', 'a') as csvfile:
					spamwriter = csv.writer(csvfile, delimiter=';', quotechar='|')
					spamwriter.writerow(results)	


				print('currency name : ',self.currency_name)
				print('heat : ', (float(self.heatness/self.count)))				
				print('sentiment : ', (float(self.sentiment_count/self.count)))				

				self.count = 0

	def on_error(self, status_code, data):
		print (status_code)





def twitter_listener(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, currency):    
	streamer = MyStreamer(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET,currency)
	streamer.statuses.filter(track=currency, language='en')





if __name__ == '__main__':


	streamlist = [None] * len(crypto_list)
	cpt = 0
	try:
		for crypto in crypto_list.keys():
			streamlist[cpt] = MyStreamer(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET,currency=crypto_list[crypto])
			p=Thread(target = twitter_listener, args = (APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, [crypto_list[crypto][0]], ))
			p.daemon=True
			p.start()
			cpt += 1
			print crypto_list[crypto]
		print streamlist
		while True: time.sleep(100)

	except (KeyboardInterrupt, SystemExit):
	  print '\n! Received keyboard interrupt, quitting threads.\n'

