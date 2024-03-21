const input = document.getElementById("search-textbox");
const searchResults = document.getElementById("search-results");
const xhttp = new XMLHttpRequest();

function search() {
    xhttp.open("GET", window.location.href + "/search?q=" + input.value, true);
    xhttp.send();
}

xhttp.onload = function() {
    if (this.status == 200) {
        searchResults.innerHTML = this.responseText;
    }
    else {
        // If there was an error (most likely due to the search text being empty), no search results are shown.
        searchResults.innerHTML = null;
        console.error(this.statusText);
    }
    
}
