// Make account deletion confirmation box appear in Settings
function deleteConfirmation() {
    var deleteBox = document.getElementById("delete-confirm");
    deleteBox.style.display = "inline-block";
}

// Toggles menu container on and off
// Set showEl to 0 to hide; 1 to display
function toggleElDisplay(menuId, el = null, parent_class = null, showEl = 99) {
    if (el)
        var parent = (el && parent_class == null) ? el.parentElement : el.closest('.' + parent_class);
    
    var menu = el ? parent.getElementsByClassName(menuId)[0] : document.getElementById(menuId);

    if (showEl == 0)
        menu.style.display = "none";
    else if (showEl == 1)
        menu.style.display = "block"
    else
        menu.style.display = (menu.style.display == "" || menu.style.display == "none") ? "block" : "none";
}

function displayComments(el) {
    var commentsContainer = el.closest('.post-footer').getElementsByClassName('comments-container')[0];
    commentsContainer.style.display = (commentsContainer.style.display == "" || commentsContainer.style.display == "none") ? "block" : "none";

    if (commentsContainer.style.display == "none")
        toggleElDisplay('reply-container', el, 'comment', 0);
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
    var form = button.closest('.post-info-form');

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
        body: new FormData(button.closest('.post-info-form')),
    }).then(function(response) {
        // Remove post from page
        var postEl = button.closest('.submission');
        postEl.style.display = "none";
    });

    return false;
}

function replyToPost(button) {
    var form = button.closest('.post-info-form');

    fetch('/reply', {
        method: 'POST',
        body: new FormData(form),
    }).then(function(response) {
        // Clear reply text area
        button.closest('.reply-container').getElementsByTagName('textarea')[0].value = "";
        
        // Display new post
    });

    return false;
}

function loadComments() {
    console.log("loaded comments")
}

function processStalking() {
    var form = document.getElementById('form-stalk');
    var button = document.getElementById('button-stalk');
    var catSelectContainer = document.getElementById('select-category-container');
    var manageCategory = document.getElementById('manage-category-container');

    fetch('/process_stalk', {
        method: 'POST',
        body: new FormData(form),
    }).then(function(response) {
        if (button.value == "unstalk") {
            button.value = "stalk";
            button.classList.replace("button-dark-highlight", "button-highlight");

            if (manageCategory)
                manageCategory.style.display = "none";
        }
        else {
            button.value = "unstalk";
            button.classList.replace("button-highlight", "button-dark-highlight");
        }
        catSelectContainer.style.display = "none";
    });

    return false;
}

function onClickStalk(el) {
    if (el.value == "unstalk") {
        processStalking();
        return false;
    }

    el.value = (el.value == "stalk") ? "confirm stalking below" : "stalk"
    toggleElDisplay('select-category-container');

    return false;
}

function updateCategoriesStalking() {
    var form = document.getElementById('form-stalk');
    var update = document.getElementById('update-text-timed');
    update.classList.replace('timed-text-visible', 'timed-text-hidden');

    fetch('/process_stalk_categories', {
        method: 'POST',
        body: new FormData(form),
    }).then(function(response) {
        update.classList.replace('timed-text-hidden', 'timed-text-visible');
    });

    return false;
}

function reloadElement(el) {
    var content = el.innerHTML;
    el.innerHTML = content;
}