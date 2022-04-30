
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
    message: '',
    window: 0,
    auto: true
}

let calculatedPos = 0


const { spawn } = require( 'child_process' );

const exec = (cmd, pars) => {
    const command = spawn(cmd, pars, {detached: true})
    // console.log( `stderr: ${ command.stderr.toString() }` );
    // console.log( `stdout: ${ command.stdout.toString() }` );
}

const sendMessage = (topic, message, value) => {
    const msg = `{"message": "${message}", "value": "${value}"}`
    exec('mosquitto_pub', ['-t', topic, '-m', msg])
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
    dto.auto = false
    sendMessage('meteo', 'windowset', 'up')
    res.send("ok")
})

app.put('/api/window/down', (req, res) => {
    dto.auto = false
    sendMessage('meteo', 'windowset', 'down')
    res.send("ok")
})

app.put('/api/window/auto', (req, res) => {
    dto.auto = true
    res.send("ok")
})


const sendFile=(file, res) => {
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
        else if (obj.message == 'window') {
            dto.window = obj.value
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


const getPosChange = (data) => {
    if (data.temperature > 40) {
        return 10
    }

    if (data.humidity > 90) {
        return -100
    }

    if (data.temperature < 10) {
        return -10
    }

    if (data.temperature < 20) {
        return -5
    }

    if (data.temperature > 25) {
        return 5
    }
    
    return 0
}


const fireTimer = () => {
    setTimeout(() => {
        const data = dto.data[dto.data.length-1]

        if (data) {
            calculatedPos = Math.min(90, Math.max(0, calculatedPos + getPosChange(data)))
            if (dto.auto) sendMessage('meteo', 'windowset', calculatedPos)
        }
        fireTimer()
    }, 3000);
}

fireTimer()
