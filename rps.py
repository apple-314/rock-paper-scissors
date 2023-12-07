# could do based on win/loss instead of actual values
# multi armed bandit approach

from scipy import stats
import random
import matplotlib.pyplot as plt
import datetime
import json

n = 1 # number of moves to look back

rps_dict = {'r': 0, 'p': 1, 's': 2}
rps_dict_rev1 = {0: 'r', 1: 'p', 2: 's'}
rps_dict_rev2 = {0: 'rock', 1: 'paper', 2: 'scissors'}

record = {}

def create_permutations(n, soFar = ''): # creates the record dictionary
	if (n == 0):
		record[soFar] = [[2, 2], [2, 2], [2, 2]] # initialize with laplace prior
		return

	for i in rps_dict.keys():
		create_permutations(n - 1, soFar + i)

# set up data
load_data = input("Load data? (n for no or filename)  ")
print()
print()
if load_data == 'n':
	create_permutations(n)
else:
	record = json.load(open("data/" + load_data + '.json'))

# -----------------------------------------------------------------
# play game!

streak = []
ct = 0
cur = ""
while True:
	# get the player's move
	while True:
		op = input(str(ct + 1) + ": rock (r), paper (p), or scissors (s)? (q to quit)  ")
		if op in ['r', 'p', 's', 'q']:
			break
		print("Invalid input")

	if op == 'q':
		break

	cur += op
	move = -1

	# determine bot's move
	if ct < n: # we haven't played long enough, so guess randomly
		move = random.randrange(3)
	else:
		state = cur[:n]
		high = 0
		for i, val in enumerate(record[state]):
			sample = stats.beta.rvs(val[0], val[1])
			if sample > high:
				high = sample
				move = i

	print("I play " + rps_dict_rev2[move])

	# analyze result and update weights
	op = rps_dict[op]
	if (move == op): # it's a tie
		if ct >= n:
			record[cur[:n]][(move+1)%3][0] += 1 # if the bot had won
			record[cur[:n]][(move+2)%3][1] += 1 # if the bot had lost
		streak.append(0)
		print("Tie!")
	elif ((move - op + 3) % 3 == 1): # the bot wins
		if ct >= n:
			record[cur[:n]][move][0] += 1 # what the bot won with
			record[cur[:n]][(move+1)%3][1] += 1 # if the bot had lost
		streak.append(1)
		print("I win!")
	else: # the player wins
		if ct >= n:
			record[cur[:n]][move][1] += 1 # what the bot lost with
			record[cur[:n]][(move+2)%3][0] += 1 # if the bot had won
		streak.append(-1)
		print("You win!")

	if ct >= n:
		cur = cur[1:]
	ct += 1
	# print(record)
	print()

print("wins: " + str(streak.count(1)))
print("losses: " + str(streak.count(-1)))
print("ties: " + str(streak.count(0)))

# plots
running_streak = []
running_ct = 0
for i in streak:
	running_ct += i
	running_streak.append(running_ct)

plt.plot([i + 1 for i in range(len(running_streak))], running_streak, marker=".", c = "blue")
plt.xlabel("Game Number")
plt.ylabel("Net Wins")
plt.title("Opponent moves only, n = " + str(n))

# save data
print()
print()
save_data = input("Save data? (n for no, d for default datetime path, or custom filename)  ")
if save_data == 'n':
	exit()
elif save_data == 'd':
	save_data = str(datetime.datetime.today())[:19]
save_data = "data/" + save_data
json.dump(record, open(save_data + '.json', 'w'))
plt.savefig(save_data + ".png") # file name is datetime without decimal of seconds
