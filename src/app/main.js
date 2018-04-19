const path = require('path')
const { ArgumentParser } = require('argparse')
const { app, dialog } = require('electron')
const { registerWindow, getWindow } = require('./window')
const { package } = require('./shared')


/**
 * 等待退出程序超时
 */
const WAITE_QUIT_TIMEOUT = 1000

function main(argv) {
    let argsParser = ArgumentParser({
        version: package.version,
        description: package.description,
        addHelp: true
    })
    argsParser.addArgument(
        ['-d', '--debug'], {
            action: 'storeTrue',
            help: 'Debug Mode',
            defaultValue: false,
            required: false
        }
    );
    argsParser.addArgument(
        ['-i', '--hidden'], {
            action: 'storeTrue',
            help: 'Hide application window',
            defaultValue: false,
            required: false
        }
    );
    let args = argsParser.parseArgs()

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

    if (args.debug) {
        process.env.DEBUG = '1'
    }

    registerWindow(args.hidden)

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
}


if (path.resolve(process.argv[1]) === __filename) {
    main(process.argv)
}