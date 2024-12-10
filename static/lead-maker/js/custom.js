// Font size slider functionality
const sliderThumb = document.getElementById('sliderThumb');
const sliderFilled = document.getElementById('slider-filled');
const valueLabel = document.getElementById('valueLabel');
const textAreaFont = document.getElementById('text-area-font');

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
  textAreaFont.style.fontSize = `${currentSize}px`;
  valueLabel.textContent = currentSize;
});

// Color pickers
const textColorInput = document.getElementById('text-color');
const bgColorInput = document.getElementById('bg-color');
const textCode = document.getElementById('text-code');
const bgCode = document.getElementById('bg-code');

textColorInput.addEventListener('input', (event) => {
  const color = event.target.value;
  textCode.textContent = color;
  textAreaFont.style.color = color;
});

bgColorInput.addEventListener('input', (event) => {
  const color = event.target.value;
  bgCode.textContent = color;
  const previewArea = document.getElementById('text-area');
  previewArea.style.backgroundColor = color;
});

// Loading and redirect function
function showLoadingAndRedirect(event) {
  event.preventDefault(); // Prevent default form submission

  const loadingWrapper = document.getElementById('loadingWrapper');
  loadingWrapper.style.display = 'flex';

  let dotCount = 0;
  const loadingDots = document.querySelector('.dots');
  const interval = setInterval(() => {
    dotCount++;
    loadingDots.textContent += '.';
    if (dotCount > 3) {
      loadingDots.textContent = '';
      dotCount = 0;
    }
  }, 500);

  setTimeout(() => {
    clearInterval(interval);
    window.location.href = 'create-lead.html'; // Redirect to the target page
  }, 3000); // Adjust delay if needed
}

function redirectToPage(url) {
  // Redirect to the specific URL passed as an argument
  window.location.href = url;
}
