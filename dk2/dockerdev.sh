set -e
# set -x

cd "$(dirname $0)"

while getopts "p:P:e:" opt; do
    case $opt in
    p)
        port="$OPTARG"
        ;;
    P)
        pythonpath="$OPTARG"
        ;;
    e)
        dockerenvarg="-e $OPTARG $dockerenvarg"
        ;;
    esac
done
shift $(($OPTIND - 1))

if [ -n "$port" ]; then
    portarg="-p $port:$port"
fi

if [ -n "$pythonpath" ]; then
    pythonpatharg="-e PYTHONPATH=$pythonpath"
fi

dev_path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
dev_path=/MyJobs/gulp/node_modules/.bin:$dev_path

init() {
    initsolrdata
    initmysqldata
    initrevproxycerts
}

initsolrdata() {
    docker build -t darrint/solrdata solrdata
    docker create --name solrdata darrint/solrdata true
}

initmysqldata() {
    docker build -t darrint/mysqldata mysqldata
    docker create --name mysqldata darrint/mysqldata true
}

initrevproxycerts() {
    keydir=revproxy/certs
    mkdir -p $keydir
    for vhost in "jobs" secure.my.jobs; do
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -subj "/C=us/CN=$vhost" \
            -keyout $keydir/$vhost.key -out $keydir/$vhost.crt
    done
}


debugargs() {
    echo "$port $portarg $pythonpath $pythonpatharg ||| $@"
}

pull() {
    docker pull mysql:5.5
    docker pull ubuntu:14.04
    docker pull ubuntu:15.10
    docker pull jwilder/nginx-proxy
}

background() {
    docker build \
        -t darrint/solr \
        solr
    docker build \
         -t darrint/revproxy \
         nginx-proxy
    docker run \
        --name solr \
        -d \
        --volumes-from solrdata \
        -p 8983:8983 \
        darrint/solr
    docker run \
        --name mysql \
        -d \
        -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
        --volumes-from mysqldata \
        --expose=3306 \
        -p 3306:3306 \
        mysql:5.5
    docker run \
        --name revproxy \
        -d \
        -p 80:80 -p 443:443 \
        -v $(pwd)/revproxy/certs:/etc/nginx/certs \
        -v /var/run/docker.sock:/tmp/docker.sock:ro \
        darrint/revproxy
}

backgroundstop() {
    docker stop mysql || true
    docker stop solr || true
    docker stop revproxy || true
    docker rm mysql || true
    docker rm solr || true
    docker rm revproxy || true
}

restartsecure() {
    docker stop secure.my.jobs || true
    docker rm secure.my.jobs || true
    runsecure || true
}

restartmicrosites() {
    docker stop star.jobs || true
    docker rm star.jobs || true
    runmicrosites || true
}

maint() {
    docker run \
        --rm \
        --net=host \
        --volumes-from solrdata \
        --volumes-from mysqldata \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        -w=/MyJobs \
        -it \
        "$1" \
        /bin/bash
}

rebuilddev() {
    cp -p ../requirements.txt dev
    time docker build -t darrint/dev dev
}

doruncd() {
    dir="$1"
    shift
    docker run \
        --net=host \
        --rm \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        $portarg \
        $pythonpatharg \
        $dockerenvarg \
        -w /MyJobs/"$dir" \
        -e PATH="$dev_path" \
        -e npm_config_unsafe_perm=1 \
        -i -t \
        darrint/dev "$@"
}

dorun() {
    doruncd . "$@"
}

manage() {
    dorun python manage.py "$@"
}

runserver() {
    virthost="$1"
    docker run \
        --name $(echo $virthost | sed 's/*/star/g') \
        --link solr \
        --link mysql \
        --expose=80 \
        --rm \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        $pythonpatharg \
        $dockerenvarg \
        -e VIRTUAL_HOST="$virthost" \
        -w /MyJobs \
        -i -t \
        darrint/dev \
        python manage.py runserver 0.0.0.0:80
}

runmicrosites() {
    pythonpatharg="-e PYTHONPATH=settings_dseo" \
        dockerenvarg="-e NO_HTTPS_REDIRECT=1 $dockerenvarg" \
        runserver "*.jobs"
}

runsecure() {
    pythonpatharg="-e PYTHONPATH=settings_myjobs" \
        runserver "secure.my.jobs"
}

"$@"
