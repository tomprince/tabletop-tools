var files = {};
export function readFileSync(filename, encoding) {
    return files[filename];
}
export function existsSync(filename) {
    return filename in files;
}
export function lstatSync(filename) {
    return {
        isFile: () => existsSync(filename),
    };
}

export function writeFiles(new_files) {
    files = new_files;
}
