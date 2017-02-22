from flask import Flask, request, render_template, redirect, session
from random import randint
import re
app = Flask(__name__)
app.secret_key = 'verysecretkeyyoucantguess'

dicFile = open("words2.txt", "r")
wordList = dicFile.read().split('\n')
dicFile.close()

@app.route('/hangman')
def hangman():
	if 'realWord' not in session: # initiate game vars
		session['reset']=True
		session['wins'] = 0
		session['losses'] = 0
	if session['reset'] == True: # initiate session/instance vars
		wordIdx = randint(0,len(wordList)-1)
		session['realWord'] = wordList[wordIdx].upper()
		wordList.remove(wordList[wordIdx])
		session['shownWord'] = "_ " * len(session['realWord'])
		session['guessCount']=0
		session['guessLeft'] = 10
		session['guessList'] = []
		session['reset']=False
	return render_template("game.html", shownWord=session['shownWord'], guessList=sorted(session['guessList']), guessLeft=str(session['guessLeft']),wins=session['wins'],losses=session['losses'])

@app.route('/hangman/done')
def endstate(): #display thank you message and score
	s='''<h1> Thanks for playing!</h1><h2> You won '''+str(session['wins'])+''' game(s) and lost '''+str(session['losses'])+''' game(s)</h2>'''
	session.clear()
	return s
	
@app.route('/hangman/guess',methods=['POST'])
def guess(): # logic for determining response to a guess
	guess = request.form['guess'].upper()
	if (len(guess) != 1 and len(guess) != len(session['realWord'])) or not guess.isalpha(): # check if valid input
		session['fail'] = "Invalid entry, please guess either a single letter or the whole word."
		session['success'] = ''
	elif guess in session['guessList']: #check if already guessed
		session['fail'] = "You already guessed that!"
		session['success'] = ''
	else: # check answer
		session['guessList'].append(guess)
		if guess == session['realWord']: #check if correct word guess
			session['shownWord'] = guess
			session['guessCount'] += 1
		elif guess in session['realWord']: #check if correct letter guess
			guessLocs = [i.start() for i in re.finditer(guess, session['realWord'])]
			session['shownWord'] = session['shownWord'].replace(" ", "")
			session['shownWord'] = list(session['shownWord'])
			for loc in guessLocs:
				session['shownWord'][loc] = guess
			session['shownWord'] = " ".join(session['shownWord'])
			session['guessCount'] += 1
			if len(guessLocs)==1:
				session['success'] = "There's " + str(len(guessLocs)) + " " + guess
			else:
				session['success'] = "There are " + str(len(guessLocs)) + " " + guess + "'s!"
			session['fail'] = ''
		else: #if not correct, subtract guess
			session['guessLeft'] -= 1
			session['guessCount'] += 1
			session['fail'] = "Nope! No " +  guess + "'s!"
			session['success'] = ''
		if session['guessLeft'] == 0: #lose state
			session['fail'] = "GAME OVER... the word was " + session['realWord']
			session['success'] = ''
			session['losses']+=1
			session['reset']=True
		elif [i.start() for i in re.finditer("_", session['shownWord'])] == []: #win state
			session['success'] = "Correct! You got it in " + str(session['guessCount']) + "guesses"
			session['fail'] = ''
			session['wins']+=1
			session['reset']=True
	return redirect('/hangman')

if __name__ == "__main__":
    app.run()