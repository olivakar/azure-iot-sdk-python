const fs = require('fs')
const aedes = require('aedes')()
const port = 8883

const options = {
    key: fs.readFileSync('/Users/olivakar/WorkspaceFork/azure-iot-sdk-python/azure-iot-device/samples/meantimerecovery/self_key.pem'),
    cert: fs.readFileSync('/Users/olivakar/WorkspaceFork/azure-iot-sdk-python/azure-iot-device/samples/meantimerecovery/self_cert.pem')
}

const server = require('tls').createServer(options, aedes.handle)

server.listen(port, function () {
    console.log('server started and listening on port', port)
})

aedes.on('clientError', function (client, err) {
  console.log('client error', client.id, err.message, err.stack)
})

aedes.on('connectionError', function (client, err) {
  console.log('client error', client, err.message, err.stack)
})

aedes.on('publish', function (packet, client) {
  if (packet && packet.payload) {
    console.log('publish packet:', packet.payload.toString())
  }
  if (client) {
    console.log('message from client', client.id)
  }
})

aedes.on('subscribe', function (subscriptions, client) {
  if (client) {
    console.log('subscribe from client', subscriptions, client.id)
  }
})

aedes.on('client', function (client) {
  console.log('new client', client.id)
})