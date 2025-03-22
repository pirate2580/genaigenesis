
/*
This is a function that executes an alert when a button on the popup is clicked
*/
async function sayHello() {
  // call chrome api here
  // queries active tabs and pull out current active tab
  let [tab] = await chrome.tabs.query({active : true});
  chrome.scripting.executeScript({
    target: {tabId: tab.id},
    func: () => {
      alert('Hello from my extension');
    }
  });
}

document.getElementById("myButton").addEventListener('click', sayHello);