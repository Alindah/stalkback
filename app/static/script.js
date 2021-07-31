// Make account deletion confirmation box appear in Settings
function deleteConfirmation() {
    var deleteBox = document.getElementById("delete-confirm");
    deleteBox.style.display = "inline-block";
}

// Toggles menu container on and off
function toggleElDisplay(menuId, el = null) {
    var menu = el ? el.parentElement.getElementsByClassName(menuId)[0] : document.getElementById(menuId);
    menu.style.display = (menu.style.display == "" || menu.style.display == "none") ? "block" : "none";
}

function toggleColor(el, color1, color2) {
    el.style.fill = (el.style.fill == color1 || el.style.fill == "") ? color2 : color1;
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
    form = button.closest('form');
    fetch('/handlelike', {
        method: 'POST',
        body: new FormData(form),
    }).then(function(response) {
        // Toggle between like icons
        var icons = button.getElementsByTagName('div')
        var likeCountEl = button.parentElement.getElementsByClassName("like-count")[0]
        var likeCount = parseInt(likeCountEl.innerHTML);

        for (let i of icons)
            i.style.display = (i.style.display == "") ? "none" : "";
        
        // Update visual like count
        likeCount = (icons[0].style.display == "none") ? likeCount + 1 : likeCount - 1;
        likeCountEl.innerHTML = likeCount;
    });
    return false;
}

function deletePost(button) {
    fetch('/handlepostdeletion', {
        method: 'POST',
        body: new FormData(button.closest('form')),
    }).then(function(response) {
        // Remove post from page
        var postEl = button.closest('.submission');
        postEl.style.display = "none";
    });
    return false;
}

function replyToPost(button) {
    fetch('/reply', {
        method: 'POST',
        body: new FormData(button.closest('form')),
    }).then(function(response) {
        // Display new post
    });
    return false;
}

function loadComments() {
    console.log("loaded comments")
}
