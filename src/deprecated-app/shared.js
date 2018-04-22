const { isObject, _extend } = require('util')

/**
 * 存放 main 主进程和 render 进程共用的数据和服务
 */

global.shared = {
    $: {},

    package: require('./package.json'),

    registerShared (name, value) {
        let _this = shared
        if (isObject(name)) {
            _this.$ = _extend(_this.$, name)
        } else {
            _this.$[name] = value
        }
    },

    unregisterShared(name) {
        let _this = shared
        delete _this.$[name]
    }
}

module.exports = global.shared