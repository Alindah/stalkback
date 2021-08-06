// Toggles some element on and off
// elClassOrId : the element name or id that you want to toggle
// el : this element that is triggering the function
// parentClass : a parent class that contains the element you want to toggle
// showEl : int - set to 0 to hide element; 1 to display
function toggleElDisplay(elClassOrId, el = null, parentClass = null, showEl = 99) {
    // If an element is entered, look for its closest ancestor of the given class
    // If no parentClass given, take its direct parent
    if (el)
        var parent = (el && parentClass == null) ? el.parentElement : el.closest('.' + parentClass);
    
    // Get the element we want to toggle by either its class name or its ID
    // If an el was given, we are looking for the toggled element within one of el's ancestors
    // Else, we are looking for an id
    var toggledEl = el ? parent.getElementsByClassName(elClassOrId)[0] : document.getElementById(elClassOrId);

    // If we want an element to show or hide instead of toggling between,
    // Set showEl to 0 to hide
    // Set showEl to 1 to display
    // Otherwise it will toggle depending on its current display status
    if (showEl == 0)
        toggledEl.style.display = "none";
    else if (showEl == 1)
        toggledEl.style.display = "block"
    else
        toggledEl.style.display = (toggledEl.style.display == "" || toggledEl.style.display == "none") ? "block" : "none";
}

// Displays comments associated with a post
// el : the element you click on to trigger the display whose ancestor is the post
function displayComments(el) {
    var commentsContainer = el.closest('.post-footer').getElementsByClassName('comments-container')[0];
    commentsContainer.style.display = (commentsContainer.style.display == "" || commentsContainer.style.display == "none") ? "block" : "none";

    if (commentsContainer.style.display == "none")
        toggleElDisplay('reply-container', el, 'comment', 0);
    else
        scrollToEl(el);
}

// Scroll to this element if it exists
// el : the element we want to scroll to
function scrollToEl(el) {
    if (el)
        el.scrollIntoView(alignToTop = true);
}

// Toggle between two colors of an svg, depending on its current color
// el : the svg element whose colors we are toggling
// color1 : one of the colors we want to toggle between, often the original color
// color2 : the other color we want to toggle to
function toggleColor(el, color1, color2) {
    el.style.fill = (el.style.fill == color1 || el.style.fill == "") ? color2 : color1;
}

// Go to page of indicated category upon clicking on it on the dropdown
// dropdown : the dropdown element
function onChangeProfCatDropdown(dropdown) {
    var selected = dropdown.options[dropdown.selectedIndex].text;
    var username = location.href.replace("http://localhost:5000/stalk/", "").split("/", 1)[0];

    if (selected != dropdown.options[0].text)
        redirect = ("http://localhost:5000/stalk/" + username + "/" + selected)
        location.href = redirect;
}

// Toggle the like button
// button : the like button
// https://stackoverflow.com/questions/7803814/prevent-refresh-of-page-when-button-inside-form-clicked
// https://stackoverflow.com/questions/62075431/flask-post-request-form-data-without-refreshing-page
// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
function toggleLike(button) {
    // Get the closest form with this class
    var form = button.closest('.post-info-form');

    // Create a new form based off our form element and send it as a request to the indicated route
    fetch('/handlelike', {
        method: 'POST',
        body: new FormData(form),
    }).then(function() {
        var icons = button.getElementsByTagName('div')
        var likeCountEl = button.parentElement.getElementsByClassName("like-count")[0]
        var likeCount = parseInt(likeCountEl.innerHTML);

        // Toggle between like icons 
        for (let i of icons)
            i.style.display = (i.style.display == "") ? "none" : "";
        
        // Update visual like count
        likeCount = (icons[0].style.display == "none") ? likeCount + 1 : likeCount - 1;
        likeCountEl.innerHTML = likeCount;
    });

    return false;
}

// Deletes a post
// button : the delete button
function deletePost(button) {
    fetch('/handlepostdeletion', {
        method: 'POST',
        body: new FormData(button.closest('.post-info-form')),
    }).then(function() {
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

// Process what happens when the a user is confirmed to stalk or is unstalked
function processStalking() {
    var form = document.getElementById('form-stalk');

    fetch('/process_stalk', {
        method: 'POST',
        body: new FormData(form),
    }).then(function() {
        location.reload();
    });

    return false;
}

// What happens when a user presses the big stalk/unstalk button
// el : the button element
function onClickStalk(el) {
    // If user is stalking this user, unstalk this user
    if (el.value == "unstalk") {
        processStalking();
        return false;
    }

    // If user is not stalking, toggle between "stalk" and the stalk confimation button
    el.value = (el.value == "stalk") ? "confirm stalking below" : "stalk"
    toggleElDisplay('select-category-container');

    return false;
}

// Update categories user is stalking
function updateCategoriesStalking() {
    var form = document.getElementById('form-stalk');
    var update = document.getElementById('update-text-timed');
    
    // Make sure "update" text is reset so animation can replay when updated again
    update.classList.replace('timed-text-visible', 'timed-text-hidden');

    fetch('/process_stalk_categories', {
        method: 'POST',
        body: new FormData(form),
    }).then(function(response) {
        // Show "updated" notification
        update.classList.replace('timed-text-hidden', 'timed-text-visible');
    });

    return false;
}

// Reload an element
// el : element being reloaded
function reloadElement(el) {
    var content = el.innerHTML;
    el.innerHTML = content;
}