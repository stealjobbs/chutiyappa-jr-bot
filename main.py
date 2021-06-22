#!/usr/bin/env python
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
import requests
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import time
import pickle
from random import randint
import argparse
import sys


#Configs


strLine = '-----------------------------------'


superusers = {}
insultList =[]
infoDb ={}
profilesDb = {}
configDb ={}
updater = None


with open('DB/config.json','r') as infile:
	configDb = json.load(infile)

VERSION= configDb['VERSION_R']
BOT_TOKEN = configDb['BOT_TOKEN_R'] 
TO_CHAT_ID =configDb['TO_CHAT_ID_R']      
SORRY_DAVE_GIF = configDb['SORRY_DAVE_GIF_R']
BYE_GIF = configDb['BYE_GIF_R']
DAISY_OGG = configDb['DAISY_OGG_R']
scope = configDb['scope']
user = configDb['user']
redirect_uri = configDb['redirect_uri']
client_id = configDb['client_id']
client_secret = configDb['client_secret']
playlistID = configDb['playlistID_R']


parser = argparse.ArgumentParser()
parser.add_argument('-t','--test',action = 'store_true', help = "Runs the test bot.")
args = parser.parse_args()
if args.test:
	VERSION = configDb['VERSION_T']
	BOT_TOKEN= configDb['BOT_TOKEN_T']
	TO_CHAT_ID = configDb['TO_CHAT_ID_T']
	SORRY_DAVE_GIF = configDb['SORRY_DAVE_GIF_T']
	BYE_GIF = configDb['BYE_GIF_T']
	DAISY_OGG = configDb['DAISY_OGG_T']
	playlistID = configDb['playlistID_T']
	print('ChutiyappaTest %s'%VERSION)
else : print('ChutiyappaJr %s'%VERSION)
	
try:
	updater = Updater(BOT_TOKEN)
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
												client_secret=client_secret,
												redirect_uri=redirect_uri,
												scope=scope))
except :
	print("Initialisation Failed. Exiting")
	sys.exit()
else:
	if args.test:
		print("ChutiyappaTest Online")
	else:
		print("ChutiyappaJr Online")




################################## Exclusively Backend #####################################
	

def metaData(update, context):
	print('META DATA:')
	print(update.update_id)
	print(update.channel_post)
	

def fromSteve(update,context):
	print('From Steve:')
	print(update.message)

def sendAnimation(update,context):
	context.bot.send_animation(update.message.chat_id, BYE_GIF)



############################## /dogo command methods ###################################

# getting image url- part of dogo
def get_url():
	contents = requests.get('https://random.dog/woof.json').json()
	url = contents['url']
	return url 

#filter url - part of dogo
def get_image_url():
	allowed_extension = ['jpg','jpeg','png']
	file_extension = ''
	while file_extension not in allowed_extension:
		url = get_url()
		file_extension = re.search("([^.]*)$",url).group(1).lower()
	return url

#Sends random Dogo pics
def dogo(update, context) :
	print(dogo)
	url = get_image_url()
	chat_id = update.message.chat_id
	context.bot.send_photo(chat_id= chat_id, photo=url)


################################ Spotify Mehods ##########################################


#Forwards spotify links from the group to the channel
def spotifyForward(update, context):
	print('spotifyForward')
	link = update.message.text
	if update.message.chat.type != 'private':
		if link.find("open.spotify.com")!= -1:
			if 'open.spotify.com/track' in link:
				context.bot.forwardMessage(chat_id= TO_CHAT_ID ,
											from_chat_id= update.message.chat_id,
											message_id=update.message.message_id)
				playlistAppender(link)
			elif 'open.spotify.com/album' in link:
				context.bot.send_message(update.message.chat_id, "Please limit to sharing tracks.\nYour album will be forwarded to the channel but won't be added to the playlist.")
				context.bot.forwardMessage(chat_id= TO_CHAT_ID ,
											from_chat_id= update.message.chat_id,
											message_id=update.message.message_id)
			#elif 'open.spotify.com/user' in link:

			
#Adds shared links to the spotify playlist
def playlistAppender(songLink):
	print('playlistAppender')
	startIndex = songLink.find('https')
	endIndex = 0
	endIndex1 = songLink.find(' ', startIndex)
	#print(endIndex1)
	endIndex2 = songLink.find('\n', startIndex)
	#print(endIndex2)
	#Filters the message for only the link
	if endIndex1 != -1 or endIndex2 != -1 :
		if endIndex1 == -1 and endIndex2 != -1 :
			endIndex = endIndex2
		elif endIndex2 == -1 and endIndex1 != -1  :
			endIndex = endIndex1
		elif endIndex1 != -1 and endIndex2 != -1 :
			if endIndex1<endIndex2 :
				endIndex = endIndex1
			if endIndex2<endIndex1:
				endIndex =  endIndex2
		songLink = songLink[startIndex:endIndex] 
	songLink = songLink[startIndex:]
	
	print("Forwarded song")
	print(songLink)

	songID = []
	songID.append(songLink)
	sp.user_playlist_remove_all_occurrences_of_tracks(user, playlistID, songID)
	sp.playlist_add_items(playlistID, songID)


#Sends The Curated Playlist
def sppPlaylist(update,context):
	print('sppPlaylist')
	playlist = sp.playlist(playlistID)
	playlistLink = playlist['external_urls']['spotify']
	totalTrackCount = playlist['tracks']['total']
	context.bot.send_message(update.message.chat_id, 'The best Playlist in the universe <3\n%d songs\n%s' % (totalTrackCount, playlistLink))


def addProfile(update,context):
	print('addProfile')
	if update.message.chat.type != 'private':
		username = update.message.from_user.username
		print(username)
		print(type(username))
		if username != None:
			try:
				profile = update.message.text.split()[1]
			except:
				sorryDave(update,context)
				update.message.reply_text("Incorrect usage. Correct usage:\n /add_profile <profile link>")
			else:
				if 'open.spotify.com/user' in profile:
					profilesDb = readProfile()
					if username in profilesDb:
						profilesDb[username]['profile'] = profile
						writeProfile(profilesDb)
						update.message.reply_text("Profile link updated successfully!")
						spotifyProfiles(update,context)
					else :
						profilesDb[username] = {}
						profilesDb[username]['profile'] = profile
						profilesDb[username]['playlists'] = []
						writeProfile(profilesDb)
						update.message.reply_text("Your profile was added successfully")
						spotifyProfiles(update,context)
				else: 
					sorryDave(update,context)
					update.message.reply_text("Incorrect usage. Correct usage:\n /add_profile <profile link>")
		else :
			sorryDave(update,context)
			update.message.reply_text("Please set a Telegram username before adding profile")
	else :
		sorryDave(update,context)
		update.message.reply_text("This is a group chat only feature")


def delProfile(update,context):
	print('delProfile')
	if update.message.chat.type != 'private':
		username = update.message.from_user.username
		profilesDb = readProfile()
		if username in profilesDb:
			profilesDb.pop(username)
			writeProfile(profilesDb)
			update.message.reply_text("Profile deleted successfully!")
			spotifyProfiles(update,context)
		else :
			sorryDave(update,context)
			update.message.reply_text("You don't have a profile. Create one using /add_profile")
	else:
		sorryDave(update,context)
		update.message.reply_text("This is a group chat only feature")




def addPlaylist(update,context):
	print('addPlaylist')
	if update.message.chat.type != 'private':
		username = update.message.from_user.username
		try:
			playlist = update.message.text.split()[1]	
		except :
			sorryDave(update,context)
			update.message.reply_text("Incorrect usage. Correct usage:\n /add_playlist <playlist link>")
		else:
			if 'open.spotify.com/playlist' in playlist:
				profilesDb = readProfile()
				if username in profilesDb:
					if playlist in profilesDb[username]['playlists']:
						update.message.reply_text("This playlist is already there in your profile!")
						spotifyProfiles(update,context)
					else:
						profilesDb[username]['playlists'].append(playlist)
						writeProfile(profilesDb)
						update.message.reply_text('Your playlist was added successfully!')
						spotifyProfiles(update,context)
				else : 
					sorryDave(update,context)
					update.message.reply_text("You still don't have a profile. First add your profile using /add_profile")
			else:
				sorryDave(update,context)
				update.message.reply_text("Incorrect usage. Correct usage:\n /add_playlist <playlist link>")				


def delPlaylists(update,context):
	print('delPlaylists')
	if update.message.chat.type != 'private':
		username = update.message.from_user.username
		profilesDb = readProfile()
		if len(profilesDb[username]['playlists'])>=1:
			message = update.message.text
			indexes = message[message.find(' ')+1:]
			indexLst = indexes.split(',')
			#print(indexLst)
			intIndexLst=[]
			for index in indexLst:
				intIndexLst.append(int(index))
			intIndexLst.sort(reverse=True)
			indexLst = intIndexLst
			for index in indexLst:
				if len(profilesDb[username]['playlists']) >= index:					
					profilesDb[username]['playlists'].pop(index-1)
					#print('\t', insultList)
			writeProfile(profilesDb)
			context.bot.send_message(update.message.chat_id, "Deleted playlists from valid indices!")
			spotifyProfiles(update,context)
		else: 
			retard(update)
			context.bot.send_message(update.message.chat_id, "Incorrect Usage. Usage Instructions:\n/del_playlists <index1>,<index2>...")
	else:
		sorryDave(update,context)
		update.message.reply_text("This is a group chat only feature")				

def spotifyProfiles(update,context):
	print('spotifyProfiles')
	if update.message.chat.type != 'private':
		profilesDb= readProfile()
		index1 = 1
		message=''
		for username in profilesDb:
			message += username+'\n'+profilesDb[username]['profile']+'\n'+'Favourite Playlists:\n'
			index2=1
			for playlist in profilesDb[username]['playlists']:
				playlistName=''
				try:
					playlistData = sp.playlist(playlist)
				except:
					#print("Bad url")
					playlistName = 'Unknown'
				else:
					playlistName = playlistData['name']
				message +='%d) '%index2+playlistName+'\n'+playlist+'\n'
				index2+=1
			message+='\n'+strLine+'\n'
			index1 +=1
		context.bot.send_message(update.message.chat_id, "Spotify Profiles:")	
		context.bot.send_message(update.message.chat_id, message, disable_web_page_preview=True)
	else:
		sorryDave(update, context)
		update.message.reply_text("This is a group chat only feature")	




def readProfile():
	print('readProfile')
	with open('DB/SpotifyProfiles.json', 'r') as infile:
			return json.load(infile)


def writeProfile(profilesDb):
	print('writeProfile')
	with open('DB/SpotifyProfiles.json', 'w') as outfile:
			json.dump(profilesDb, outfile, indent = 1)
	



################################### Group Chat Methods #####################################

###Add info messages
def addStart(update,context):
	print('addStart')
	if verifyUser(update, 1):
		infoDb = readInfo()
		message = update.message.text
		try:
			info = message[message.find('\n')+1:]
		except:
			update.message.reply_text("Incorrect usage. Correct usage:\n/add_start <Chat Type>\n<Message>")
		else:
			if 'P' in update.message.text.split('\n')[0]:
				infoDb['startP'] = info
				writeInfo(infoDb)
				update.message.reply_text("Start message updated successfully!")
				update.message.reply_text(readInfo()['startP'])


			elif 'G' in update.message.text.split('\n')[0]:
				infoDb['startG'] = info
				writeInfo(infoDb)
				update.message.reply_text("Start message updated successfully!")
				update.message.reply_text(readInfo()['startG'])
			else : 
				update.message.reply_text("Incorrect usage. Correct usage:\n/add_start <Chat Type>\n<Message>")
			
def addHelp(update,context):
	print('addHelp')
	if verifyUser(update,1):
		infoDb = readInfo()
		message = update.message.text
		try:
			info = message[message.find('\n')+1:]
		except:
			update.message.reply_text("Incorrect usage. Correct usage:\n/add_help <Chat Type>\n<Message>")
		else:
			if 'P' in update.message.text.split('\n')[0]:
				infoDb['helpP'] = info
				writeInfo(infoDb)
				update.message.reply_text("Help message updated successfully!")
				update.message.reply_text(readInfo()['helpP'])
			elif 'G' in update.message.text.split('\n')[0]:
				infoDb['helpG'] = info
				writeInfo(infoDb)
				update.message.reply_text("Help message updated successfully!")
				update.message.reply_text(readInfo()['helpG'])

			else : 
				update.message.reply_text("Incorrect usage. Correct usage:\n/add_help <Chat Type>\n<Message>")

def addAdminHelp(update,context):
	print('addAdminHelp')
	if verifyUser(update,1):
		infoDb = readInfo()
		message = update.message.text
		try:
			info = message[message.find('\n')+1:]
		except:
			update.message.reply_text("Incorrect usage. Correct usage:\n/add_admin_help\n<Message>")
		else:
			infoDb['adminHelp'] = info
			writeInfo(infoDb)
			update.message.reply_text("Admin help message updated successfully!")
			update.message.reply_text(readInfo()['adminHelp'])
			

def addAbout(update,context):
	print('addAbout')
	if verifyUser(update,1):
		infoDb = readInfo()
		message = update.message.text
		try:
			info = message[message.find('\n')+1:]
		except:
			update.message.reply_text("Incorrect usage. Correct usage:\n/add_about <Chat Type>\n<Message>")
		else:
			if 'P' in update.message.text.split('\n')[0]:
				infoDb['aboutP'] = info
				writeInfo(infoDb)
				update.message.reply_text("About message updated successfully!")
				update.message.reply_text(readInfo()['aboutP'])
			elif 'G' in update.message.text.split('\n')[0]:
				infoDb['aboutG'] = info
				writeInfo(infoDb)
				update.message.reply_text("About message updated successfully!")
				update.message.reply_text(readInfo()['aboutG'])

			else : 
				update.message.reply_text("Incorrect usage. Correct usage:\n/add_about <Chat Type>\n<Message>")

def addJoinMsg(update,context):
	print('addJoinMsg')
	if verifyUser(update,1):
		infoDb = readInfo()
		message = update.message.text
		try:
			info = message[message.find('\n')+1:]
		except:
			update.message.reply_text("Incorrect usage. Correct usage:\n/add_newmember_msg\n<Message>")
		else:
			infoDb['newMember'] = info
			writeInfo(infoDb)
			update.message.reply_text("New member message updated successfully!")
			update.message.reply_text(readInfo()['newMember'])

def addLeftMsg(update,context):
	print("addLeftMsg")
	if verifyUser(update,1):
		infoDb = readInfo()
		message = update.message.text
		try:
			info = message[message.find('\n')+1:]
		except:
			update.message.reply_text("Incorrect usage. Correct usage:\n/add_leftmember_msg\n<Message>")
		else:
			infoDb['leftMember'] = info
			writeInfo(infoDb)
			update.message.reply_text("Left member message updated successfully!")
			update.message.reply_text(readInfo()['leftMember'])

def start(update,context):
	print('start')
	if update.message.chat.type != 'private':
		update.message.reply_text(readInfo()['startG'])
	else : update.message.reply_text(readInfo()['startP'])

def help(update,context):
	print('help')
	if update.message.chat.type != 'private':
		update.message.reply_text(readInfo()['helpG'])
	else : update.message.reply_text(readInfo()['helpP'])	

def adminHelp(update, context):
	print('adminHelp')
	update.message.reply_text(readInfo()['adminHelp'])
	
def about(update,context):
	print('about')
	if update.message.chat.type != 'private':
		update.message.reply_text(readInfo()['aboutG'])
	else : update.message.reply_text(readInfo()['aboutP'])	

def readInfo() :
	print('readInfo')
	with open('DB/info.json','r') as infile:
		return json.load(infile)

def writeInfo(infoDb) :
	print('writeInfo')
	with open('DB/info.json', 'w') as outfile:
		json.dump(infoDb,outfile, indent = 1)


#Welcomes new user
def newMember(update, context):
	print("newMember")
	for new_member in update.message.new_chat_members:
		print(new_member)
		if new_member.first_name != 'ChutiyappaJr' :
			newMemberMsg =readInfo()['newMember']
			context.bot.send_message(update.message.chat_id, newMemberMsg %new_member.first_name)

#Gives update on removed user
def leftMember(update, context):
	print("leftMember")
	print(update.message.left_chat_member)
	leftMemberMsg = readInfo()['leftMember']
	context.bot.send_message(update.message.chat_id, leftMemberMsg%update.message.left_chat_member.first_name )

#Help message
'''
def help(update, context):
	update.message.reply_text("Chutiyappa nan appa, adhre avn obba gampa. I can send dogo pics for now. Use /dogo")
'''
#Says Bye
def bye(update,context):
	print('bye')
	context.bot.send_animation(update.message.chat_id, BYE_GIF)

#Sings Daisy
def singDaisy(update,context):	
	print('singDaisy')
	context.bot.send_message(update.message.chat_id, 'Hope you like it :)')
	context.bot.send_voice(update.message.chat_id, DAISY_OGG)

#Says Hi ;)
def hi(update,context):
	print('hi')
	username = update.message.from_user.first_name
	insultList=readInsultList()
	insult = insultList[randint(0, len(insultList))]
	context.bot.send_message(update.message.chat_id, "Hey %s. %s"%(username, insult)) 




####################################Privacy and Security###############################

def readSUlist():
	print('readSUlist')
	with open('DB/superusers.json','r') as infile:
		superusers = json.load(infile)
		return superusers

def writeSUlist(superusers):
	print('writeSUlist')
	with open('DB/superusers.json', 'w') as outfile:
		json.dump(superusers,outfile, indent =1)

def showSUlist(update,context):
	print('showSUlist')
	if verifyUser(update,1):
		superusers=readSUlist()
		update.message.reply_text(str(superusers))


def addSU(update,context):
	print('addSU')
	if verifyUser(update,1):
		message = update.message.text
		message = message.split()
		if len(message) == 3:
			accessLevel = message[1]
			username = message[2]
			superusers = readSUlist()
			if accessLevel in superusers:
				superusers[accessLevel].append(username)
				writeSUlist(superusers)
				showSUlist(update,context)
			else : update.message.reply_text('Access Level does not exist!')
		else : 
			retard(update)
			update.message.reply_text('Incorrect usage. Correct usage :\n/add_su <Access Level> <Username>')


def delSU(update,context):
	print('delSU')
	if verifyUser(update,1):
		message = update.message.text
		message = message.split()
		if len(message) == 3:
			accessLevel = message[1]
			username = message[2]
			superusers = readSUlist()
			if accessLevel in superusers:
				if username in superusers[accessLevel]:
					superusers[accessLevel].remove(username)
					writeSUlist(superusers)
					showSUlist(update,context)
					update.message.reply_text("Deleted successfully!")
				else : update.message.reply_text('Username does not exist in Access Level %s'%accessLevel)
			else : update.message.reply_text('Access Level does not exist!')
		else : 
			retard(update)
			update.message.reply_text('Incorrect usage. Correct usage :\n/del_su <Access Level> <Username>')		
 



def verifyUser(update, accessLevel):
	print('verifyUser')
	username = update.message.from_user.username
	print('\t',username,accessLevel)
	superusers = readSUlist()
	
	if accessLevel == 1:
		if username in superusers["1"]: return True

	elif accessLevel == 2:
		if username in superusers["1"] or superusers["2"]: return True
	
	else : 
		update.message.reply_text("Access denied.")
		return False


###################################Insult Management Methods#############################


#Add Insults
def addInsults(update,context):
	print('addInsults')
	if verifyUser(update,2):
		insultList=readInsultList()
		message = update.message.text
		insults = message.splitlines()
		insults.pop(0)
		duplicates=False
		if len(insults)!=0:
			for insult in insults:
				if insult not in insultList:
					insultList.append(insult)
				else : duplicates = True
			writeInsultList(insultList)
			context.bot.send_message(update.message.chat_id, "Insult/s added successfully!")
			if duplicates: context.bot.send_message(update.message.chat_id, "Duplicates have been skipped")
			showInsultList(update,context)
		else: 
			retard(update)
			context.bot.send_message(update.message.chat_id, "Incorrect Usage. Usage Instructions:\n/add_insults\n<insult1>\n<insult2>\n.\n.\n.")


def delInsults(update,context):
	print('deleteInsults')
	insultList = readInsultList()
	if verifyUser(update,2):
		if len(insultList) >=1:
			message = update.message.text
			indexes = message[message.find(' ')+1:]
			indexLst = indexes.split(',')
			print(indexLst)
			intIndexLst=[]
			for index in indexLst:
				intIndexLst.append(int(index))
			intIndexLst.sort(reverse=True)
			indexLst = intIndexLst
			for index in indexLst:
				if len(insultList) >= index:					
					insultList.pop(index-1)
					#print('\t', insultList)
			writeInsultList(insultList)
			context.bot.send_message(update.message.chat_id, "Insults at valid indexes deleted.")
			showInsultList(update,context)
		else: 
			retard(update)
			context.bot.send_message(update.message.chat_id, "Incorrect Usage. Usage Instructions:\n/del_insults <index1>,<index2>...")
 

def showInsultList(update,context):
	print('showInsultList')
	if verifyUser(update,2):
		insultList=readInsultList()
		print('\t',insultList)
		insults=''
		for i,insult in enumerate(insultList):
			i+=1
			insults =insults+ '%d) '%i+insult+'\n'
		if len(insults) <= 4096:
			context.bot.send_message(update.message.chat_id,"List of Insults :\n%s" %insults)
		else:
			parts = []
			while len(insults) > 0:
				if len(insults) > 4096:
					part = insults[:4096]
					first_lnbr = part.rfind('\n')
					if first_lnbr != -1:
						parts.append(part[:first_lnbr])
						insults = insults[(first_lnbr+1):]
					else:
						parts.append(part)
						insults = insults[4096:]
				else:
					parts.append(insults)
					break
			for part in parts:
				context.bot.send_message(update.message.chat_id,part)

def readInsultList():
	print('readInsultList')
	with open('DB/InsultList.txt', 'rb') as infile:
		insultList = pickle.load(infile)
		return insultList
		print('\t',insultList)

def writeInsultList(insultList):
	print('writeInsultList')
	print('\t', insultList)
	with open('DB/InsultList.txt', 'wb') as outfile:
			pickle.dump(insultList, outfile)

def retard(update):
	print('retard')
	update.message.reply_text('Retard')

def sorryDave(update, context):
	print('sorryDave')
	context.bot.send_animation(update.message.chat_id, SORRY_DAVE_GIF)
	time.sleep(0.1)	


###################################### MAIN ###############################################

def main():


	dp = updater.dispatcher 

	dp.add_handler(CommandHandler('dogo', dogo))
	dp.add_handler(CommandHandler('help', help))
	dp.add_handler(CommandHandler('admin_help', adminHelp))
	dp.add_handler(CommandHandler('about', about))
	dp.add_handler(CommandHandler('start',start))
	dp.add_handler(CommandHandler('hi',hi))
	dp.add_handler(CommandHandler('hey',hi))
	dp.add_handler(CommandHandler('bye',bye))
	dp.add_handler(CommandHandler('sing',singDaisy))

	dp.add_handler(CommandHandler('playlist', sppPlaylist))	
	dp.add_handler(CommandHandler('spotify_profiles', spotifyProfiles))
	dp.add_handler(CommandHandler('add_profile', addProfile))
	dp.add_handler(CommandHandler('del_profile', delProfile))
	dp.add_handler(CommandHandler('add_playlist', addPlaylist))
	dp.add_handler(CommandHandler('del_playlists', delPlaylists))
	
	dp.add_handler(CommandHandler('add_start',addStart))
	dp.add_handler(CommandHandler('add_help',addHelp))
	dp.add_handler(CommandHandler('add_about',addAbout))
	dp.add_handler(CommandHandler('add_joinmsg', addJoinMsg))
	dp.add_handler(CommandHandler('add_leftmsg', addLeftMsg))
	dp.add_handler(CommandHandler('add_admin_help', addAdminHelp))



	dp.add_handler(CommandHandler('add_su',addSU))
	dp.add_handler(CommandHandler('del_su',delSU))
	dp.add_handler(CommandHandler('show_su',showSUlist))

	dp.add_handler(CommandHandler('add_insults',addInsults))
	dp.add_handler(CommandHandler('del_insults',delInsults))
	dp.add_handler(CommandHandler('show_insults',showInsultList))
	

	dp.add_handler(CommandHandler('meta', metaData))




#	dp.add_handler(CommandHandler('send_ani',sendAnimation))
	#dp.add_handler(CommandHandler('save_file', saveFile))
	#dp.add_handler(CommandHandler('hey', hey))
	#dp.add_handler(CommandHandler('bye', bye))
	#dp.add_handler(CommandHandler('about' about))
	
	#dp.add_handler(MessageHandler(Filters.text, metaData))
	dp.add_handler(MessageHandler(Filters.chat(218785074), fromSteve))
	dp.add_handler(MessageHandler(Filters.command, sorryDave))
	dp.add_handler(MessageHandler(Filters.text & ~Filters.command, spotifyForward))
	dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, newMember))
	dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, leftMember))
	

	
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
