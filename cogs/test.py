import random
import time

word_list = open("./../authdict.txt", "r")
words = word_list.readlines()

for x in range (0, len(words)):
    words[x] = words[x].replace("\n", "")

first_word = random.sample(words,1)
auth_phrase = first_word[0]

for x in range (0, 5):

    joiners = [" and ", " the ", " do ", " can "]
    concater = random.sample(joiners, 1)
    word = random.sample(words,1)

    new_phrase = concater[0] + word[0]
    auth_phrase += new_phrase

print(auth_phrase)
time.sleep(5)