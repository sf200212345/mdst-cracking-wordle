# contains the implementation of the base Wordle game class

import pathlib
import random
import string

# https://gist.github.com/cfreshman/d97dbe7004522f7bc52ed2a6e22e2c04
GUESSES_PATH = pathlib.Path(__file__).parent / "valid_guesses.txt"

# https://www.kaggle.com/datasets/bcruise/wordle-valid-words
SOLUTIONS_PATH = pathlib.Path(__file__).parent / "valid_solutions.txt"

WORD_LENGTH = 5
NUM_GUESSES = 6

# Wordle class: runs all the Wordle games. Has various flags for how the game class should accept input and how it should display output.
class Wordle:
  def __init__(self, input_function=None, verbose=True, stats=True, simulate=0, initial_guesses=[]) -> None:
    # read word lists into memory, ENFORCING ALL WORDS AS CAPITAL LETTERS
    with open(GUESSES_PATH, "r") as read_obj:
      self.valid_guesses = read_obj.read().split()
      for i in range(len(self.valid_guesses)):
        self.valid_guesses[i] = self.valid_guesses[i].upper()
    with open(SOLUTIONS_PATH, "r") as read_obj:
      self.valid_solutions = read_obj.read().split()
      for i in range(len(self.valid_solutions)):
        self.valid_solutions[i] = self.valid_solutions[i].upper()

    # README
    # keep track of the input function. If you want to accept input from the user, input_function will be of type None
    # all input functions will have a common interface:
    # accepts the arguments: current_guesses, guess_feedback, filtered_guesses, valid_solutions
    # where current_guesses, guess_feedback match their definition down below in the play function
    # and filtered_guesses is the result returned by filter_on_feedback in the Wordle class
    # This function will return a string to be used as the next guess
    self.input_function = input_function

    # verbose = True means print_state will be used after every guess. Otherwise, only the stats are printed.
    self.verbose = verbose

    # stats = True means stats will be printed after every game, otherwise stats will be printed at the end
    self.stats = stats

    # simulate > 0 means you want to simulate the input number of rounds.
    # otherwise the game class will prompt you if you want to continue playing
    self.simulate = simulate

    # keep a list of initial guesses to use, if your algorithm demands it
    # this will be used to initialize current_guesses in the play loop
    self.initial_guesses = initial_guesses
    for i in range(len(self.initial_guesses)):
      self.initial_guesses[i] = self.initial_guesses[i].upper()

    # keep relevant stats
    self.num_games = 0
    self.num_guesses = 0
    self.num_wins = 0

  def play(self) -> None:
    while True:
      # select solution word
      current_solution = random.choice(self.valid_solutions)

      current_guesses = self.initial_guesses.copy()

      # C for correct, M for misplaced, W for wrong
      guess_feedback = []

      # since there are initial guesses now, also need to populate guess_feedback
      for i in current_guesses:
        guess_feedback.append(self.generate_feedback(i, current_solution))

      # start a game
      for guess_num in range(len(current_guesses), NUM_GUESSES):
        if self.input_function is None:
          current_guess = input(f"Guess {guess_num + 1}: ").upper()
        else:
          current_guess = self.input_function(current_guesses,
                                              guess_feedback,
                                              self.filter_on_feedback(current_guesses, guess_feedback),
                                              self.valid_solutions)

        # make sure the user guess is valid
        while not self.is_valid_guess(current_guess):
          if self.input_function is None:
            current_guess = input(f"Invalid guess, try again. Guess {guess_num + 1}: ").upper()
          else:
            # should not ever get to this else statement, since input_function should return a word from the list of valid guesses/solutions
            current_guess = self.input_function(current_guesses,
                                                guess_feedback,
                                                self.filter_on_feedback(current_guesses, guess_feedback),
                                                self.valid_solutions)

        # valid guess has been obtained
        current_guesses.append(current_guess)
        if current_guess == current_solution:
          break

        # generate feedback for current guess
        # change to "C" if correct, change to "M" if misplaced. W is wrong
        guess_feedback.append(self.generate_feedback(current_guess, current_solution))


        # print state after every guess
        if self.verbose:
          self.print_state(current_guesses, guess_feedback)

      # ending states
      if self.verbose:
        if current_guesses[-1] == current_solution:
            print(f"\nCongratulations! You have correctly guessed {current_solution} in {len(current_guesses)} tries!")
        else:
            print(f"\nUnfortunately, you have failed to correctly guess {current_solution}.")

      # update stats and print after each game
      self.get_print_stats(current_guesses[-1] == current_solution, len(current_guesses))

      # let user decide when to quite when simulate == 0
      if self.simulate == 0:
        if input("Enter 'quit' to quit. Enter anything else to continue playing: ").upper() == "QUIT":
            break
      else:
        if self.simulate == self.num_games:
          break

  # checks if a guess is valid. Current guess has to be WORD_LENGTH in length, all letters, and in valid_guesses
  def is_valid_guess(self, current_guess: str) -> bool:
    return len(current_guess) == WORD_LENGTH and current_guess.isalpha() and current_guess.upper() in self.valid_guesses

  # generates feedback for current guess
  # static method so you can call this method with Wordle.generate_feedback outside of the class
  # notice how there is no "self" argument here
  @staticmethod
  def generate_feedback(current_guess, current_solution):
    # using an array because strings are immutable in Python
    feedback = ["W"] * WORD_LENGTH
    # create a dictionary mapping letters to num_occurences for current_solution for words with multiple of the same letter
    # e.g. solution is GROWS, guess is GOOSE, the middle O should have C and the first O should be W
    solution_letters = {}
    for i in current_solution:
      if solution_letters.get(i) is None:
        solution_letters[i] = 1
      else:
        solution_letters[i] += 1

    # need to iterate through the entire word for correct letters first before generating misplaced letters, see example above.
    for i in range(WORD_LENGTH):
      if current_guess[i] == current_solution[i]:
        feedback[i] = "C"
        # modify solution_letters as well to prevent the wrong feedback from being generated, see example above.
        solution_letters[current_guess[i]] -= 1

    for i in range(WORD_LENGTH):
      if current_guess[i] != current_solution[i] and current_guess[i] in current_solution and solution_letters[current_guess[i]] > 0:
        feedback[i] = "M"
        solution_letters[current_guess[i]] -= 1

    # feedback is default initialized to W, so no need to update feedback for this

    return "".join(feedback)

  # takes in the current guesses and guess feedback and returns a filtered list of valid_guesses
  def filter_on_feedback(self, current_guesses, guess_feedback):
    # disregard green tiles, handle that separately. If green tiles are used to filter the list of valid_guesses,
    # guesses may not be great. E.g. GREEN returns CCCMW, if you limit the guessing space to words starting with GRE,
    # it's hard to eliminate other letters as there are only 2 more spots left
    # We will let individual algorithms handle what to do with the green tiles

    filtered_guesses = []

    # keeps an array of all letters that shouldn't be in that position
    # this means either letters that are wrong (these letters should be added to all letter positions)
    # or letters that are misplaced for this position
    letter_not_in_position = [set() for i in range(WORD_LENGTH)]
    # helps in cases where a word has multiple of the same letter
    not_wrong_letters = set()

    # need separate for loops because words with multiple of the same letter would have that letter be propogated to all positions
    for guess, feedback in zip(current_guesses, guess_feedback):
      for i in range(WORD_LENGTH):
        if feedback[i] == "M":
          letter_not_in_position[i].add(guess[i])
          not_wrong_letters.add(guess[i])
        elif feedback[i] == "C":
          # read the description above for why we don't do anything else with correct letters
          not_wrong_letters.add(guess[i])
    for guess, feedback in zip(current_guesses, guess_feedback):
      for i in range(WORD_LENGTH):
        if feedback[i] == "W":
          if guess[i] in not_wrong_letters:
            letter_not_in_position[i].add(guess[i])
          else:
            # propagate to all positions, since letter cannot be in word at all
            for j in range(WORD_LENGTH):
              letter_not_in_position[j].add(guess[i])

    # now go through the list of guesses and append to filtered guesses if no letters in word at that position are in letter_not_in_position
    for word in self.valid_guesses:
      valid = True
      for i in range(WORD_LENGTH):
        if word[i] in letter_not_in_position[i]:
          valid = False
          break
      if valid:
        filtered_guesses.append(word)

    return filtered_guesses

  def get_print_stats(self, win: bool, num_guesses: int) -> None:
    if win:
        self.num_wins += 1
    self.num_games += 1
    self.num_guesses += num_guesses

    if self.stats or (not self.stats and self.simulate > 0 and self.num_games == self.simulate):
      print(f"\nCurrent win rate: {self.num_wins} / {self.num_games} = {self.num_wins / self.num_games}")
      print(f"Average number of guesses: {self.num_guesses / self.num_games}\n")

  def print_state(self, current_guesses: list[str], guess_feedback: list[str]) -> None:
    correct = set()
    misplaced = set()
    wrong = set()
    for i in reversed(range(len(current_guesses))):
      for j in range(WORD_LENGTH):
        if guess_feedback[i][j] == "C":
          correct.add(current_guesses[i][j])

    for i in reversed(range(len(current_guesses))):
      for j in range(WORD_LENGTH):
        if guess_feedback[i][j] == "M" and current_guesses[i][j] not in correct:
          misplaced.add(current_guesses[i][j])
        elif guess_feedback[i][j] == "W":
          wrong.add(current_guesses[i][j])

    print(f"\t\t\tGUESSES\t\t\tFEEDBACK")
    for guess_num in range(NUM_GUESSES):
      if guess_num < len(current_guesses):
          print(f"\t\t\t{current_guesses[guess_num]}\t\t\t{guess_feedback[guess_num]}")
      else:
          print("\t\t\t_____\t\t\t_____")
    print(f"Correct: {', '.join(sorted(list(correct)))}")
    print(f"Misplaced: {', '.join(sorted(list(misplaced)))}")
    print(f"Wrong: {', '.join(sorted(list(wrong)))}")
    print(f"Unused: {', '.join(sorted(list(set(string.ascii_uppercase).difference(correct).difference(misplaced).difference(wrong))))}\n")

if __name__ == "__main__":
    game = Wordle()
    game.play()