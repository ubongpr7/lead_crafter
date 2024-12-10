function showLoadingAndRedirect(event) {
    event.preventDefault(); // Prevent default click behavior

    // Show the loading block
    document.querySelector(".load").style.display = "block";
    document.querySelector(".contain").style.display = "none";

    // Delay redirection by 2 seconds to show loading state
    setTimeout(function () {
        window.location.href = "voice-subtitle.html"; // Redirect to the target page
    }, 2000); // 2-second delay before redirect
}

document.getElementById('download').addEventListener('click', function (event) {
    event.preventDefault(); // Prevent the default link behavior

    // Create a temporary hidden link element to force file download
    const link = document.createElement('a');
    link.href = this.href; // The href is the file URL to download
    link.setAttribute('download', ''); // Set the download attribute to force download

    // Append link to body, click it, and remove it
    document.body.appendChild(link);
    link.click();
    // document.body.removeChild(link);

    // Redirect after download
    setTimeout(() => {
        window.location.href = '/submitSubtitle'; // Replace with the redirect URL
    }, 1000); // Delay to ensure the download starts before redirecting
});

function upgradePayment(formid){
    document.getElementById(formid).submit();
  }