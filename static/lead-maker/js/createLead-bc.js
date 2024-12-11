function showLoadingAndRedirect(event) {
    event.preventDefault(); // Prevent default click behavior

    // Show the loading block
    // document.querySelector('.load').style.display = 'block';
    // document.querySelector('.contain').style.display = 'none';

    // // Optional: Add some dots animation
    // let dots = 0;
    // const loadingText = document.querySelector('.lead-title .dots');
    // const interval = setInterval(() => {
    //     dots = (dots + 1) % 4; // Cycle through 0 to 3
    //     loadingText.textContent = '.'.repeat(dots); // Update dots
    // }, 500);
    // Submit the form programmatically after a short delay
    const form = document.querySelector('.lead-form'); // Select the form
    form.submit(); 
    // setTimeout(() => {
    //   clearInterval(interval);
    //   const form = document.querySelector('.lead-form'); // Select the form
    //   form.submit(); // Submit the form
    // }, 3000); // Adjust delay if needed
  }

document.addEventListener('DOMContentLoaded', function () {
    updateSlideNumbers();
});
function updateSlideNumbers() {
    const rows = document.querySelectorAll('#leadsTable tbody tr');
    rows.forEach((row, index) => {
        row.cells[0].innerText = `Slide ${index + 1}`;
    });
}
let currentNumber = document.getElementById('no_of_slides').value


function deleteSlide(btn) {
    var row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
    // updateSlideNumbers();
    currentNumber++
    document.getElementById('no_of_slides').value=currentNumber
}

const form = document.querySelector('.lead-form');
console.log(form);
form.addEventListener('submit', showLoadingAndRedirect);

