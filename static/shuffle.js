// Runs entirely in the browser - never talks to Flask or the database.
const list = document.getElementById("names");

document.getElementById("shuffle").addEventListener("click", () => {
  const items = Array.from(list.children);        // grab the list
  for (let i = items.length - 1; i > 0; i--) {    // Fisher-Yates shuffle
    const j = Math.floor(Math.random() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  items.forEach((li) => list.appendChild(li));    // redraw in new order
});
