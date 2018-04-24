process.once('loaded', () => {
    const { shell, remote } = require('electron')

    global.system = {
        require: global.require,
        module: global.module,

        openLink(url, options, callback) {
            return shell.openExternal(url, options, callback)
        }
    }

    delete global.require
    delete global.module

    global.eval = () => {
        throw new Error('disabled')
    }

    console.log('process.loaded')
})