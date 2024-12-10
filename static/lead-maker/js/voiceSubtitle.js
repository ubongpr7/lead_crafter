// Font size slider functionality
const sliderThumb = document.getElementById('sliderThumb');
const sliderFilled = document.getElementById('slider-filled');
const valueLabel = document.getElementById('valueLabel');
const textAreaFont = document.getElementById('text-area-font');
const textArea = document.getElementById("text-area");

let isDragging = false;
const minFontSize = 12; // minimum font size
const maxFontSize = 48; // maximum font size
let currentSize = minFontSize;

sliderThumb.addEventListener('mousedown', () => {
  isDragging = true;
});

document.addEventListener('mouseup', () => {
  isDragging = false;
});

document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
  
    const rect = sliderThumb.parentElement.getBoundingClientRect();
    const offsetX = e.clientX - rect.left;
  
    // Calculate new font size based on mouse position
    currentSize = Math.round((offsetX / rect.width) * (maxFontSize - minFontSize) + minFontSize);
    currentSize = Math.min(maxFontSize, Math.max(minFontSize, currentSize));
  
    // Update the slider thumb and filled area
    const percent = (currentSize - minFontSize) / (maxFontSize - minFontSize);
    sliderThumb.style.left = `${percent * 100}%`;
    sliderFilled.style.width = `${percent * 100}%`;
  
    // Update font size
    textAreaFont.style.fontSize = `${currentSize*0.4}px`;
    // textArea.style.maxWidth = `400px`;

   

    valueLabel.textContent = currentSize;
  
    // Update the hidden input with the current font size
    fontSize.value = currentSize; // Update the hidden input
  });

// Color pickers
// const textColorInput = document.getElementById('text-color');
// const bgColorInput = document.getElementById('bg-color');
// const textCode = document.getElementById('text-code');
// const bgCode = document.getElementById('bg-code');

// textColorInput.addEventListener('input', (event) => {
//   const color = event.target.value;
//   textCode.textContent = color;
//   textAreaFont.style.color = color;
// });

// bgColorInput.addEventListener('input', (event) => {
//   const color = event.target.value;
//   const bgPicker = document.getElementById("bg-picker");
//   bgPicker.style.backgroundColor=color;
//   bgCode.textContent = color;
//   const previewArea = document.getElementById('text-area');
//   previewArea.style.backgroundColor = color;
// });

const bgColorInput = document.getElementById("bg-color");
const textColorInput = document.getElementById("text-color");
const fontSizeInput = document.getElementById("font-size");

let textAreaFontt = document.getElementById("text-area-font");
const fontSizeValue = document.getElementById("font-size-value");
const bgPicker = document.getElementById("bg-picker");
const textPicker = document.getElementById("text-picker");
const bgCode = document.getElementById("bg-code");
const textCode = document.getElementById("text-code");
// const fontSizeInputValue = document.getElementById("font-size").value();
// fontSizeValue.textContent = fontSizeInputValue + "px";

bgColorInput?.addEventListener("input", function () {
  textArea.style.backgroundColor = bgColorInput.value;
  bgPicker.style.backgroundColor = bgColorInput.value;
  bgCode.textContent = bgColorInput.value;
});

textColorInput?.addEventListener("input", function () {
  textAreaFontt.style.color = textColorInput.value;
  textPicker.style.backgroundColor = textColorInput.value;
  textCode.textContent = textColorInput.value;
});

// File upload functionality
const fileInputs = document.querySelectorAll('.br-input');
const noFileTexts = document.querySelectorAll('.browse-field p');

fileInputs.forEach((input, index) => {
  input.addEventListener('change', (event) => {
    const fileName = event.target.files.length > 0 ? event.target.files[0].name : 'No file chosen';
    console.log(fileName);
    // noFileTexts[index].textContent = fileName; // Update the text to show the selected file name
    noFileTexts[index].textContent =`${fileName.slice(0,15)}`;
  });
});





