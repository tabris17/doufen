/**
 * 访问 Python 的后台服务
 */
const ClientRequest = require('electron')
const WebSocket = require('ws')

function getOptions(url) {
    return {
        method: 'POST',
        url: url,
        port: 1234
    }
}

function addAuthorization(resolve, reject) {

}