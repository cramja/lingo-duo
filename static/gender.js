var HttpClient = function() {
    this.get = function(aUrl, aCallback) {
        var anHttpRequest = new XMLHttpRequest();
        anHttpRequest.onreadystatechange = function() {
            if (anHttpRequest.readyState == 4 && anHttpRequest.status == 200)
                aCallback(anHttpRequest.responseText);
        }

        anHttpRequest.open("GET", aUrl, true);
        anHttpRequest.send(null);
    }
}

var jsonUrl = document.getElementById("callback-url").textContent;
var http = new HttpClient();

function Word(word, gender) {
    this.word = word;
    this.gender = gender;
    this.correct = 0;
    this.incorrect = 0;

    this.guessGender = function(guess) {
        let correct = (guess == this.gender);
        this.correct += correct ? 1 : 0;
        this.incorrect += correct ? 0 : 1;
        return correct ? "Correct!" : "Incorrect: " + this.word + " is " + this.gender;
    }

    this.isComplete = function() {
        if (this.correct > 3 * this.incorrect) {
            return true;
        }
        return false;
    }
}

function processWords(words) {
    let processed = []
    words.forEach((word) => {
        processed.push(new Word(word["word"], word["gender"]));
    });

    return processed;
}

function Game(words) {
    this.rawWords = words;
    this.state = {
        "current": 0,
        "message": "",
        "remaining": processWords(words),
        "completed": []
    };

    this.setup = function() {
        // attach button listeners
        this.updateVis();
        document.getElementById("btn-male").addEventListener("click", () => this.onSelect("Masculine"));
        document.getElementById("btn-female").addEventListener("click", () => this.onSelect("Feminine"));
        document.getElementById("btn-neuter").addEventListener("click", () => this.onSelect("Neuter"));
    }

    this.onSelect = function(gender) {
        let idx = this.state['current'];
        let remaining = this.state['remaining'];
        let completed = this.state["completed"];
        let word = remaining[idx]
        this.state.message = word.guessGender(gender);

        if (word.isComplete()) {
            completed.push(remaining.splice(idx,1)[0]);
        }

        if (remaining.length == 0) {
            alert("congrats!");
            return;
        }

        this.state.current = Math.floor(Math.random() * remaining.length);
        this.updateVis();
    }

    this.updateVis = function() {
        let word = this.state["remaining"][this.state["current"]];
        document.getElementById("word").textContent = word.word;
        document.getElementById("translation").textContent = this.state.message;
    }

}

http.get(jsonUrl, function(response) {
    var game = new Game(JSON.parse(response));
    game.setup();
});
