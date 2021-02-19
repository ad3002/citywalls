var token = '';
var key = "";


var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/Etxe');

var db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', function() {
  console.log('DB connected...');
});


var ItemsSchema = mongoose.Schema({
    title: String, 
    image: String,
    address: String,
    dome: String,
    author_links: String,
    author_names: String,
    build_date: String,
    style: String,
    views: String,
    comments: String,
    link: String
});

var Item = mongoose.model('Items', ItemsSchema);

var Bot = require('node-telegram-bot-api'),
    bot = new Bot(token, { polling: true });

console.log('bot server started...');

var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var ObjectId = require('mongodb').ObjectID;
var url = 'mongodb://localhost:27017/Etxe';

bot.onText(/^\/say_hello (.+)$/, function (msg, match) {
  var name = match[1];
  bot.sendMessage(msg.chat.id, 'Hello ' + name + '!').then(function () {
    // reply sent!
  });
});

bot.onText(/^\/f (.+)$/, function (msg, match) {

  var name = match[1];

  MongoClient.connect('mongodb://127.0.0.1:27017/Etxe', function(err, db) {

    var address = match[1];

    if (err) throw err;
    console.log("Connected to Database");  
    // Fetch the collection test
    var collection = db.collection('Items');
    collection.find({"address":address}).nextObject(function(err, doc) {            
        console.log(address);
        console.log(doc);
        console.log(err);

        if (doc == null) {
                  bot.sendMessage(msg.chat.id,  
                  "Не найдено"
                  ).then(function () {
          });
          return;
        }

        bot.sendMessage(msg.chat.id,  
                  doc["title"] + 
                  '\n\nСтиль: ' + doc["style"] + 
                  '\nАрхитектор: ' + doc["authors_names"] + 
                  '\nПостроен: ' + doc["build_year"] + '\n' + 
                  doc["image"]
                  ).then(function () {

                    bot.sendMessage(msg.chat.id,  
                              doc["link"]
                              ).then(function () {});
                    });

                    
                  });
        
  });
});

bot.onText(/^\/s (.+)$/, function (msg, match) {

  MongoClient.connect('mongodb://127.0.0.1:27017/Etxe', function(err, db) {

    var address = match[1];

    if (err) throw err;
    console.log("Connected to Database");  
    // Fetch the collection test
    var collection = db.collection('Streets');
    collection.find({"title": new RegExp(address, 'i')}).toArray(function(err, docs) {            
        console.log(address);
        console.log(docs);
        console.log(err);

        var results = "Result:\n";

        for (i = 0; i < docs.length; i++) { 
          results = results + docs[i]["title"] + "\n";
        }

        bot.sendMessage(msg.chat.id,  
                  results
                  ).then(function () {
    });
  });
  });
});



bot.onText(/^\/h (.+)$/, function (msg, match) {

  MongoClient.connect('mongodb://127.0.0.1:27017/Etxe', function(err, db) {

    var address = match[1];

    if (err) throw err;
    console.log("Connected to Database");  
    // Fetch the collection test
    var collection = db.collection('Items');
    collection.find({"address": new RegExp(address, 'i')}).toArray(function(err, docs) {            
        console.log(address);
        console.log(docs);
        console.log(err);

        if (docs.length > 50) {
          bot.sendMessage(msg.chat.id,  
                  "Слишком широкий запрос"
                  ).then(function () {
          });
          return;
        }

        var results = "Result:\n";

        for (i = 0; i < docs.length; i++) { 
          results = results + docs[i]["address"] + "\n";
        }

        bot.sendMessage(msg.chat.id,  
                  results
                  ).then(function () {
        });
  });
  });
});

bot.on('location', function (msg, match) {

  var url = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+msg["location"]["latitude"]+","+msg["location"]["longitude"]+"&key="+key;

  console.log(msg);
  console.log(url);
});

