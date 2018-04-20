/**
 * 创建程序主窗口
 */
const isNullOrUndefined = require('util')
const { app, BrowserWindow, Tray, Menu, dialog } = require('electron')
const path = require('path')
const url = require('url')

const WIN_HEIGHT = 640
const WIN_WIDTH = 960
const WIN_TITLE = '豆坟'
const WIN_ICON = path.join(__dirname, 'assets/douban.ico')

let window
let tray

function createWindow() {
    let debug = process.env.DEBUG

    window = new BrowserWindow({
        width: WIN_WIDTH,
        height: WIN_HEIGHT,
        minWidth: WIN_WIDTH,
        minHeight: WIN_HEIGHT,
        type: debug ? 'normal' : 'splash',
        title: WIN_TITLE,
        show: true,
        icon: WIN_ICON
    })
    window.loadURL(url.format({
        pathname: path.join(__dirname, 'pages/index.html'),
        protocol: 'file:',
        slashes: true
    }))

    if (debug) {
        window.webContents.openDevTools()
    }

    window.on('closed', () => {
        window = null
    })

    window.on('close', (event) => {
        event.sender.hide()
        event.preventDefault()
        return false
    })

    window.on('page-title-updated', function(event, title) {
        event.preventDefault()
        if (title != '') {
            this.setTitle(`${WIN_TITLE} - ${title}`)
        }
    })

    window.webContents.on('crashed', () => {
        const dialogOptions = {
            type: 'info',
            buttons: ['重新加载(&R)', '退出程序(&X)'],
            defaultId: 1,
            cancelId: 1,
            noLink: true,
            title: '信息',
            normalizeAccessKeys: true,
            message: '程序遇到崩溃。'
        }
        dialog.showMessageBox(dialogOptions, (result) => {
            if (result == 0) window.reload()
            else app.quit()
        })
    })
}


function createTray() {
    let showOrHideWindow = () => {
        let window = getWindow()
        window.isVisible() ? window.hide() : window.show()
    }

    tray = new Tray(WIN_ICON)
    tray.setToolTip(WIN_TITLE)
    tray.setContextMenu(Menu.buildFromTemplate([{
            label: '显示/隐藏窗口(&H)',
            click: showOrHideWindow
        },
        { type: 'separator' },
        {
            label: '开始(&S)',
            click() {}
        },
        {
            label: '停止(&T)',
            click() {}
        },
        { type: 'separator' },
        {
            label: '退出(&X)',
            click() {
                const dialogOptions = {
                    type: 'question',
                    buttons: ['是(&Y)', '否(&N)'],
                    defaultId: 1,
                    cancelId: 1,
                    noLink: true,
                    title: '确认',
                    normalizeAccessKeys: true,
                    message: '是否退出程序？'
                }
                dialog.showMessageBox(dialogOptions, (result) => {
                    if (result == 0) {
                        try {
                            window.destroy()
                            app.quit()
                        } catch (e) {}
                    }
                })

            }
        }
    ]))
    tray.on('double-click', showOrHideWindow)
}


/**
 * 
 * @param {boolean} hidden
 */
function registerWindow(hidden = false) {
    if (app.isReady()) {
        return
    }

    app.on('ready', () => {
        createTray()
        if (!hidden) {
            createWindow()
        }
    })

    app.on('activate', () => {
        if (window === null) {
            createWindow()
        }
    })
}

function getWindow() {
    if (!window || window.isDestroyed()) {
        createWindow()
    }
    return window
}

exports.registerWindow = registerWindow
exports.getWindow = getWindow
exports.isWindowCreated = () => { return !isNullOrUndefined(window) }