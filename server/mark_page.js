// labels for the AI agent
let labels = [];

function unmarkPage() {
  // Unmark page logic, this is helper for markPage

  // remove the final labels from DOM
  for (const label of labels) {
  document.body.removeChild(label);
  }
  labels = [];
}

function markPage() {

  // unmark previous annotations
  unmarkPage();

  // retrieves the size and position of the <body> element in the browser's viewport.
  var bodyRect = document.body.getBoundingClientRect();

  // Select all elements on page and convert NodeList to array
  let elements = Array.from(document.querySelectorAll("*"));

  // Process each element
  let items = elements.map((element) => {

    // Get viewport height and width
    let viewportWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    let viewportHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

    // Extract and clean text content by removing leading/trailing space and space longer than 2
    let textualContent = element.textContent.trim().replace(/\s{2,}/g, " ");

    // get an element's tag name and Aria Label
    let elementType = element.tagName.toLowerCase();
    let ariaLabel = element.getAttribute("aria-label") || "";

    // Get the bounding boxes within the element and filter to only see visible ones
    let rects = Array.from(element.getClientRects())
      .filter((box) => {
        let centerX = box.left + box.width / 2;
        let centerY = box.top + box.height / 2;
        let elementAtCenter = document.elementFromPoint(centerX, centerY);

        // this filters rectangles inside an element out s.t. we only have rectangles that are in the center of its box
        return elementAtCenter === element || element.contains(elementAtCenter);
      })
      .map((box) => {
        // maps them to their bounding box coordinates
        return {
          left: Math.max(0, box.left),
          top: Math.max(0, box.top),
          right: Math.min(viewportWidth, box.right),
          bottom: Math.min(viewportHeight, box.bottom),
          width: Math.min(viewportWidth, box.right) - Math.max(0, box.left),
          height: Math.min(viewportHeight, box.bottom) - Math.max(0, box.top)
        };
      });
    
    // calculate the total area of the element based on the sum of its bounding box rectangles
    let totalArea = rects.reduce((acc, rect) => acc + rect.width * rect.height, 0);

    // identify interactive elements for LLM AI agent
    let isInteractive = (
      ["input", "textarea", "select", "button", "a", "iframe", "video"].includes(elementType) ||
      element.onclick !== null ||
      window.getComputedStyle(element).cursor === "pointer"
    );

    // return the final processed element
    return {
      element,
      include: isInteractive,
      area: totalArea,
      rects,
      text: textualContent,
      type: elementType,
      ariaLabel
    };
  });


  // AI agent doesn't need to mark uninteractive or small elements, filter them out
  items = items.filter((item) => item.include && item.area >= 20);

  // filter out elements that are subsets of other elements
  items = items.filter(
    (x) => !items.some((y) => x.element.contains(y.element) && x !== y)
  );

  // helper function to generate random color for coloring bounding box to make AI agent better detect
  function getRandomColor() {
    let color = "#";
    const letters = "0123456789ABCDEF";
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

  // create randomly colored borders for the elements identified
  labels = [];
  items.forEach((item, index) => {
    item.rects.forEach((box) => {

        // create new box
        let newElement = document.createElement("div");
        let borderColor = getRandomColor();

        // Outline styling
        Object.assign(newElement.style, {
            outline: `2px dashed ${borderColor}`,   // draw dashed outline with random borderColor
            position: "fixed",              //fixes position on screen to ignore scrolling
            left: `${box.left}px`,          // sets position based on bb coordinates
            top: `${box.top}px`,
            width: `${box.width}px`,        // Ensures the box matches the size of the original element.
            height: `${box.height}px`,
            pointerEvents: "none",        // 	Prevents the floating box from interfering with user clicks.
            boxSizing: "border-box",      // Ensures the size calculation includes the border.
            zIndex: 2147483647            // max z-index
        });

        // Add floating label at the corner
        let label = document.createElement("span");
        // give it index so AI agent decides the number to interact with basically
        label.textContent = index;

        // label styling
        Object.assign(label.style, {
            position: "absolute",         // Ensures the label is positioned relative to the floating box.
            top: "-19px",                 // 	Moves the label above the box for visibility.
            left: "0px",
            background: borderColor,
            color: "white",
            padding: "2px 4px",           // 	Improves spacing and readability.
            fontSize: "12px",
            borderRadius: "2px"
        });

        // attach label to new element
        newElement.appendChild(label);

        // attach new element to page over old element
        document.body.appendChild(newElement);
        labels.push(newElement);
    });
  });


  // Extract final coordinates for the clickable element for the AI agent
  const coordinates = items.flatMap((item) =>
    item.rects.map(({ left, top, width, height }) => ({
        x: (left + left + width) / 2,
        y: (top + top + height) / 2,
        type: item.type,
        text: item.text,
        ariaLabel: item.ariaLabel,
    }))
  );

  // Based on output of video, LLM needs to decide coordinate to interact
  return coordinates;
}