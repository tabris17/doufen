const EventEmitter = require('events')
const WebSocket = require('ws')

class Notifier extends EventEmitter {

    /**
     * 创建通知器
     * @param {string} service 
     */
    constructor(service, interval=500) {
        super()
        this._service = service
        this._interval = interval
        this.connect()
    }

    connect() {
        let websocket = new WebSocket(this._service, {
            origin: 'localhost'
        })
        websocket.on('error', (error) => {
            if (error.code == 'ECONNREFUSED') {
                console.debug('WebSocket ECONNREFUSED: retry late')
                setTimeout(() => {
                    this.connect()
                }, this._interval)
            }
        })
        websocket.on('close', (code, reason) => {
            this.emit('close', code, reason)
        })
        websocket.on('open', () => {
            this.emit('open')
        })
        websocket.on('message', (data) => {
            this.emit('message', data)
        })
        this._websocket = websocket
    }

    close() {
        this._websocket.close()
    }

    send(...args) {
        this._websocket.send.apply(this._websocket, args)
    }
}

module.exports = Notifier