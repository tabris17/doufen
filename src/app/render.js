process.once('loaded', () => {
    const { shell, remote } = require('electron')
    const path = require('path')
    const EventEmitter = require('events')

    global.system = {
        require: global.require,
        module: global.module,

        /**
         * 引用本地的代码
         * @param {string} mod
         */
        requireNative(mod) {
            return system.require(path.join(__dirname, mod))
        },

        /**
         * 在浏览器里打开链接
         * @param {string} url 
         * @param {JSON} options 
         * @param {Function} callback 
         */
        openLink(url, options, callback) {
            return shell.openExternal(url, options, callback)
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