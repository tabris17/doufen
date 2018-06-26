/**
 * 主进程代码入口
 */
const path = require('path')
const url = require('url')
const { ArgumentParser } = require('argparse')
const { app, dialog, ipcMain, Notification } = require('electron')
const { splashScreen, createMainWindow, createTray, getMainWindow } = require('./window')
const childProcess = require('child_process')
const electronReferer = require('electron-referer')
const Messenger = require('./messenger')


const DEFAULT_SERVICE_PORT = 8398
const DEFAULT_SERVICE_HOST = '127.0.0.1'
const MESSENGER_RECONNECT_TIMES = 10
const MESSENGER_RECONNECT_INTERVAL = 5000
const MAX_LOG_LINES = 1000


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
            if (!win.isVisible()) win.show()
            else if (win.isMinimized()) win.restore()
            win.focus()
        }
    })
    if (isDuplicateInstance) {
        app.quit()
    }

    return isDuplicateInstance
}


let logger = {
    lines: new Array(MAX_LOG_LINES),
    cursor: 0,
    append(line) {
        this.lines[this.cursor] = line
        return this.cursor = (this.cursor + 1) % MAX_LOG_LINES
    },
    all() {
        let partA = this.lines.slice(this.cursor).join("\n")
        let partB = this.lines.slice(0, this.cursor).join("\n")
        return (partA + partB).trim()
    },
    restore() {
        this.cursor = 0
        this.lines = new Array(MAX_LOG_LINES)
    }
}

global.sharedData = {
    logger: logger
}


/**
 * 程序入口主函数
 * 
 * @param {Array} args 
 */
function main(args) {
    if (ensureSingleton()) {
        return
    }

    let parsedArgs = parseArgs(args)
    
    global.debugMode = parsedArgs.debug
    if (debugMode) {
        console.debug = console.log
    } else {
        console.debug = (...args) => {}
        childProcess.spawn('service', ['-q'])
    }

    let serviceUrl = url.format({
        port: parsedArgs.port,
        pathname: '/',
        protocol: 'http:',
        hostname: DEFAULT_SERVICE_HOST
    })

    let messenger = new Messenger(url.format({
        port: parsedArgs.port,
        pathname: '/notify',
        protocol: 'ws:',
        hostname: DEFAULT_SERVICE_HOST
    }), 100, times=MESSENGER_RECONNECT_TIMES)

    messenger.on('fail', () => {
        dialog.showMessageBox({
            type: 'error',
            buttons: ['确定(&O)'],
            noLink: true,
            title: '错误',
            normalizeAccessKeys: true,
            message: '服务没有响应。请重新启动程序。'
        }, () => {
            app.exit()
        })
    })

    app.on('ready', () => {
        let splash = splashScreen()
        let win = createMainWindow()

        const handleMessengerClose = () => {
            messenger.once('close', () => {
                let notification = new Notification({
                    title: '错误',
                    body: '服务连接中断。正在尝试重新连接...'
                })
                notification.show()

                messenger.connect(MESSENGER_RECONNECT_INTERVAL, 3)
                messenger.once('open', () => {
                    let notification = new Notification({
                        title: '消息',
                        body: '服务重新连接成功！'
                    })
                    notification.show()

                    handleMessengerClose()
                })
            })
        }

        const bootstrap = () => {
            console.debug('service started')

            let splashWebContents = splash.webContents
            splashWebContents.send('ready-to-connect')

            win.loadURL(serviceUrl)
            win.once('ready-to-show', () => {
                console.debug('main window rendered')

                splashWebContents.send('ready-to-show')
                splash.once('closed', () => {
                    win.show()
                    createTray()
                })
            })

            handleMessengerClose()
        }

        console.debug('waiting for service to be started')
        if (messenger.isConnected) {
            bootstrap()
        } else {
            messenger.once('open', () => {
                bootstrap()
            })
        }

        messenger.on('message', (data) => {
            switch (data.sender) {
                case 'logger':
                    logger.append(data.message)
                    win.webContents.send('logger-update')
                    break
                case 'worker':
                    let noticeTitle, noticeBody
                    switch (data.event) {
                        case 'error':
                            noticeTitle = '通知'
                            noticeBody = `工作进程"${data.src}"发生错误: ${data.message}`
                            break
                        case 'done':
                            noticeTitle = '通知'
                            noticeBody = `工作进程"${data.src}"执行完毕`
                            win.webContents.send('worker-status-change')
                            break
                        case 'ready':
                            noticeTitle = '通知'
                            noticeBody = `工作进程"${data.src}"已启动`
                            win.webContents.send('worker-status-change')
                            break
                        case 'working':
                            noticeTitle = '通知'
                            noticeBody = `工作进程"${data.src}"开始执行任务"${data.target}"`
                            win.webContents.send('worker-status-change')
                            break
                    }
                    (new Notification({
                        title: noticeTitle,
                        body: noticeBody
                    })).show()
                    break
            }
        })
    
    })

    app.on('activate', () => {
        if (!getMainWindow()) {
            let win = createMainWindow()
            win.loadURL(serviceUrl).once('ready-to-show', () => {
                win.show()
            })
        }
    })

    app.on('window-all-closed', () => {
        if (process.platform !== 'darwin') {
            app.quit()
        }
    })

    app.on('will-quit', () => {
        console.debug('app will quit')
        messenger.close()
    })

    electronReferer('https://www.douban.com/')
}

let mainArgs = []

if (process.argv[1] && [__filename, __dirname].indexOf(path.resolve(process.argv[1])) > -1) {
    mainArgs = process.argv.slice(2)
} else if (process.argv) {
    mainArgs = process.argv.slice(1)
}

main(mainArgs)