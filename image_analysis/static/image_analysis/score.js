function endGame () {
    var yesButton = document.getElementById("yesButton");
    var noButton = document.getElementById("noButton");
    yesButton.hidden = true;
    noButton.hidden = true;

    var finalScoreElem = document.getElementById("finalScore");

    finalScoreElem.textContent = "You scored the computer at " + (window.success / (window.success + window.fail)) * 100 + "% correct";

    var homeLink = document.getElementById("home");
    homeLink.hidden = false;
}

function loadNextQuestion () {
    var prev_image = document.getElementById("img" + window.currentImage);
    if (prev_image != null){
        prev_image.hidden = true
    }

    window.currentImage = window.currentImage + 1;

    var current_image = document.getElementById("img" + window.currentImage);
    if (current_image != null){
        current_image.hidden = false
    } else {
        endGame();
    }
}

window.onload = function () {
    window.currentImage = -1;
    window.success = 0;
    window.fail = 0;

    var yesButton = document.getElementById("yesButton");
    var noButton = document.getElementById("noButton");

    yesButton.onclick = function () {
        window.success += 1;
        loadNextQuestion();
    }

    noButton.onclick = function () {
        window.fail += 1;
        loadNextQuestion();
    }
    loadNextQuestion();
}