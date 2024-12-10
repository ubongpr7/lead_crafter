// function delayedRedirect() {
//     // Sleep for 60 seconds (60,000 milliseconds)
//     setTimeout(function() {
//         // Redirect after the delay
//         window.location.href = '/create-lead';  // Replace with the desired URL
//     }, 3000);  // 60,000 milliseconds = 60 seconds
// }
// delayedRedirect();


function delayedRedirect() {
    const progressElement = document.getElementById('progress-count');
    let progress = 0;

    // Update progress every 30ms (to complete in 3 seconds)
    const interval = setInterval(function() {
        progress += 1;
        progressElement.textContent = progress + '%';

        if (progress >= 100) {
            clearInterval(interval); // Stop the interval when progress reaches 100%
        }
    }, 30); // 3000ms / 100 steps = 30ms per step

    // Redirect after the delay
    setTimeout(function() {
        progressElement.textContent = '100%';
        // window.location.href = '/create-lead';  // Replace with the desired URL
    }, 3000);  // Redirect after 3 seconds
    setTimeout(function() {
        // progressElement.textContent = '100%';
        window.location.href = '/create-lead';  // Replace with the desired URL
    }, 3500);  // Redirect
}

delayedRedirect();
