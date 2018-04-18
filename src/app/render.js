/**
 * used by index.html
 */

(function(global) {
    const { shell, remote } = require('electron')

    let templates = {}
    global.document.querySelectorAll('link[rel="import"]').forEach((link) => {
        let name = link.attributes.href.nodeValue
        let template = link.import.querySelector('template.page')
        templates[name] = global.document.importNode(template.content, true)
    })

    global.system = {
        require: global.require,
        exports: global.exports,
        module: global.module,

        openLink(url, options, callback) {
            return shell.openExternal(url, options, callback)
        },

        navigate(name, container) {
            let template = templates[name]
            if (!template) {
                return false
            }
            let parentNode = global.document.querySelector('#' + container)
            parentNode.innerHTML = ''
            let templateNode = global.document.importNode(template, true)
            parentNode.appendChild(templateNode)
            return true
        },

        shared(name) {
            return remote.getGlobal('shared')[name]
        }
    }

    delete global.require
    delete global.exports
    delete global.module

})(window)