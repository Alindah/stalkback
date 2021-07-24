// Make account deletion confirmation box appear in Settings
function deleteConfirmation() {
    var deleteBox = document.getElementById("delete-confirm");
    deleteBox.style.display = "inline-block";
}

// Toggles menu container on and off
function toggleMenu() {
    var menu = document.getElementById("menu-container");

    if (menu.style.display == "" || menu.style.display == "none")
        menu.style.display = "block";
    else
        menu.style.display = "none";
}