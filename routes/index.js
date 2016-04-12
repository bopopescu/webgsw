var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.sendfile(htmlpath+"index.html");
});

router.post('/contacto', function(req, res, next) {

    var nombre = req.body.name;
    var email = req.body.email;
    var mensaje = req.body.message;

    var nodemailer = require('nodemailer');

    var transporter = nodemailer.createTransport('smtps://olivagustavov%40gmail.com:wathsupman"@smtp.gmail.com');


    var mailOptions = {
      from: 'olivagustavov@gmail.com',
      to: 'goliva@gosmartware.com',
      subject: 'Nuevo Contacto',
      text: 'nombre : '+nombre +"\n email: "+email + "\n mensaje: "+mensaje, // plaintext body
      html: '' // html body
    };


    transporter.sendMail(mailOptions, function (error, info) {
      if (error) {
        return console.log(error);
        res.json({ code:1 ,error: true});
      }
      console.log('Message sent: ' + info.response);
      res.json({code:0,error: false});
    });


});


module.exports = router;
