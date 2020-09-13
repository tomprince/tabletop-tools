const files = {};
export function readFileSync(filename, encoding) {
    return files[filename];
}
export function writeFileSync(filename, content) {
    files[filename] = content;
}
export function existsSync(filename) {
    return filename in files;
}
export function lstatSync(filename) {
    return {
        isFile: () => existsSync(filename),
    };
}
