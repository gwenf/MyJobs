export function promiseTest(t) {
    return (done) => t().then(done).catch(done.fail);
}
