dk() {
    time sh dk2/dockerdev.sh "$@"
}

dkm() {
    dk -P settings_myjobs manage "$@"
}

dkr() {
    dk -P settings_myjobs:. dorun "$@"
}

dkg() {
    dk doruncd gulp "$@"
}

dkgg() {
    dkg nodejs node_modules/.bin/gulp "$@"
}

