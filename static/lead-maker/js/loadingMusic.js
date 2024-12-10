
// function checkVideoStatus() {
//     fetch("/checkEditing")
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === true) {
//                 // Redirect to success page when the video is processed
//                 window.location.href = "/download";
//             } else {
//                 // Retry after a delay
//                 setTimeout(checkVideoStatus, 20000);
//             }
//         });
// }
// checkVideoStatus();



function checkVideoStatus() {
    const progressElement = document.getElementById("progress-count"); // Element to show progress
    let progress = 0;

    // Function to update the progress bar
    function updateProgress() {
        // Increment progress (simulate it reaching 100%)
        if (progress < 96) {
            progress = Math.min(progress + 5, 95); // Increase by 10 each check, max 100
            progressElement.textContent = `${progress}%`;
        }
    }

    // This function will check the video status from the API
    function fetchStatus() {
        fetch("/checkEditing")
            .then(response => response.json())
            .then(data => {
                console.log(data)
                if (data.status === true) {
                    // If the status is true, set progress to 100 and redirect
                    clearInterval(progressInterval); // Stop the progress update
                    clearInterval(statusInterval); 
                    progressElement.textContent = "100%";
                   

                    setTimeout(()=>{
                        window.location.href = "/download";  // Redirect to the download page
                    },500)
                }
            })
            .catch(error => {
                console.error("Error checking video status:", error);
            });
    }

    // Update the progress every 2 seconds
    const progressInterval = setInterval(updateProgress, 6000);

    // Check the status every 5 seconds
    const statusInterval = setInterval(fetchStatus, 7000);
}

// Start the process
checkVideoStatus();
