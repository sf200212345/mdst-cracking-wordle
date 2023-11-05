// useful global constants
const WORD_LENGTH = 5;
const NUM_GUESSES = 6;

let current_guesses = [];
let guess_feedback = [];

// current_solution_index is a random number corresponding to an index in the solution list in Flask
let current_solution_index = 0;

reset_board();

function change_mode() {
    // change the text content of the current mode
    let new_mode = document.getElementById("modes").value;
    
    if (new_mode !== document.getElementById("curr-mode").textContent) {
        document.getElementById("curr-mode").textContent = new_mode;
        reset_board();
    }

    if (new_mode === "user") {
        document.getElementById("if-user-mode").className = "";
        document.getElementById("not-user-mode").className = "disabled";
    }
    else {
        document.getElementById("if-user-mode").className = "disabled";
        document.getElementById("not-user-mode").className = "";
    }
}

function insert_letters() {
    for (let row = 0; row < current_guesses.length; ++row) {
        for (let col = 0; col < WORD_LENGTH; ++col) {
            let curr_letter = document.getElementById(row.toString() + col.toString());
            if (guess_feedback[row][col] === "C") {
                curr_letter.className = ("letter correct");
            }
            else if (guess_feedback[row][col] === "M") {
                curr_letter.className = ("letter misplaced");
            }
            else {
                curr_letter.className = ("letter wrong");
            }
            
            curr_letter.textContent = current_guesses[row][col];
        }
    }
}

function submit_user_input() {
    let user_input = document.getElementById("user-input");
    if (current_guesses.length >= NUM_GUESSES) {
        user_input.value = "MAX GUESSES REACHED";
        return;
    }
    if (guess_feedback[guess_feedback.length - 1] === "CCCCC") {
        user_input.value = "CORRECTLY GUESSED";
        return;
    }
    let guess = user_input.value.toUpperCase();
    fetch("/check_guess/?index=" + current_solution_index.toString() + "&guess=" + guess,
          { credentials: "same-origin", method: "POST" })
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
        })
        .then((data) => {
            console.log(data.feedback);
            if (data.feedback === "INVALID") {
                user_input.value = data.feedback;
            }
            else {
                // proper guess, so we can append it and the feedback to current_guesses and guess_feedback
                current_guesses.push(guess);
                guess_feedback.push(data.feedback);
                insert_letters();
                if (guess_feedback[guess_feedback.length - 1] === "CCCCC") {
                    user_input.value = "CORRECTLY GUESSED";
                }
            }
        })
        .catch((error) => console.log(error));
}

function simulate() {
    // simulate using the current mode num_simulate times
    // can only call this function when the mode is not user
    let num_simulate = document.getElementById("num-simulate").value;
    let mode = document.getElementById("curr-mode").textContent;
    for (let i = 0; i < num_simulate; ++i) {
        // start a new game
        reset_board();

        // use while loop, since initial guesses can increase the guess amount
    }
}

function reset_board() {
    if (current_guesses.length >= NUM_GUESSES || guess_feedback[guess_feedback.length - 1] === "CCCCC") {
        // store the data in db and update stats
    }
    current_guesses = [];
    guess_feedback = [];

    // need to query the api for this number
    fetch("/get_solution_index/", { credentials: "same-origin", method: "GET" })
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
        })
        .then((data) => {
            current_solution_index = data.index;
            console.log(current_solution_index);
        })
        .catch((error) => console.log(error));
    // clear the top words section
    document.getElementById("top-words").innerHTML = "Not Available";

    // clear all user input
    document.getElementById("user-input").value = "";

    document.getElementById("modes").value = document.getElementById("curr-mode").textContent;

    // clear colors of all letters in the game board and remove letters
    for (let row = 0; row < NUM_GUESSES; ++row) {
        for (let col = 0; col < WORD_LENGTH; ++col) {
            let curr_letter = document.getElementById(row.toString() + col.toString());
            curr_letter.className = "letter";
            curr_letter.textContent = "";
        }
    }
}