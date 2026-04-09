
'use strict'

if (process.env.NODE_ENV === 'production') {
  module.exports = require('./integral-sdk.cjs.production.min.js')
} else {
  module.exports = require('./integral-sdk.cjs.development.js')
}
