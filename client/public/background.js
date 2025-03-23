// background.js

chrome.action.onClicked.addListener(() => {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then((stream) => {
      console.log("Microphone access granted:", stream);
    })
    .catch((error) => {
      console.error("Error obtaining user media (audio):", error);
    });
});