const http = require('http');
const express = require('express');
//const MessagingResponse = require('twilio').twiml.MessagingResponse;
const bodyParser = require('body-parser').urlencoded({
  extended: false,
});
const twilio = require('twilio')(
    process.env.TWILIO_ACCOUND_SID,
    process.env.TWILIO_AUTH_TOKEN
);

const MessagingResponse = require('twilio').twiml.MessagingResponse;

const app = express();

const nodemailer = require('nodemailer')

var transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'smartalarm42@gmail.com',
    pass: 'SmartAlarm42!!'
  }
});

var mailOptions = {
  from: 'smartalarm42@gmail.com',
  to: 'smartalarm42@gmail.com',
  subject: 'Sending Email using Node.js',
  text: 'default'
};

// [START gae_flex_twilio_recieve_sms]
app.post('/sms', bodyParser, (req, res) => {
  const twiml = new MessagingResponse();

  const body = req.body.Body;
  mailOptions.text = body
  twiml.message('message recieved');

  res.writeHead(200, {'Content-Type': 'text/xml'});
  res.end(twiml.toString());

  transporter.sendMail(mailOptions, function(error, info){
    if (error) {
      console.log(error);
    } else {
      console.log('Email sent: ' + info.response);
    }
  });
});
// [END gae_flex_twilio_recieve_sms]


const PORT = process.env.PORT;
app.listen(PORT, () => {
    console.log(`App listening on port ${PORT}`);
    console.log('Press Ctrl+C to quit.');
});
//http.createServer(app).listen(1337, () => {
//  console.log('Express server listening on port 1337');
//});
