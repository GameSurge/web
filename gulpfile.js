/* eslint-env node */
/* eslint-disable no-console */

'use strict';

var fs = require('fs');
var path = require('path');

var cleanCSS = require('gulp-clean-css');
var gulp = require('gulp');
var gulpif = require('gulp-if');
var rework = require('gulp-rework');
var sass = require('gulp-sass');
var uglify = require('gulp-uglify');

var STATIC_BASE = 'gsweb/static/';
var BOOTSTRAP_BASE = 'node_modules/bootstrap/dist/';
var MINIFY = process.env.GSWEB_MINIFY === '1';


if (!process.env.GSWEB_ASSETS_FOLDER) {
    console.error('GSWEB_ASSETS_FOLDER is not defined.');
    console.error('Use `flask gulp` instead of running gulp directly.');
    process.exit(1);
}


function verboseWatcher(watcher) {
    watcher.on('change', function(evt) {
        var relPath = path.relative('.', evt.path);
        console.log('File %s was %s', relPath, evt.type);
    });
}

function reworkCSSURLs(style) {
    style.rules.forEach(function(rule) {
        if (!rule.declarations) {
            return;
        }
        rule.declarations.filter(function(decl) {
            return ~decl.value.indexOf('url(');
        }).forEach(function(decl) {
            if (decl.type === 'comment') {
                return;
            }
            // we keep the regex simple and ignore the odd chance that someone might
            // have escaped quotes in a path.  this shouldn't happen anyway!
            decl.value = decl.value.replace(/url\(\s*(["']?)(?!data:)([^"')]+)\1\s*\)/, function(match, quote, url) {
                if (~url.indexOf('://') || url.indexOf('//') === 0) {
                    // absolute or protocol-relative url
                    return;
                }
                // rewrite relative URLs to work with versioned assets
                var fsPath = path.join(path.dirname(decl.position.source), url);
                try {
                    var version = (fs.statSync(fsPath).mtime.getTime() / 1000).toFixed();
                } catch (exc) {
                    console.error('Could not get mtime for %s (url: %s)', fsPath, url);
                    return match;
                }
                url = '../../v' + version + '/' + path.relative(STATIC_BASE, fsPath);
                return "url('" + url + "')";
            });
        });
    });
}


gulp.task('bootstrap-css', function() {
    return gulp.src(BOOTSTRAP_BASE + 'css/bootstrap-flex.css')
        .pipe(gulpif(MINIFY, cleanCSS({sourceMap: false})))
        .pipe(gulp.dest(process.env.GSWEB_ASSETS_FOLDER));
});


gulp.task('bootstrap-js', function() {
    return gulp.src(BOOTSTRAP_BASE + 'js/bootstrap.js')
        .pipe(gulpif(MINIFY, uglify()))
        .pipe(gulp.dest(process.env.GSWEB_ASSETS_FOLDER));
});


gulp.task('scss', function() {
    return gulp.src(STATIC_BASE + 'css/gsweb.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(rework(reworkCSSURLs))
        .pipe(gulpif(MINIFY, cleanCSS({sourceMap: false})))
        .pipe(gulp.dest(process.env.GSWEB_ASSETS_FOLDER));
});


gulp.task('js', function() {
    return gulp.src(STATIC_BASE + 'js/gsweb.js')
        .pipe(gulpif(MINIFY, uglify()))
        .pipe(gulp.dest(process.env.GSWEB_ASSETS_FOLDER));
});


gulp.task('watch', function() {
    verboseWatcher(gulp.watch(STATIC_BASE + 'css/**/*.scss', ['scss']));
    verboseWatcher(gulp.watch(STATIC_BASE + 'js/**/*.js', ['js']));
});
