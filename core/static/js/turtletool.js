// script.js
var corpArray = {
    "alliance" : {
        "Verge of Collapse" : "99001968",
        "Sleeper Social Club" : "99000767",
        "Odin's Call" : "99004013",
        "Hole Control" : "99004344",
        "Scary Wormhole People" : "99003144",
        "Of Sound Mind" : "99000739",
        "Low-Class" : "99004368",
        "It Must Be Jelly Cause Jam Don't Shake" : "99004643",
        "Ixtab." : "99002675",
        "404 Hole Not Found" : "99005887",
        "Unsettled." : "99004242",
        "Half Massed" : "99005023",
        "DURA LEXX" : "99003700",
        "Exit Strategy.." : "99004364",
        "The Last Chancers" : "1475695446",
        "Friendly Probes": "99006112"
    },
    "corporation" : {
        "Hard Knocks Inc." : "98040755",
        "Lazerhawks" : "98290394",
        "Isogen 5" : "98297019",
        "Useless Idea" : "98067874",
        "Catastrophic Overview Failure" : "98319972",
        "Spectraliz IIZ" : "98100175",
        "No Vacancies" : "98323701",
        "fiftyninepee" : "98262249"
        
    }
    
}

var shipArray = {
    "Legion" : "29986",
    "Tengu" : "29984",
    "Proteus" : "29988",
    "Loki" : "29990",
    "Bhaalgorn" : "17920",
    "Vindicator": "17740",

    "Sleipnir": "22444",
    "Claymore": "22468",
    "Absolution": "22448",
    "Damnation": "22474",

    "Guardian": "11987",
    "Basilisk": "11985",
    "Gila": "17715",
    "Curse": "20125",
    "Huginn": "11961",

    "Confessor": "34317",
    "Jackdaw": "34828",
    "Hecate": "35683",
    "Svipul": "34562",
    "Pontifex": "37481",
    "Stork": "37482",
    "Magus": "37483",
    "Bifrost": "37480",
    "Deacon": "37457",
    "Kirin": "37458",
    "Thalia": "37459",
    "Scalpel": "37460",


    "Archon" : "23757",
    "Chimera" : "23915",
    "Thanatos" : "23911",
    "Nidhoggur" : "24483"
}

var select = document.getElementById("nameSelect");
var shipSelect = document.getElementById("shipSelect");
var checkbox = document.getElementById("typeCheckbox");
var link = document.getElementById("link");


var shipSize = 0;

for (var type in corpArray){
    for (var name in corpArray[type]){
        var option = document.createElement("option");
        option.text = name;
        select.add(option);
    }
}

for (var ship in shipArray){
    var option = document.createElement("option");
    option.text = ship;
    shipSelect.add(option);
    shipSize++;
}
shipSelect.size = shipSize;

function onNewSelect(){
    var corpType;
    var corpID;
    var shipText = "";
    
    for (var type in corpArray){
        for (var name in corpArray[type]){
            if (name == select[select.selectedIndex].text){
                corpType = type;
                corpID = corpArray[type][name];
            }
        }
    }
    
    for (var i = 0; i < shipSelect.length; i++){
        if (shipSelect[i].selected){
            shipText = shipText + shipArray[shipSelect[i].text] + ",";
        }
    }
    if (shipText.length > 0){   
        shipText = "/ship/" + shipText.substr(0,shipText.length-1);
    }
    
    if (typeof corpID != 'undefined'){
        var newHref = "https://zkillboard.com/" + corpType + "/" + corpID + shipText + "/losses/";
        if (!checkbox.checked){
            newHref = newHref + "w-space/";
        }
        link.href = newHref;
        link.text = "Click me!";
        link.className = "btn btn-success"
    } else {
        link.href = "";
        link.text = "Pick an alliance...";
        link.className = "btn btn-success disabled"
    }
}

select.options[0].text = "Pick an alliance/corporation";
