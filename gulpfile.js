var gulp = require('gulp');
var gutil = require('gulp-util');
var jshint = require('gulp-jshint');
var clean = require('gulp-clean');
var childProcess = require('child_process');
var electron = require('electron-prebuilt');
var os = require('os');
var path = require('path');

gulp.task('default', ['run']);

gulp.task('jshint-html', function() {
    return gulp.src('*.html')
        .pipe(jshint.extract('auto'))
        .pipe(jshint())
        .pipe(jshint.reporter('jshint-stylish'));
});

gulp.task('watch', function() {
    gulp.watch('*.html', ['jshint-html']);
});

gulp.task('run', function() {
    childProcess.spawn(electron, ['--debug=5858', '.'], { stdio: 'inherit'});
});

gulp.task('package', function() {
    childProcess.spawn(path.join(os.homedir(), '/node_modules/.bin/electron-packager'), [
        '.',
        '--platform=darwin', 
        '--arch=x64', 
        '--out=build', 
        '--overwrite'
        ], { stdio: 'inherit'}); 
});

gulp.task('clean', function() {
    return gulp.src('build/')
        .pipe(clean());
});