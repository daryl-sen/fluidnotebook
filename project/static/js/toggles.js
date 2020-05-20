function toggleMenu()
{
    var curtain = document.getElementById('curtain');
    var menu = document.getElementById('mobile');

    if (curtain.style.display === "none")
    {
      menu.style.width = "100%";
      curtain.style.display = "block";
    }
    else if(curtain.style.display === "block")
    {
      menu.style.width = "0";
      curtain.style.display = "none";
    }
}

function toggleElement(eID)
{
    var elementBlock = document.getElementById(eID);
    if (elementBlock.style.display === "block")
    {
        elementBlock.style.display = "none";
    }
    else if (elementBlock.style.display = "none")
    {
        elementBlock.style.display = "block";
    }
}







function hideKeywords() {
    // hide keywords
    var keywordsList = document.getElementsByTagName("u");
    for (var i = 0; i < keywordsList.length; i++) {
        keywordsList[i].style.backgroundColor = "#393939";
        keywordsList[i].style.color = "#393939";
    }
    // change toggle function
    var toggleKeywordsButton = document.getElementById("toggleKeywordsButton");
    toggleKeywordsButton.setAttribute( "onClick", "showKeywords()" );
}

function showKeywords() {
    // show keywords
    var keywordsList = document.getElementsByTagName("u");
    for (var i = 0; i < keywordsList.length; i++) {
        keywordsList[i].style.backgroundColor = "inherit";
        keywordsList[i].style.color = "inherit";
    }
    // change toggle function
    var toggleKeywordsButton = document.getElementById("toggleKeywordsButton");
    toggleKeywordsButton.setAttribute( "onClick", "hideKeywords()" );
}

// keypress event listener for shortcuts

var keymap = {};
onkeydown = onkeyup = function(e){
    e = e || event; // to deal with IE
    keymap[e.keyCode] = e.type == 'keydown';
    if ((keymap[75]))
    {
        document.getElementById("toggleKeywordsButton").click();
    }
}
