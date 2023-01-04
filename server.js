const express = require('express');
const app = express();
const path = require('path');
var port = 3000;
let {PythonShell} = require('python-shell');

app.use(express.static(path.join(__dirname)));

app.listen(port, function () {
    console.log(`server running on port ${port}`);
})

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname + '/index.html'));
});

app.post('/submit', executeData); 

function executeData(req, res) {
    var fileStructure = req.query.fileStructure;
    var environment = req.query.environment;
    var keywords = req.query.keywords;
    if(!fileStructure || !environment) {
        res.sendFile(path.join(__dirname + '/nofile.html'));
    }
    else {
        let options = { args : [fileStructure],
                        pythonPath: environment};
        if(keywords) {
            options.args = options.args.concat([keywords]);
        }
        PythonShell.run('./DirectoryToGraph.py', options, function(err, data) {
                if(err) res.send(err);
                else res.sendFile(path.join(__dirname + '/success.html'));
        });
    }
}


