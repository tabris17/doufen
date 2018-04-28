/**
 * renderer 进程调用的模块
 */
process.once('loaded', () => {
    const { shell, remote } = require('electron')
    const path = require('path')
    const EventEmitter = require('events')

    global.system = {
        require: global.require,
        module: global.module,

        /**
         * 在浏览器里打开链接
         * @param {string} url 
         * @param {JSON} options 
         * @param {Function} callback 
         * @returns {boolean}
         */
        openLink(url, options, callback) {
            return shell.openExternal(url, options, callback)
        },

        /**
         * 返回程序路径
         * @returns {string}
         */
        getAppPath() {
            return __dirname
        }
    }
    system.__proto__ = EventEmitter.prototype

    global.document.addEventListener('DOMContentLoaded', () => {
        const jquery = require('jquery')
        require('mustache').tags = ['${', '}']
        global.$ = jquery
        system.emit('loaded')
    })

    delete global.require
    delete global.module

    global.eval = () => {
        throw new Error('disabled')
    }
})