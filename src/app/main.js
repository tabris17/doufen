/**
 * 主进程代码入口
 */
const path = require('path')
const { ArgumentParser } = require('argparse')
const { app, dialog } = require('electron')
const { initializeWindow, getMainWindow } = require('./window')


const DEFAULT_SERVICE_URL = 'http://127.0.0.1:8398/'


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

    initializeWindow(parsedArgs.service)

    app.on('all-window-closed', () => {
        if (process.platform !== 'darwin') {
            app.quit()
        }
    })
}


if ([__filename, __dirname].indexOf(path.resolve(process.argv[1])) > -1) {
    main(process.argv.slice(2))
}