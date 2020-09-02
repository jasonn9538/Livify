'''
	File Name: Livify.py
	Author: Jason Nguyen
	Date Created: 2 September 2020
	Date Last Modified: 2 September 2020
	Python Version 3.8

'''

########################################################################################################################################

'''

	CONTENTS:
	
		1. Introduction
		2. Data Gathering
		3. Grabbing Spotify Audio Features
		4. Creating a Database of Probabilities
		5. Time to Organize
		6. TODO
		7. Salutations
		
'''

########################################################################################################################################

'''

	1. Introduction:

		In this project of mine, I used information from a website that hosts user inputed tracklists from popular DJs.
		I took this information from the website and focused on the transitions that DJs made going from one song into another.
		I recorded this data and transformed it into usable data that outlines the songs audio features using the Spotify API.
		Now we have data on if song X we can recommend song Y that goes after. We do this by analyzing the audio features of song X 
		such as tempo, key, mode, liveness, loudness, energy, danceability, and more. Knowing the audio features of song X, we have
		data that we gained previously on what type of song would come after song X, we get the best fitting song Y determined from 
		thousands of transitions by popular DJs. We use the song Y features and grab the song in the playlist that most closely matches
		the features of song Y. 

		*****
		Using this program, we can take an entire spotify playlist and sort the playlist into the best flowing DJ set.
		*****

		In this python file, I will show some of the code that I use to make this project and explain the steps.

		Disclaimer: I will be excluding certain modules I used as this is a file to outline my coding methods rather than a code for
		someone to use for themselves. If you are interested in using this program. Please message me on Github or open an issue 
		and I will work on making a usable version. I will also not be mentioning the website I took this information from due to them
		wanting to make sure that their data was kept secret. Thank you.

'''

########################################################################################################################################

'''

	2. Data Gathering:

		I had a txt file that I stored links from the previously mentioned website. I grabbed thousands of DJ sets in 
		all different genres to ensure that the program was able to analyze and recommend the right type of songs. I
		used an API from another person found on GitHub that scraped the website and only took pairs of songs that 
		we played right after another, also referred to as tranitioning into each other. If the songs had a Spotify
		link attached to them, the transition was recorded into a csv file.

'''

file1 = open("links.txt","r") 

links = file1.readlines()

for link in links:

	print(link)
	tracklist = Tracklist(link)

	# Initial fetch
	tracklist.fetch()

	# Get a list of tracks
	tracks = tracklist.get_tracks()

	# Get spotify and apple id for the first track

	with io.open('livify_db.csv', 'a') as new_file:
		csv_writer = csv.writer(new_file, lineterminator = '\n')
		for i in range(0, len(tracks)-1):

			# If song i and song i+1 had spotify links, the link was recorded. That meant that a transition with both
			# songs were added to the database. 

			if 'spotify' in tracks[i].external_ids and 'spotify' in tracks[i+1].external_ids:

				line = track1, i, tracks[i].get_external('spotify'), 'next', track2, i+1, tracks[i+1].get_external('spotify')
				print(line)
				try:
					csv_writer.writerow(line)
				except:
					print("FAILED ADDING TRANSITION")

	# Made sure to have the program sleep inbetween fetching the tracklists to make sure the website didn't time us out.

	sleeping = random.uniform(1,20)
	print("Sleeping for: ", sleeping)
	time.sleep(sleeping)



########################################################################################################################################

'''

	3. Grabbing Spotify Audio Features:

		This part of the program grabs all of the spotify URI's that were recorded in the data dathering step and fetches the spotify 
		audio features using the Spotify API. It takes all of the transitions recorded in the initial transition database and adds audio 
		features and then records them all to a json file for faster reading for the next step.

'''

# My spotify credentials are ommited for obvious reasons
Client_ID = ''
Client_Secret = ''
Username = ''
Scope = ''
Redirect_URL = ''

# An initialize connection function that I created to better and easier connect to the Spotify API. Preciously, I had to type in the terminal
# each of the enviroment variables. I created this function to not only skip that step but to create 
# the spotify connection and return the spotify 
# 

def init_connection(Client_ID, Client_Secret, Username, Redirect_URL):

	scope = 'playlist-modify-private'

	init_cmd = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI"]
	init_cmd_imputs = [Client_ID, Client_Secret, Redirect_URL]
	for i in range(0,len(init_cmd)):
		os.environ[init_cmd[i]] = init_cmd_imputs[i]

	token = util.prompt_for_user_token(Username, scope)

	sp = spotipy.Spotify(auth=token)

	return sp

sp = init_connection(Client_ID, Client_Secret, Username, Redirect_URL)

db = {}

# Opens transition database

with open('livify_db.csv', newline='') as csvfile:
	reader = list(csv.reader(csvfile, delimiter=',', quotechar='|'))

# Grabs spotify URIs and fetches audio features for each of the songs.

for i in range(0,len(reader)):

	print("{}/{}".format(i, len(reader)), reader[i])

	link_URI_from = ast.literal_eval(reader[i][2])['spotify']
	link_URI_to = ast.literal_eval(reader[i][6])['spotify']

	db[i] = {'from_song_name':reader[i][0], 'from_index': reader[i][1], 'from_audio_features': sp.audio_features(link_URI_from)[0],
			 'to_song_name': reader[i][4], 'to_index': reader[i][5], 'to_audio_features': sp.audio_features(link_URI_to)[0]}

# Dumps all of the new database into a json file for faster reading.

a_file = open("database.json", "w")
json.dump(db, a_file)
a_file.close()



########################################################################################################################################

'''

	4. Creating a Database of Probabilities:

		Now that I have a json file which I read and store as a dictionary. I look through the dictionary and grab each of the audio
		features from the songs. I create a new database and count each variable's(ex. acousticness, dancebility, tempo, etc.) instances of
		song X transitioning into song Y's variable. I then go through that dictionary again and transform the counts of times that transition
		was made into probabilities.

'''

db = json.load(open("database.json","r"))

acousticness_change = defaultdict(dict)
danceability_change = defaultdict(dict)
energy_change = defaultdict(dict)
instrumentalist_change = defaultdict(dict)
key_change = defaultdict(dict)
liveness_change = defaultdict(dict)
loudness_change = defaultdict(dict)
mode_change = defaultdict(dict)
speechiness_change = defaultdict(dict)
tempo_change = defaultdict(dict)
time_signature_change = defaultdict(dict)
valence_change = defaultdict(dict)

for i in db:

	# acousticness
	from_acousticness = round(db[i]['from_audio_features']['acousticness'], 1)
	to_acousticness = round(db[i]['to_audio_features']['acousticness'], 1)
	# print(from_acousticness, to_acousticness)
	try:
		acousticness_change[from_acousticness][to_acousticness] += 1
	except KeyError:
		acousticness_change[from_acousticness][to_acousticness] = 1

	# danceability
	from_danceability = round(db[i]['from_audio_features']['danceability'], 1)
	to_danceability = round(db[i]['to_audio_features']['danceability'], 1)
	# print(from_danceability, to_danceability)
	try:
		danceability_change[from_danceability][to_danceability] += 1
	except KeyError:
		danceability_change[from_danceability][to_danceability] = 1

	# energy
	from_energy = round(db[i]['from_audio_features']['energy'], 1)
	to_energy = round(db[i]['to_audio_features']['energy'], 1)
	# print(from_energy, to_energy)
	try:
		energy_change[from_energy][to_energy] += 1
	except KeyError:
		energy_change[from_energy][to_energy] = 1

	# instrumentalness
	from_instrumentalness = round(db[i]['from_audio_features']['instrumentalness'], 1)
	to_instrumentalness = round(db[i]['to_audio_features']['instrumentalness'], 1)
	# print(from_instrumentalness, to_instrumentalness)
	try:
		instrumentalist_change[from_instrumentalness][to_instrumentalness] += 1
	except KeyError:
		instrumentalist_change[from_instrumentalness][to_instrumentalness] = 1
	
	# key
	from_key = int(db[i]['from_audio_features']['key'])
	to_key = int(db[i]['to_audio_features']['key'])
	# print(from_key, to_key)
	try:
		key_change[from_key][to_key] += 1
	except KeyError:
		key_change[from_key][to_key] = 1

	# liveness
	from_liveness = round(db[i]['from_audio_features']['liveness'], 1)
	to_liveness = round(db[i]['to_audio_features']['liveness'], 1)
	# print(from_liveness, to_liveness)
	try:
		liveness_change[from_liveness][to_liveness] += 1
	except KeyError:
		liveness_change[from_liveness][to_liveness] = 1

	# loudness
	from_loudness = two_round(db[i]['from_audio_features']['loudness'], 2)
	to_loudness = two_round(db[i]['to_audio_features']['loudness'], 2)
	# print(from_loudness, to_loudness)
	try:
		loudness_change[from_loudness][to_loudness] += 1
	except KeyError:
		loudness_change[from_loudness][to_loudness] = 1

	# mode
	from_mode = int(db[i]['from_audio_features']['mode'])
	to_mode = int(db[i]['to_audio_features']['mode'])
	# print(from_mode, to_mode)
	try:
		mode_change[from_mode][to_mode] += 1
	except KeyError:
		mode_change[from_mode][to_mode] = 1

	# speechiness
	from_speechiness = round(db[i]['from_audio_features']['speechiness'], 1)
	to_speechiness = round(db[i]['to_audio_features']['speechiness'], 1)
	# print(from_speechiness, to_speechiness)
	try:
		speechiness_change[from_speechiness][to_speechiness] += 1
	except KeyError:
		speechiness_change[from_speechiness][to_speechiness] = 1


	# tempo 
	from_tempo = two_round(db[i]['from_audio_features']['tempo'], 2)
	to_tempo = two_round(db[i]['to_audio_features']['tempo'], 2)
	# print(from_tempo, to_tempo)
	try:
		tempo_change[from_tempo][to_tempo] += 1
	except KeyError:
		tempo_change[from_tempo][to_tempo] = 1

	# time_signature
	from_time_signature = int(db[i]['from_audio_features']['time_signature'])
	to_time_signature = int(db[i]['to_audio_features']['time_signature'])
	# print(from_time_signature, to_time_signature)
	try:
		time_signature_change[from_time_signature][to_time_signature] += 1
	except KeyError:
		time_signature_change[from_time_signature][to_time_signature] = 1

	# valence
	from_valence = round(db[i]['from_audio_features']['valence'], 1)
	to_valence = round(db[i]['to_audio_features']['valence'], 1)
	# print(from_valence, to_valence)
	try:
		valence_change[from_valence][to_valence] += 1
	except KeyError:
		valence_change[from_valence][to_valence] = 1


total_change_db = collections.OrderedDict()

total_change_db['acousticness_change'] = acousticness_change
total_change_db['danceability_change'] = danceability_change
total_change_db['energy_change'] = energy_change
total_change_db['instrumentalness_change'] = instrumentalist_change
total_change_db['key_change'] = key_change
total_change_db['liveness_change'] = liveness_change
total_change_db['loudness_change'] = loudness_change
total_change_db['mode_change'] = mode_change
total_change_db['speechiness_change'] = speechiness_change
total_change_db['tempo_change'] = tempo_change
total_change_db['time_signature_change'] = time_signature_change
total_change_db['valence_change'] = valence_change

for i in total_change_db:

	for j in total_change_db[i]:

		sum = 0

		for x in total_change_db[i][j]:

			sum += total_change_db[i][j][x]

		for x in total_change_db[i][j]:

			total_change_db[i][j][x] = total_change_db[i][j][x] / sum



########################################################################################################################################

'''

	5. Time To Organize:

		I now have a vast database full of probabilities of DJs transitions and if given song X, how to proceed into the best song Y.
		To utilize this data, the code below, grabs a spotify playlist link and a new spotify playlist URI to paste the organized playlist
		into. For ease, a spotify playlist full of songs (playlist A) and an empty playlist to paste it into (playlist B). The code below, 
		fetches all of the songs and the songs audio features in playlist A. Then, using the probability database, it finds the best sequence
		to order the entire playlist by testing every combination of the playlist and adds the new ordered sequence into the new playlist. 
		The code is completed and the playlist is ready to listen to.

'''

playlist_ID = ''
new_playlist = ''

offset = 0
playlist = sp.playlist_tracks(playlist_ID, offset = offset)
count = 0
playlist_URIs = []
while len(playlist['items']) != 0:
	for i in playlist['items']:
		count += 1
		playlist_URIs.append(i['track']['uri'])
	offset += 100
	playlist = sp.playlist_tracks(playlist_ID, offset=offset)

playlist_data = defaultdict(dict)

count_import = 1
for i in playlist_URIs:

	print('Importing track: {}/{}'.format(count_import, len(playlist_URIs)))
	count_import += 1
	track_features = sp.audio_features(i)[0]
	playlist_data[i]['acousticness'] = round(track_features['acousticness'], 1)
	playlist_data[i]['danceability'] = round(track_features['danceability'], 1)
	playlist_data[i]['energy'] = round(track_features['energy'], 1)
	playlist_data[i]['instrumentalness'] = round(track_features['instrumentalness'], 1)
	playlist_data[i]['key'] = track_features['key']
	playlist_data[i]['liveness'] = round(track_features['liveness'], 1)
	playlist_data[i]['loudness'] = two_round(track_features['loudness'])
	playlist_data[i]['mode'] = track_features['mode']
	playlist_data[i]['speechiness'] = round(track_features['speechiness'], 1)
	playlist_data[i]['tempo'] = two_round(track_features['tempo'])
	playlist_data[i]['time_signature'] = track_features['time_signature']
	playlist_data[i]['valence'] = round(track_features['valence'], 1)

playlist_data_copy = playlist_data.copy()

final_order = []
best_difference = 9999999999999999999
counter = 1

for i in playlist_data:

	print(counter)
	counter += 1

	track_X_URI = i

	playlist_data = playlist_data_copy.copy()

	new_order = []

	total_difference = 0

	new_order.append(track_X_URI)

	while len(playlist_data) > 1:

		track_X_data = playlist_data[track_X_URI]

		del playlist_data[track_X_URI]

	# 	# find track x changes

		track_Y_features = {}

		for i in track_X_data:

			values = [x for x in total_change_db['{}_change'.format(i)][track_X_data[i]]]
			probs = [total_change_db['{}_change'.format(i)][track_X_data[i]][x] for x in total_change_db['{}_change'.format(i)][track_X_data[i]]]

			if not values:

				total_change_db['{}_change'.format(i)].pop(track_X_data[i])
				test_dict = {}
				test_dict = total_change_db['{}_change'.format(i)]
				search_key = track_X_data[i]

				res = test_dict[min(test_dict.keys(), key = lambda key: abs(key-search_key))]

				values = list(res.keys())
				probs = [res[x] for x in res]

			pick = values[probs.index(max(probs))]

			track_Y_features[i] = pick

		track_Y_pick = ''
		track_Y_similarity = 999999999999999

		for i in playlist_data:

			track_Y_data = playlist_data[i]

			similarity_score = 0

			for j in track_Y_features:

				# Tempo is given a larger weight because we want the lowest flucuation between tempo to have the music "flow"
				if j == 'tempo' or j == 'loudness':
					similarity_score += (((track_Y_features[j]/20)-(track_Y_data[j]/20))**2)
				elif j == 'key':
					similarity_score += (((track_Y_features[j]/10)-(track_Y_data[j]/10))**2)
				else:
					similarity_score += (track_Y_features[j]-track_Y_data[j])**2

			if similarity_score < track_Y_similarity:

				track_Y_similarity = similarity_score
				track_Y_pick = i
				track_Y_pick_data = track_Y_data

		track_X_URI = track_Y_pick

		total_difference += track_Y_similarity

		new_order.append(track_Y_pick)

	if best_difference > total_difference:

		best_difference = total_difference
		final_order = new_order

		print("New best order found")

print(final_order, len(final_order))

chunks = [final_order[x:x+100] for x in range(0, len(final_order), 100)]

for i in chunks:
	
	sp.user_playlist_add_tracks(Username, playlist_id=new_playlist, tracks = i)

########################################################################################################################################

'''

	6. TODO:

		There is still plenty to do in this program to make the AI smarter and make better organized playlist. This includes finding 
		a better data structure to store individual tracks' audio features into so that it creates a "song profile". This way, we can
		use every variable in conjunction to each other to reccomend the next track rather than using each variable independently. If
		I were to implement the song profile data structure, the AI will need a LOT more training as there are almost 1000000000 different 
		song profiles that could possibly exist. 

		Taking this program and adding a web UI with Django and Heroku will most likely be the next step after ensuring that the recommender
		algorithm is working to the best of it's ability.

'''

########################################################################################################################################

'''

	7. Salutations:

		Thank you for reading this project of mine and feel free to message me if you have any questions.

'''
