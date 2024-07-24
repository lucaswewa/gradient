var mdns = require('mdns-js');
//if you have another mdns daemon running, like avahi or bonjour, uncomment following line
//mdns.excludeInterface('0.0.0.0');

var browser = mdns.createBrowser(mdns.tcp("xthings"));
var count = 0

browser.on('ready', function () {
    browser.discover(); 
});

browser.on('update', function (data) {
    console.log(count)
    console.log('addresses:', data["addresses"]);
    console.log('query:', data["query"]);
    console.log('type:', data["type"]);
    console.log('host:', data["host"]);
    console.log('port:', data["port"]);
    console.log('fullname:', data["fullname"]);
    console.log('txt:', data["txt"]);
    console.log('interfaceIndex:', data["interfaceIndex"]);
    console.log('networkInterface:', data["networkInterface"]);
    count = count + 1
});