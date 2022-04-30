
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

const express = require('express')
const app = express()
const port = 8080

app.use('/favicon.png', express.static('weathericon/png/fair_day.png'))

app.get('/api', (req, res) => {
    res.send(dto)
})

app.get('/', (req, res) => {
    sendFile('plot.html', res)
})

app.get('/icons/:file', (req, res) => {
    sendFile(`weathericon/svg/${req.params.file}`, res)
})

app.put('/api/window/up', (req, res) => {
    console.log('up')
})

app.put('/api/window/down', (req, res) => {
    console.log('down')
})


sendFile=(file, res) => {
    fs.readFile(file, 'utf8', (err, data) => {
        if (err) {
            console.error(err)
            throw new Error('No such file')
        }
        res.send(data)
    })    
}

app.listen(port, () => console.log(`server is running on http://localhost:${port}`))

process.stdin.on('data', data => {
    try {
        obj = JSON.parse(data)
        if (obj.message == 'sensors') {
            const sample = JSON.parse(obj.value)
            sample.time = new Date()
            sample.icon = iconFromSensors(sample)
            dto.data.push(sample)
            
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

const iconFromSensors = (value) => {
    if          (value.light    > 50) {
        if      (value.humidity > 80) return 'heavyrain'
        else if (value.humidity > 60) return 'lightrain'
        else                          return 'clearsky_day'
    } else if   (value.light    > 10) {
        if      (value.humidity > 80) return 'heavyrain'
        else if (value.humidity > 60) return 'lightrain'
        else                          return 'cloudy'
    } else {
        if      (value.humidity > 80) return 'heavyrainshowers_night'
        else if (value.humidity > 60) return 'lightrainshowers_night'
        else                          return 'clearsky_night'
    }
}
