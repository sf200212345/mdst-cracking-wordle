# contains your implementation of algorithms

import random
from utility import *

# referred to as the brute force algorithm in week 2 slides
# idea here is to only limit solution space to words that match the feedback pattern of your most recent guess WHEN COMPARED WITH THE SOLUTION
def only_matched_patterns(current_guesses, guess_feedback, valid_solutions):
    remaining_solutions = []
    for word in valid_solutions:
        current_word_feedback = generate_feedback(current_guesses[-1], word)
        if current_word_feedback == guess_feedback[-1]:
            remaining_solutions.append(word)
    return random.choice(remaining_solutions)
