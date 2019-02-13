const express = require('express');

let app = express();

app.listen(3000, () => {
    console.log(`Server started on port`);
});

app.get('/', (req, res) => {
     res.json({'a':12});;
});

app.get('/a', (req, res) => {
     res.redirect('https://www.google.com');
});