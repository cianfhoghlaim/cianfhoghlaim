var validWords=[];
var letters = "";
var discoveredWords =[];
var totalScore = 0;
var centerLetter = "";
var cursor = true;
var numFound = 0;
var maxscore = 0;
var dead = '';
setInterval(() => {
  if(cursor) {
    document.getElementById('cursor').style.opacity = 0;
    cursor = false;
  }else {
    document.getElementById('cursor').style.opacity = 1;
    cursor = true;
  }
}, 600);

//makes http request to an api endpoint that returns today's letters/words
function get_valid_words(){

    const url='https://cadhan.com/api/beach/1.0';

    var request = new XMLHttpRequest();
    request.open('POST', url, true);
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    request.onreadystatechange = function(event){
      try {
        if(request.readyState == 3 && request.status == 200){
          var data = JSON.parse(event.target.responseText);
          console.log(data)
          letters = data['letters'].split('');
          validWords = data['possible_words'];
          maxscore = data['maxscore'];
          initialize_letters();
          initialize_score();
        }
      } 
      catch (e){
        console.log('error: '+e.message)
      };
    };
    request.send('teanga=TEANGA');
}

function initialize_score(){
  document.getElementById("maxscore").innerHTML = String(maxscore);
}
//Creates the hexagon grid of 7 letters with middle letter as special color
function initialize_letters(){
    
    var hexgrid = document.getElementById('hexGrid')
    for(var i=0; i<letters.length; i++){
        var thischar = letters[i];
        
        var pElement = document.createElement("P");
        pElement.innerHTML = thischar;
        
        var aElement = document.createElement("A");
        aElement.className = "hexLink";
        aElement.href = "#";
        aElement.appendChild(pElement);
        aElement.addEventListener('click', clickLetter(thischar), false);

        var divElement = document.createElement('DIV');
        divElement.className = "hexIn"; 
        divElement.appendChild(aElement);
        
        var hexElement = document.createElement("LI");
        hexElement.className = "hex";
        hexElement.appendChild(divElement);
        if(i==3){
          aElement.id = "center-letter";
          centerLetter = letters[i];
        }
        hexgrid.appendChild(hexElement);
    }
}

Array.prototype.shuffle = function() {
  let input = this;
  for (let i = input.length-1; i >=0; i--) {
    let randomIndex = Math.floor(Math.random()*(i+1)); 
    let itemAtIndex = input[randomIndex]; 
    input[randomIndex] = input[i]; 
    input[i] = itemAtIndex;
  }
  return input;
}

function shuffleLetters() {
    letters.shuffle()
    //get center letter back to letter[3]
    var centerIndex = letters.indexOf(centerLetter);
    if(letters[3] != centerLetter) {
        var temp = letters[3];
        letters[3] = centerLetter;
        letters[centerIndex] = temp;
    }
    var hexgrid = document.getElementById('hexGrid')
    while (hexgrid.firstChild) {
      hexgrid.removeChild(hexgrid.firstChild);
    }
    initialize_letters()

    /*
    //fill in shuffled letters into hex grid 
    for(var i=0; i<letters.length; i++) {
        var char = letters[i];
        var hexLetterElement = document.getElementsByClassName("hexLink");
        hexLetterElement[i].removeChild(hexLetterElement[i].firstChild);

        var pElement = document.createElement("P");
        pElement.innerHTML = char;
        hexLetterElement[i].appendChild(pElement); 
    }*/
}

//Validate whether letter typed into input box was from one of 7 available letters
// document.getElementById("testword").addEventListener("keydown", function(event){
//     if(!letters.includes(event.key.toUpperCase())){
//         alert('Invalid Letter Typed')
//         event.preventDefault();
//     }
//   }
//   )

//When letter is clicked add it to input box
var clickLetter = function(letter){
  return function curried_func(e){
    var tryword = document.getElementById("testword");
    dead = '';
    tryword.innerHTML = tryword.innerHTML + letter.toLowerCase();
  }
}

//Deletes the last letter of the string in the textbox
function deleteLetter(){
  var tryword = document.getElementById("testword");
  var trywordTrimmed = tryword.innerHTML.substring(0, tryword.innerHTML.length-1);
  tryword.innerHTML = trywordTrimmed
  if(!checkIncorrectLetters(trywordTrimmed)) {
      tryword.style.color = 'black';
  }
  dead = '';
}

function wrongInput(selector){
  $(selector).fadeIn(1000);
  $(selector).fadeOut(500);
  $("#cursor").hide();
  $( "#testword" ).effect("shake", {times:2.5}, 450, function(){
      clearInput();
      $("#cursor").show();
    } );

}

function rightInput(selector){
  $(selector).fadeIn(1500).delay(500).fadeOut(1500);
  
  clearInput();
}

function clearInput(){
  $("#testword").empty();
}

function showPoints(pts){
  $(".points").html("+" + pts);

}
//check if the word is valid and clear the input box
//word must be at least 4 letters
//word must contain center letter
//word can't already be found 
function submitWord(){
  var tryword = document.getElementById('testword');
  var centerLetter = document.getElementById('center-letter').firstChild.innerHTML;

  let score = 0;
  dead = '';
  var isPangram = false;
  var showScore = document.getElementById("totalScore");

  if(tryword.innerHTML.length < 4){ 
    wrongInput("#too-short");
  }else if(discoveredWords.includes(tryword.innerHTML.toLowerCase())){
    wrongInput("#already-found");
  }else if(!tryword.innerHTML.toLowerCase().includes(centerLetter.toLowerCase())){
    wrongInput("#miss-center");

  }else if(validWords.includes(tryword.innerHTML.toLowerCase())){

    var isPangram = checkPangram(tryword.innerHTML);
    score = calculateWordScore(tryword.innerHTML, isPangram);
    addToTotalScore(score);
    console.log("totalscore: " + totalScore);
    
    showDiscoveredWord(tryword.innerHTML);
    numFound++;
    document.getElementById("numfound").innerHTML = numFound;
    document.getElementById("score").innerHTML = totalScore;

    var l = tryword.innerHTML.length;
    if(isPangram){
      rightInput("#pangram");
      showPoints(score);
    }else if(l < 5){
      rightInput("#good");
      showPoints(score);
    }else if(l<7){
      rightInput("#great");
      showPoints(score);
    }else{
      rightInput("#amazing");
      showPoints(score);
    }

  }else{
    wrongInput("#invalid-word");
  }
}

//if word was valid, display it 
//if all words are found end game.
function showDiscoveredWord(input){
    
    var discText = document.getElementById("discoveredText");
    discoveredWords.push(input.toLowerCase());
    discoveredWords.sort() 
    while(discText.firstChild){
      discText.removeChild(discText.firstChild);
    }

    var numFound = discoveredWords.length; 
    var numCol = Math.ceil(numFound/6);
    var w = 0; 
    for(var c=0; c<numCol; c++){
      var list = document.createElement("UL");
      list.id= "discovered-words"+c;
      list.style.cssText = "padding:5px 10px; font-weight:100; ";
      discText.appendChild(list);
      var n = 6; 
      if(c == numCol-1){
        if(numFound%6 ==0){
          if(numFound==0){
            n = 0
          }
          else{
            n=6;
          }
        }else{
        n = numFound%6;}
      }
      for(var i=0; i<n; i++){
        var listword = document.createElement("LI");
        var pword = document.createElement("P");
        pword.innerHTML = discoveredWords[w]; 
        listword.appendChild(pword);
        list.appendChild(listword);
        w++;
      }
    }
    if (numFound == validWords.length){
      alert("CONGRATS");
    }
}

//adds input "score" to the total score of user
function addToTotalScore(score) {
  totalScore += score;
}

//calculates the score of input "input" and also adjusts if "input" is a pangram 
function calculateWordScore(input, isPangram) {
  
  let len = input.length;
  let returnScore = 1; 
  if(len > 4) {
    if(isPangram) {
      returnScore = len + 7;
      
    }else{
      returnScore = len;
    }
  }
  console.log('score ' + returnScore)
  return returnScore;
}

//checks if "input" word is a pangram
function checkPangram(input) {
  
  var i;
  var containsCount = 0;
  var containsAllLetters = false;
  for(i = 0; i < 7; i++) {
    if(input.includes(letters[i])) {
      containsCount++;
    }
  }
  if(containsCount == 7) {
    containsAllLetters = true;
  }
  console.log("isPangram?: " + containsAllLetters);
  return containsAllLetters;
  
 return false;
}

function checkIncorrectLetters(input) {
  var i;
  var badLetterCount = 0;
  for(i = 0; i < input.length; i++) {
    if(!letters.includes(input[i])) {
      badLetterCount++;
    }
  }
  if(badLetterCount > 0) {
    return true;
  }
  return false;
}

//takes keyboard event from user and determines what should be done
function input_from_keyboard(ev) {
  var tryword = document.getElementById("testword");
  var extraChars = 'àèìòùÀÈÌÒÙáéíóúÁÉÍÓÚ';

  if(ev.keyCode == 13) {
    submitWord();
  }

  else if(ev.keyCode == 8) {
    deleteLetter();
  }

  else if (ev.key == 'Dead') {
    dead = ev.code;  // e.g. Backquote or Quote
  }

  else if (ev.key == 'Shift' || ev.key=='CapsLock') {
    // don't change dead status
  }

  else if((ev.keyCode >= 97 && ev.keyCode <= 122) ||
     (ev.keyCode >= 65 && ev.keyCode <= 90)  ||
     extraChars.includes(ev.key))  {
    var c = ev.key.toLowerCase();
    if (dead == 'Backquote') {
      if (c=='a') { c='à'; }
      else if (c=='e') { c='è'; }
      else if (c=='i') { c='ì'; }
      else if (c=='o') { c='ò'; }
      else if (c=='u') { c='ù'; }
    }
    else if (dead == 'KeyE') {
      if (c=='a') { c='á'; }
      else if (c=='e') { c='é'; }
      else if (c=='i') { c='í'; }
      else if (c=='o') { c='ó'; }
      else if (c=='u') { c='ú'; }
    }
    dead = '';
    tryword.innerHTML = tryword.innerHTML+ c;
    if(checkIncorrectLetters(tryword.innerHTML)) {
      tryword.style.color = 'grey';
    }
  }
  else {  // everything else; punctuation, numbers, etc.
    dead = '';
  }
}
