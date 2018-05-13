/**
 * 与后台服务通信
 */
const EventEmitter = require('events')
const WebSocket = require('ws')

const SILENT_CLOSE_CODE = 892356

/**
 * 支持重试连接的 WebSocket 客户端
 * 
 * @extends EventEmitter
 */
class Messenger extends EventEmitter {

    /**
     * 创建 Messenger
     * 
     * @param {string} address
     * @param {int} interval
     * @param {int} times
     */
    constructor(address, interval=500, times=Number.MAX_SAFE_INTEGER) {
        super()
        this._address = address
        this.connect(interval, times)
    }

    /**
     * 连接服务器
     * 
     * @param {int} interval
     * @param {int} times
     */
    connect(interval, times) {
        let websocket = new WebSocket(this._address, {
            origin: 'localhost'
        })
        websocket.on('error', (error) => {
            if (error.code == 'ECONNREFUSED') {
                if (times <= 0) {
                    console.debug('[WebSocket]ECONNREFUSED: stop trying')
                    this.emit('fail')
                    return
                }

                console.debug(`[WebSocket]ECONNREFUSED: try to reconnect after ${interval}ms later. ${times - 1} times left`)

                setTimeout(() => {
                    this.connect(interval, times - 1)
                }, interval)
            } else {
                console.debug('[WebSocket]error:' + error.message)
            }
        })
        websocket.once('close', (code, reason) => {
            console.debug(`[WebSocket]closed: code: ${code} reason: ${reason}`)
            if (code == SILENT_CLOSE_CODE) {
                console.debug('slient closed')
                return
            }
            this.emit('close', code, reason)
        })
        websocket.once('open', () => {
            console.debug('[WebSocket]opened')
            this.emit('open')
        })
        websocket.on('message', (data) => {
            console.debug('[WebSocket]message received:' + data)
            this.emit('message', data)
        })
        this._websocket = websocket
    }

    /**
     * 是否已经连接
     * 
     * @returns {boolean}
     */
    get isConnected() {
        let websocket = this._websocket
        return websocket.readyState === websocket.OPEN
    }

    /**
     * 关闭连接
     * 
     * @param {boolean} silent 
     */
    close(silent=true) {
        this._websocket.close(SILENT_CLOSE_CODE)
    }

    /**
     * 终止连接
     */
    terminate() {
        this._websocket.terminate()
    }

    /**
     * 发送消息
     * 
     * @param {any} args 
     */
    send(...args) {
        this._websocket.send.apply(this._websocket, args)
    }
}

module.exports = Messenger