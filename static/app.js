document.addEventListener("DOMContentLoaded", function(event) {
    sendData('/init');
    sendData('/get_rigs');
    sendData('/get_ports');
    sendData('/get_paritys');
    fillData();

    document.getElementById("cwbtn").onclick = clickcw;
    document.getElementById("freqbtn").onclick = clickfreq;
    document.getElementById("txbtn").onclick = clicktx;
    document.getElementById("rxbtn").onclick = clickrx;
    document.getElementById("savebtn").onclick = clicksave;

    var elms = document.querySelectorAll("[id='modebtn']");
    for(var i = 0; i < elms.length; i++)
        elms[i].onclick = clickmode;

    var elms = document.querySelectorAll("[id='rigbtn']");
    for(var i = 0; i < elms.length; i++)
        elms[i].onclick = clickrig;

    var elms = document.querySelectorAll("[id='portbtn']");
    for(var i = 0; i < elms.length; i++)
        elms[i].onclick = clickport;

    var elms = document.querySelectorAll("[id='paritybtn']");
    for(var i = 0; i < elms.length; i++)
        elms[i].onclick = clickparity;

    setInterval(function() {
        if (document.getElementById("autoupdate").checked) {
            fillData();
        }
    }, 5000);

    setInterval(function() {
        sendData('/get_status');
    }, 2000);

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
    //console.log(json);
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
    if (json.hasOwnProperty('status')) {
        document.getElementById("status").classList.remove("text-bg-warning");
        if (json.status == false) {
            document.getElementById("status").classList.remove("text-bg-success");
            document.getElementById("status").classList.add("text-bg-danger");
            document.getElementById("status").innerHTML = "OFFLINE";
        }
        if (json.status == true) {
            document.getElementById("status").classList.remove("text-bg-danger");
            document.getElementById("status").classList.add("text-bg-success");
            document.getElementById("status").innerHTML = "ONLINE";
        }
    }
    if (json.hasOwnProperty('rigs')) {
        const ul = document.getElementById("rigs");
        ul.innerHTML = "";
        json.rigs.forEach(function (item, index) {
            //console.log(item, index);
            const li = document.createElement("li");
            const a = document.createElement("a");
            li.setAttribute('id', 'rigbtn');
            a.classList.add("dropdown-item");
            a.setAttribute('href', '#');
            a.appendChild(document.createTextNode(item));
            li.appendChild(a);
            ul.appendChild(li);
        });
    }
    if (json.hasOwnProperty('ports')) {
        const ul = document.getElementById("ports");
        ul.innerHTML = "";
        json.ports.forEach(function (item, index) {
            //console.log(item, index);
            const li = document.createElement("li");
            const a = document.createElement("a");
            li.setAttribute('id', 'portbtn');
            a.classList.add("dropdown-item");
            a.setAttribute('href', '#');
            a.appendChild(document.createTextNode(item));
            li.appendChild(a);
            ul.appendChild(li);
        });
    }

    if (json.hasOwnProperty('paritys')) {
        const ul = document.getElementById("paritys");
        ul.innerHTML = "";
        json.paritys.forEach(function (item, index) {
            const li = document.createElement("li");
            const a = document.createElement("a");
            li.setAttribute('id', 'paritybtn');
            a.classList.add("dropdown-item");
            a.setAttribute('href', '#');
            a.appendChild(document.createTextNode(item));
            li.appendChild(a);
            ul.appendChild(li);
        });
    }

    if (json.hasOwnProperty('rig')) {
        document.getElementById("Rig").value = json.rig.rigModel;
        document.getElementById("Port").value = json.rig.rigDevice;
        document.getElementById("Rate").value = json.rig.rigRate;
        document.getElementById("DataBits").value = json.rig.rigDataBits;
        document.getElementById("StopBits").value = json.rig.rigStopBits;
        document.getElementById("Parity").value = json.rig.rigParity;
        document.getElementById("WriteDelay").value = json.rig.rigWriteDelay;
    }

}

function fillData() {
    sendData('/get_freq');
    sendData('/get_mode');
    sendData('/get_ptt');
}


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

function clickrig() {
    rig = this.getElementsByTagName('a')[0].innerHTML;
    if (rig) {
        document.getElementById("Rig").value = rig;
        console.log(rig);
    }
}

function clickport() {
    port = this.getElementsByTagName('a')[0].innerHTML;
    if (port) {
        document.getElementById("Port").value = port;
        console.log(port);
    }
}

function clickparity() {
    parity = this.getElementsByTagName('a')[0].innerHTML;
    if (parity) {
        document.getElementById("Parity").value = parity;
        console.log(parity);
    }
}

function clicksave() {
    rig = document.getElementById("Rig").value;
    port = document.getElementById("Port").value;
    rate = document.getElementById("Rate").value;
    databits = document.getElementById("DataBits").value;
    stopbits = document.getElementById("StopBits").value;
    parity = document.getElementById("Parity").value;
    writedelay = document.getElementById("WriteDelay").value;

    if (rig && port) {
        const data = {
            rigDevice: port,
            rigModel: rig,
            rigRate: rate,
            rigDataBits: databits,
            rigStopBits: stopbits,
            rigParity: parity,
            rigWriteDelay: writedelay
        }
        const urlParams = new URLSearchParams(data);
        url = '/set_rig?' + urlParams.toString();
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