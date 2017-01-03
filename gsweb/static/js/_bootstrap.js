'use strict';

// bootstrap isn't playing along well with browserify and checks for global
// jQuery / Tether objects so we need to provide them...
global.Tether = require('tether');
global.$ = global.jQuery = require('jquery');
require('bootstrap');
// luckily it only needs access to the jQuery global at import time, so let's
// get rid of them again...
global.$.noConflict(true);
