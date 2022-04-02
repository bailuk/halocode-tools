
/**
 * 
 * To start server:
 * npm run install && npm run
 * 
 * This installs dependencies and runs:
 * mosquitto_sub -t test  | node plot.js
 *   
 * 
 */


let dto = {
    data: [],
    message: ''
}


const fs = require('fs')

const express = require('express');
const app = express();
const port = 8080;

app.get('/api', (req, res) => {
    res.send(dto)
});


app.get('/', (req, res) => {
    fs.readFile('plot.html', 'utf8' , (err, data) => {
        if (err) {
            console.error(err)
            return
        }
        res.send(data)
    })
});


app.listen(port, () => console.log(`server is listening on port ${port}!`))


process.stdin.on('data', data => {

    try {
        obj = JSON.parse(data)
        if (obj.message == 'accel') {
            const accel = JSON.parse(obj.value)
            accel.time = new Date()
            dto.data.push(accel)
            
            if (dto.data.length > 50) {
                dto.data.splice(0,1)
            }

        }


        else if (obj.message == 'message') {
            dto.message = obj.value
        }

    } catch(error) {
        console.log(`Error: ${error}`)
    }

});
