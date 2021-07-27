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

// Go to page of indicated category upon clicking on it on the dropdown
function onChangeProfCatDropdown(dropdown) {
    var selected = dropdown.options[dropdown.selectedIndex].text;
    var username = location.href.replace("http://localhost:5000/stalk/", "").split("/", 1)[0];

    if (selected != dropdown.options[0].text)
        redirect = ("http://localhost:5000/stalk/" + username + "/" + selected)
        location.href = redirect;
}

// https://stackoverflow.com/questions/7803814/prevent-refresh-of-page-when-button-inside-form-clicked
// https://stackoverflow.com/questions/62075431/flask-post-request-form-data-without-refreshing-page
// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
function toggleLike(button) {
    fetch('/handlelike', {
        method: 'POST',
        body: new FormData(button.parentElement),
    }).then(function(response) {
        // Toggle between like icons
        icons = button.getElementsByTagName('div')

        for (let i of icons)
            i.style.display = (i.style.display == "") ? "none" : "";
    });
    return false;
}
