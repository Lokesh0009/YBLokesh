const texts = ["Full Stack Developer", "Data Scientist", "Data Analyst"];
let currentText = 0;
let currentLetter = 0;
const typingDiv = document.getElementById('typing');
const typingSpeed = 150;
const erasingSpeed = 100;
const delayBetweenTexts = 2000;  // 2 seconds between texts

function typeText() {
    if (currentLetter < texts[currentText].length) {
        typingDiv.textContent += texts[currentText].charAt(currentLetter);
        currentLetter++;
        setTimeout(typeText, typingSpeed);
    } else {
        setTimeout(eraseText, delayBetweenTexts);
    }
}

function eraseText() {
    if (currentLetter > 0) {
        typingDiv.textContent = texts[currentText].substring(0, currentLetter - 1);
        currentLetter--;
        setTimeout(eraseText, erasingSpeed);
    } else {
        currentText = (currentText + 1) % texts.length;
        setTimeout(typeText, typingSpeed);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    setTimeout(typeText, typingSpeed);
});
