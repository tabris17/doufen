/**
 * 主进程代码入口
 */
const path = require('path')
const { ArgumentParser } = require('argparse')
const { app, dialog } = require('electron')
const { registerWindow, getWindow } = require('./window')
const { package, registerShared } = require('./shared')



const WAITE_QUIT_TIMEOUT = 1000
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
        ['-n', '--hidden'], {
            action: 'storeTrue',
            help: 'Hide window when the application startup.',
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
 * 注册服务
 */
function registerSharedServices() {
    registerShared({
        // 新增登录授权
        'service.authorization.add': (s) => { console.log(s) },
        // 移除登录授权（仅移除）
        'service.authorization.remove': '',
        // 所有登录收取列表
        'service.authorization.all': '',
        // 删除并注销登录授权（授权不再可用）
        'service.authorization.destroy': '',

        // 新增代理服务器
        'service.proxy.add': '',
        // 移除代理服务器
        'service.proxy.remove': '',
        // 所有代理服务器列表
        'service.proxy.all': '',

        // 获取配置
        'service.settings.get': '',
        // 写入配置
        'service.settings.set': '',

        // 服务运行状态查询
        'service.status.query': '',
        // 服务心跳检测
        'service.status.helo': '',

        // 启动工作进程
        'service.worker.start': '',
        // 停止工作进程
        'service.worker.stop': '',
        // 暂停工作进程
        'service.worker.pause': '',
        // 恢复工作进程
        'service.worker.continue': '',
        // 所有工作进程列表
        'service.worker.all': ''
    })
}

/**
 * 程序入口主函数
 * 
 * @param {Array} args 
 */
function main(args) {
    let parsedArgs = parseArgs(args)

    const isDuplicateInstance = app.makeSingleInstance((commandLine, workingDirectory) => {
        let window = getWindow()
        if (window) {
            if (window.isMinimized()) window.restore()
            window.focus()
        }
    })
    if (isDuplicateInstance) {
        app.quit()
    }

    if (parsedArgs.debug) {
        process.env.DEBUG = '1'
    }

    registerWindow(parsedArgs.hidden)

    app.on('all-window-closed', () => {
        if (process.platform !== 'darwin') {
            app.quit()
        }
    })

    let isReadyToQuit
    app.on('will-quit', (event) => {
        if (isReadyToQuit) {
            return
        }
        event.preventDefault()
        if (isReadyToQuit === false) {
            return
        } else {
            isReadyToQuit = false
        }

        // 收尾工作

        setTimeout(() => {
            let dialogResult = dialog.showMessageBox({
                type: 'warning',
                buttons: ['立即结束', '继续等待'],
                defaultId: 1,
                cancelId: 1,
                noLink: true,
                title: '提示',
                normalizeAccessKeys: true,
                message: '程序响应超时。是否强制退出？'
            })
            if (dialogResult == 0) {
                isReadyToQuit = true
                app.quit()
            }
        }, WAITE_QUIT_TIMEOUT)
    })

    registerSharedServices()
}


if (path.resolve(process.argv[1]) === __filename) {
    main(process.argv.slice(2))
}