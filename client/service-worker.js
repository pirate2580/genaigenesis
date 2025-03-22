// Using chrome api

// chrome.action.onClicked.addListener(tab => {
//   chrome.scripting.executeScript({
//     target: {tabId: tab.id}, // pass id of the tab you are currently on
//     func: () => {
//       alert("Hello from my extension");
//     }
//   });
// });


// when you click on chrome extension, it fires event listener here and passes instance of tab currently open