const express = require('express');
const server = express();
const querystring = require('querystring');
const bodyParser = require('body-parser');
const { exec } = require('child_process');

server.use(bodyParser.urlencoded({ extended: false }));
server.use(bodyParser.json());

server.set('port', 3000);

//Basic routes
server.get('/', (request, response) => {
    response.status(500);
});

// http://localhost:3000/vnc?host=IP&port=port
server.get('/vnc', (request, response) => {
    console.log('Received VNC request');
    let host = request.query.host;
    let port = request.query.port;
    let clientparams = host + ':' + port;

    console.log(`Server params: ${clientparams}`);

    exec('lxterminal -e /home/pi/VNCBinaries/runclient ' + clientparams + '&' , (err, stdout, stderr) => {
        console.log(stdout);
        console.log(stderr);
    });

    child.on('exit', code => {
        console.log(`Exit code is: ${code}`);
    });

    response.status(200);
    response.end();
});

//Express error handling middleware
server.use((request, response) => {
    response.type('text/plain');
    response.status(505);
    response.send('Error page');
});

//Binding to a port
server.listen(3000, () => {
    console.log('Express server started at port 3000');
});