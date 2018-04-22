/**
 * 主进程代码入口
 */
const path = require('path')
const { ArgumentParser } = require('argparse')
const { app, dialog } = require('electron')
const { registerWindow, getWindow } = require('./window')


const DEFAULT_SERVICE_URL = 'http://127.0.0.1:8398/'

/**
 * 解析命令行参数
 * 
 * @param {Array} args 
 */
function parseArgs(args) {
    let argsParser = ArgumentParser({
        version: package.version,
        description: package.description,
        addHelp: true
    })
    argsParser.addArgument(
        ['-d', '--debug'], {
            action: 'storeTrue',
            help: 'Set debug mode on.',
            defaultValue: false,
            required: false
        }
    )
    argsParser.addArgument(
        ['-s', '--service'], {
            action: 'store',
            metavar: 'url',
            dest: 'service',
            help: 'Specify the service url.',
            defaultValue: DEFAULT_SERVICE_URL,
            required: false
        }
    )
    return argsParser.parseArgs(args)
}


function singleton() {
    const isDuplicateInstance = app.makeSingleInstance((commandLine, workingDirectory) => {
        let win = getWindow()
        if (win) {
            if (win.isMinimized()) win.restore()
            win.focus()
        }
    })
    if (isDuplicateInstance) {
        app.quit()
    }
}


/**
 * 程序入口主函数
 * 
 * @param {Array} args 
 */
function main(args) {
    let parsedArgs = parseArgs(args)
    if (parsedArgs.debug) {
        process.env.DEBUG = '1'
    }

    registerWindow()

    app.on('all-window-closed', () => {
        if (process.platform !== 'darwin') {
            app.quit()
        }
    })
}


if (path.resolve(process.argv[1]) === __filename) {
    main(process.argv.slice(2))
}