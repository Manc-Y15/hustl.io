


var trade_with = [
    "confidence", 
    "passion", 
    "no idea what you're doing",
    "others",
    "friends",
    "competition"];

var counter = 0;
var elem = $("#trade-with");
setInterval(change, 3500);
function change() {
    elem.fadeOut(function(){
        elem.html(trade_with[counter]);
        counter++;
        if(counter >= trade_with.length) { counter = 0; }
        elem.fadeIn();
    });
}