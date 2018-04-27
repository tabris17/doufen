/**
 * 主进程代码入口
 */
const path = require('path')
const url = require('url')
const { ArgumentParser } = require('argparse')
const { app, dialog } = require('electron')
const { initializeWindow, getMainWindow } = require('./window')
const Notifier = require('./notifier')


const DEFAULT_SERVICE_PORT = 8398
const DEFAULT_SERVICE_HOST = '127.0.0.1'


/**
 * 解析命令行参数
 * 
 * @param {Array} args 
 */
function parseArgs(args) {
    const package = require('./package.json')
    let argsParser = ArgumentParser({
        version: package.version,
        prog: package.commandName,
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
        ['-p', '--port'], {
            action: 'store',
            dest: 'port',
            metavar: 'port',
            type: 'int',
            help: 'Specify the port of service.',
            defaultValue: DEFAULT_SERVICE_PORT,
            required: false
        }
    )
    return argsParser.parseArgs(args)
}


/**
 * 确保程序单例运行
 */
function ensureSingleton() {
    const isDuplicateInstance = app.makeSingleInstance((commandLine, workingDirectory) => {
        let win = getMainWindow()
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
    ensureSingleton()

    let parsedArgs = parseArgs(args)
    
    global.debugMode = parsedArgs.debug
    if (debugMode) {
        console.debug = console.log
    } else {
        console.debug = (...args) => {}
    }

    let notifier = new Notifier(url.format({
        port: parsedArgs.port,
        pathname: '/notify',
        protocol: 'ws:',
        hostname: DEFAULT_SERVICE_HOST
    }))

    initializeWindow(url.format({
        port: parsedArgs.port,
        pathname: '/',
        protocol: 'http:',
        hostname: DEFAULT_SERVICE_HOST
    }))

    app.on('all-window-closed', () => {
        if (process.platform !== 'darwin') {
            app.quit()
        }
    })
}


if ([__filename, __dirname].indexOf(path.resolve(process.argv[1])) > -1) {
    main(process.argv.slice(2))
}