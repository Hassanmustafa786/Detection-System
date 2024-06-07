function showUploadMessage() {
    document.getElementById("upload-message").style.display = "block";
}

function validateForm() {
    // Check if username and password fields are empty
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    if (username === "" || password === "") {
        alert("Please enter both username and password.");
        return false; // Prevent form submission
    }
    return true;
}

function scrollToAbout() {
    var aboutSection = document.getElementById('about');
    aboutSection.scrollIntoView({ behavior: 'smooth' });
}