import pathlib
import random
import string

# https://gist.github.com/cfreshman/d97dbe7004522f7bc52ed2a6e22e2c04
GUESSES_PATH = pathlib.Path(__file__).parent / "valid_guesses.txt"

# https://www.kaggle.com/datasets/bcruise/wordle-valid-words
SOLUTIONS_PATH = pathlib.Path(__file__).parent / "valid_solutions.txt"

WORD_LENGTH = 5
NUM_GUESSES = 6

class Wordle:
    def __init__(self, mode: str) -> None:
        # TODO: read word lists into memory using paths from above

        # remember the mode, currently only cli is valid
        self.mode = mode

        # keep relevant stats
        self.num_games = 0
        self.num_guesses = 0
        self.num_wins = 0

    # TODO: this is the main game loop. Fill in all the logic
    def play(self) -> None:
        if self.mode == "cli":
            while True:
                # READ ME
                # These data structures should be used to generate output using get_print_stats and print_state.
                # If you do not want to use the functions we give you for printing, you are free to choose your
                # own data structures and names
                
                # An array of strings to keep past guesses. Guesses should be kept in the order they came in.
                current_guesses = []
                
                # An array of strings to keep past guess feedback. Has only three possible letters:
                # C for correct, M for misplaced, W for wrong. Each feedback letter corresponds to one letter
                # for the same guess as current_guesses.
                # e.g. guessed WORDS and the solution was BIRDS, guess_feedback[-1] = "WWCCC"
                guess_feedback = []

                # TODO: select solution word randomly (hint: we imported the random module above)
                
                # TODO: Allow the user to guess 6 (NUM_GUESSES) times for the solution word. For each guess:
                # 1. Take the user input and validate it using self.is_valid_guess
                #   Hint: either make all words upper or lower case for consistency.
                # 2. Check if guess is the solution word. If it is, the current game ends.
                # 3. If it isn't, you need to generate feedback for the current guess. Use the explanation for guess_feedback to help.
                #   Hint: strings are immutable in Python, but arrays can be converted easily using "".join(array_name)
                # 4. print the current state using self.print_state, and pass in the proper arguments.
                
                # TODO: After the user guesses the solution word or uses up all 6 guesses, need to check which situation it is.
                # Output a little message and how many guesses it took
                
                # TODO: update stats using get_print_stats by passing it the proper data

                # TODO: prompt user to continue playing the game by taking their choice (yes, quit, no, etc) as input

    # TODO: implement this function with all the checks needed to validate a guess.
    # user_guess should be passed-in from the for loop in self.play
    def is_valid_guess(self, user_guess: str) -> bool:
        pass

    # Do not modify this function. Takes a bool "win" that tells whether or not the user guessed the word
    # and num_guesses as the number of guesses the user made in this current game.
    # This function updates all stats and prints it to the console
    def get_print_stats(self, win: bool, num_guesses: int) -> None:
        if win:
            self.num_wins += 1
        self.num_games += 1
        self.num_guesses += num_guesses
        print(f"\nCurrent win rate: {self.num_wins} / {self.num_games} = {self.num_wins / self.num_games}")
        print(f"Average number of guesses: {self.num_guesses / self.num_games}\n")

    # Do not modify this function. This takes current_guesses and guess_feedback from the self.play function
    # with the same definitions given in that function. 
    # This function finds all the correct, misplaced, wrong and unused letters based on the parameters
    # and prints it all out with your past guessing history for a nice display.
    def print_state(self, current_guesses: [str], guess_feedback: [str]) -> None:
        correct = set()
        misplaced = set()
        wrong = set()
        for i in reversed(range(len(current_guesses))):
            for j in range(WORD_LENGTH):
                if guess_feedback[i][j] == "C":
                    correct.add(current_guesses[i][j])
                elif guess_feedback[i][j] == "M" and current_guesses[i][j] not in correct:
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
    game = Wordle("cli")
    game.play()