// function delayedRedirect() {
//     // Sleep for 60 seconds (60,000 milliseconds)
//     setTimeout(function() {
//         // Redirect after the delay
//         window.location.href = '/music';  // Replace with the desired URL
//     }, 120000);  // 60,000 milliseconds = 60 seconds
// }
// // delayedRedirect();

// function checkVideoStatus() {
//     fetch("/checkEditing")
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === true) {
//                 // Redirect to success page when the video is processed
//                 window.location.href = "/music";
//             } else {
//                 // Retry after a delay
//                 setTimeout(checkVideoStatus, 20000);
//             }
//         });
// }
// checkVideoStatus();



// function checkVideoStatus() {
//     const progressElement = document.getElementById("progress-count"); // Element to show progress
//     let progress = 0;

//     function updateProgress() {
//         // Increment progress (simulate it reaching 100%)
//         progress = Math.min(progress + 10, 100); // Increase by 10 each check, max 100
//         progressElement.textContent = `${progress}%`;

//         if (progress >= 100) {
//             progressElement.textContent = "100%";
//         }
//     }

//     fetch("/checkEditing")
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === true) {
//                 // Set progress to 100 and redirect
//                 progressElement.textContent = "100%";
//                 window.location.href = "/music";
//             } else {
//                 // Update progress and retry after a delay
//                 updateProgress();
//                 setTimeout(checkVideoStatus, 2000); // Retry every 2 seconds
//             }
//         })
//         .catch(error => {
//             console.error("Error checking video status:", error);
//         });
// }

// // Start the process
// checkVideoStatus();


// function checkVideoStatus() {
//     const progressElement = document.getElementById("progress-count"); // Element to show progress
//     let progress = 0;

//     // Function to update the progress bar
//     function updateProgress() {
//         // Increment progress (simulate it reaching 100%)
//         if (progress < 96) {
//             progress = Math.min(progress + 5, 100); // Increase by 10 each check, max 100
//             progressElement.textContent = `${progress}%`;
//         }
//     }

//     // This function will check the video status from the API
//     function fetchStatus() {
//         fetch("/checkEditing")
//             .then(response => response.json())
//             .then(data => {
//                 console.log(data)
//                 if (data.status === true) {
//                     // If the status is true, set progress to 100 and redirect
//                     clearInterval(progressInterval); // Stop the progress update
//                     progressElement.textContent = "100%";
//                     setTimeout(()=>{
//                         window.location.href = "/music"; // Redirect to the download page
//                     },1000)
//                 }
//             })
//             .catch(error => {
//                 console.error("Error checking video status:", error);
//             });
//     }

//     // Update the progress every 2 seconds
//     const progressInterval = setInterval(updateProgress, 3000);

//     // Check the status every 5 seconds
//     const statusInterval = setInterval(fetchStatus, 5000);
// }

// // Start the process
// checkVideoStatus();


function checkVideoStatus() {
    const progressElement = document.getElementById("progress-count"); // Element to show progress
    let progress = 0;

    // Function to update the progress bar
    function updateProgress() {
        // Increment progress but stop at 90% unless status is true
        if (progress < 96) {
            progress = Math.min(progress + 5, 95); // Increase by 5 each check, max 90%
            console.log('from update progress function',progress)
            progressElement.textContent = `${progress}%`;
        }
    }

    // This function will check the video status from the API
    function fetchStatus() {
        fetch("/checkEditing")
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === true) {
                    // If the status is true, set progress to 100 and redirect
                    clearInterval(progressInterval); // Stop the progress update
                    clearInterval(statusInterval); // Stop the status checks
                    progress = 100;
                    progressElement.textContent = "100%";
                    setTimeout(() => {
                        window.location.href = "/music"; // Redirect to the download page
                    }, 500);
                }
            })
            .catch(error => {
                console.error("Error checking video status:", error);
            });
    }

    // Update the progress every 3 seconds
    const progressInterval = setInterval(updateProgress, 6000);

    // Check the status every 5 seconds
    const statusInterval = setInterval(fetchStatus, 7000);
}

// Start the process
checkVideoStatus();
