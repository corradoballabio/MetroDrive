// set up ================================================================
var express = require('express');
var app = express();                                // create our app w/ express
var mysql = require('mysql');                       // mysql for database 
var morgan = require('morgan');                     // log requests to the console (express4)
var bodyParser = require('body-parser');            // pull information from HTML POST (express4)
var methodOverride = require('method-override');    // simulate DELETE and PUT (express4)
var session = require('client-sessions');           // manage user session with cookies


// connection configuration ==============================================

var connection = mysql.createConnection({
    host     : 'localhost',
    user     : 'root',
    password : '11cr+bl12!',
    database : 'metrodrivedb'
});

//connect to the db
connection.connect(function(error) {
    if(!!error) {
      console.log('Error: ' + error);
    } else {
      console.log("DB connected");
    }
});

// session configuration ================================================

app.use(session({
    cookieName: 'session',
    secret: 'eg[isfd-8yF9-7w2315df{}+Ijsli;;to8',
    duration: 30 * 60 * 1000,
    activeDuration: 5 * 60 * 1000,
    httpOnly: true,
    secure: true,
    ephemeral: true
}));

app.use(express.static(__dirname + '/public'));                 // set the static files location /public/img will be /img for users
app.use(morgan('dev'));                                         // log every request to the console
app.use(bodyParser.urlencoded({'extended':'true'}));            // parse application/x-www-form-urlencoded
app.use(bodyParser.json());                                     // parse application/json
app.use(bodyParser.json({ type: 'application/vnd.api+json' })); // parse application/vnd.api+json as json
app.use(methodOverride());

// =============================== routes ===============================

// api routes -----------------------------------------------------------

// get specified assicurato
app.get('/api/login', function(req, res) {
    connection.query('SELECT idAssicurato FROM assicurato WHERE email = ' + connection.escape(req.query.n) 
        + " AND password = " + connection.escape(req.query.p), function(err, rows, fields) {
        if (!err) {
            if (rows.length != 0) {
                // sets a cookie with the user's info
                req.session.user = rows[0].idAssicurato;
                
                res.send(true); 
            } else {
                res.send(false);
            }
        }
        else{
            console.log('Error while performing Query.');
        }
    });
});

// query logged user info
app.get('/api/userpage/user', function(req, res) {
    connection.query('SELECT nome, cognome, pic FROM assicurato WHERE idAssicurato = ' + connection.escape(req.session.user), 
        function(err, rows, fields) {
        if (!err) {
            res.json(rows[0]);
        }
        else{
            console.log('Error while performing Query.' + err);
        }
    }); 
});

// get assicurato veicoli
app.get('/api/userpage/vehicles', function(req, res) {
    connection.query('SELECT idVeicolo, modello, targa FROM veicolo JOIN relazionepolizza where Veicolo_idVeicolo = idVeicolo and Assicurato_idAssicurato = ' + connection.escape(req.session.user), 
        function(err, rows, fields) {
        if (!err) {
            res.json(rows);
        }
        else{
            console.log('Error while performing Query.' + err);
        }
    }); 
});

// get veicolo indici
app.get('/api/indexes', function(req, res) {
    connection.query('SELECT month(data) AS mese, year(data) AS anno, kmtot, kmSopraLimiti, frenate, frenateHarsh, accelerazioni, accelerazioniHarsh FROM indicediguida WHERE Veicolo_idVeicolo = ' + connection.escape(req.query.v) + ' ORDER BY data DESC', 
        function(err, rows, fields) {
        if (!err) {
            res.json(rows);
        }
        else{
            console.log('Error while performing Query.' + err);
        }
    }); 
});


// application routes ---------------------------------------------------

app.get('/', function(req, res) {;
    res.sendFile('public/login.html', { root : __dirname});
});

app.get('/userpage', function(req, res) {
  if (req.session && req.session.user) { // Check if session exists
    // lookup the user in the DB by pulling their email from the session
    connection.query('SELECT idAssicurato FROM assicurato WHERE idAssicurato = ' + connection.escape(req.session.user), function (err, rows, fields) {
      if (rows.length == 0) {
        // if the user isn't found in the DB, reset the session info and
        // redirect the user to the login page
        req.session.reset();
        res.sendFile('public/login.html', { root : __dirname});
      } else {
        // expose the user to the template
        // render the userpage page
        res.sendFile('public/userpage.html', { root : __dirname});
      }
    });
  } else {
    res.redirect('/login');
  }
});

app.get('/logout', function(req, res) {
    req.session.reset();
    res.redirect('/');
});


// set server ready to accept request ===================================

app.listen(3000);