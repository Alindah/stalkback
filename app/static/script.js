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

function onChangeProfCatDropdown(dropdown) {
    var selected = dropdown.options[dropdown.selectedIndex].text;
    var username = location.href.replace("http://localhost:5000/stalk/", "").split("/", 1)[0];

    if (selected != dropdown.options[0].text)
        redirect = ("http://localhost:5000/stalk/" + username + "/" + selected)
        location.href = redirect;
}