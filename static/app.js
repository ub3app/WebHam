document.addEventListener("DOMContentLoaded", function(event) {
    fillData();

    document.getElementById("cwbtn").onclick = clickcw;
    document.getElementById("freqbtn").onclick = clickfreq;
    document.getElementById("txbtn").onclick = clicktx;
    document.getElementById("rxbtn").onclick = clickrx;

    var elms = document.querySelectorAll("[id='modebtn']");
    for(var i = 0; i < elms.length; i++)
        elms[i].onclick = clickmode;

});

function sendData(url) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            getData(this);
        }
    };
    xhttp.open("GET", url, false);
    xhttp.send();
}

function getData(data) {
    const json = JSON.parse(data.responseText);
    console.log(json);
    if (json.hasOwnProperty('freq')) {
        document.getElementById("freq").value = json.freq;
    }
    if (json.hasOwnProperty('mode')) {
        document.getElementById("Mode").value = json.mode;
    }
    if (json.hasOwnProperty('ptt')) {
        if (json.ptt == 0) {
            document.getElementById("txbtn").classList.remove("btn-danger");
            document.getElementById("txbtn").classList.add("btn-outline-primary");
            document.getElementById("rxbtn").classList.remove("btn-outline-primary");
            document.getElementById("rxbtn").classList.add("btn-success");
        }
        if (json.ptt == 1) {
            document.getElementById("txbtn").classList.remove("btn-outline-primary");
            document.getElementById("txbtn").classList.add("btn-danger");
            document.getElementById("rxbtn").classList.remove("btn-success");
            document.getElementById("rxbtn").classList.add("btn-outline-primary");
        }
    }
}

function fillData() {
    sendData('/get_freq');
    sendData('/get_mode');
    sendData('/get_ptt');
}

const interval = setInterval(function() {
    if (document.getElementById("autoupdate").checked) {
        fillData();
    }
}, 5000);


function clickcw() {
    wpm = document.getElementById("cwwpm").value;
    phrase = document.getElementById("cwphrase").value;
    if (wpm && phrase) {
        console.log(wpm);
        console.log(phrase);

        const data = {
            wpm: wpm,
            phrase: phrase
        }

        const urlParams = new URLSearchParams(data);
        url = '/send_cw?' + urlParams.toString();

        console.log(url);

        sendData(url);
    }
}

function clickfreq() {
    freq = document.getElementById("freq").value;
    if (freq) {
        const data = {
            freq: freq
        }

        const urlParams = new URLSearchParams(data);
        url = '/set_freq?' + urlParams.toString();

        console.log(url);

        sendData(url);
    }
}

function clickmode() {
    mode = this.getElementsByTagName('a')[0].innerHTML;
    if (mode) {
        document.getElementById("Mode").value = mode;
        const data = {
            mode: mode
        }

        const urlParams = new URLSearchParams(data);
        url = '/set_mode?' + urlParams.toString();

        console.log(url);

        sendData(url);
    }

}

function clicktx() {
    const data = {
        ptt: 1
    }
    const urlParams = new URLSearchParams(data);
    url = '/set_ptt?' + urlParams.toString();
    console.log(url);
    sendData(url);
}

function clickrx() {
    const data = {
        ptt: 0
    }
    const urlParams = new URLSearchParams(data);
    url = '/set_ptt?' + urlParams.toString();
    console.log(url);
    sendData(url);
}