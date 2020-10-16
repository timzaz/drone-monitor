function bootstrap () {
    let namespace = '/'
    document.onreadystatechange
    const socket = io.connect(namespace)

    // Handle new connections
    socket.on('connect', function () {
        // Indicate we are now monitoring live
        // document.getElementById('connection-status').innerText = 'Connected'
    })

    socket.on('disconnect', function () {
        // Indicate we are no longer live
        // document.getElementById('connection-status').innerText = 'Disconnected'
    })

    socket.on('drone_update', function (data) {
        // Update table items
        let body = document.getElementById('body')
        let element = document.createElement('tr')
        element.id = data.drone

        if (element.highlight) element.classList.add('is-selected')
        let droneData = document.createElement('td')
        droneData.innerText = data.drone

        let speedData = document.createElement('td')
        speedData.innerText = data.speed

        element.appendChild(droneData)
        element.appendChild(speedData)

        try {
            let oldElement = document.getElementById(data.drone)
            if (typeof oldElement !== "undefined") {
                body.removeChild(oldElement)
            }
        } catch (error) {
            
        }
        
        body.appendChild(element)
    })
}

function docReady (fn) {
    if (
        document.readyState === 'complete' ||
        document.readyState === 'interactive') {
        
        setTimeout(fn, (1))
    } else {
        document.addEventListener('DOMContentLoaded', fn)
    }
}

docReady(bootstrap)
