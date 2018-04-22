const { _extend } = require('util')

let shared = {}
let package = require('./package.json')
let debug = false

function debug(option) {
    debug = true
}

function registerShared(keyValuePairs) {
    shared = _extend(shared, keyValuePairs)
}

function unregisterShared(name) {
    let _this = shared
    delete _this.$[name]
}