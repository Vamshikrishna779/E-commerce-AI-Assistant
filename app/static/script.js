window.addEventListener("DOMContentLoaded", () => {
  const answerBox = document.getElementById("answer-box");
  if (!answerBox) return;

  const text = answerBox.textContent;
  answerBox.textContent = "";

  let i = 0;
  function typeChar() {
    if (i < text.length) {
      answerBox.textContent += text.charAt(i);
      i++;
      setTimeout(typeChar, 20);
    }
  }

  typeChar();
});
