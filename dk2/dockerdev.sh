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
    initsolrdata53
    initmysqldata55
    initrevproxycerts
    initnet
}

initsolrdata53() {
    docker build -t solrdata53 solrdata53
    docker create --name solrdata53 solrdata53 true
}

initmysqldata55() {
    docker build -t mysqldata55 mysqldata55
    docker create --name mysqldata55 mysqldata55 true
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

initnet() {
  docker network create myjobs
}


debugargs() {
    echo "$port $portarg $pythonpath $pythonpatharg ||| $@"
}

pull() {
    docker pull mysql:5.5
    docker pull ubuntu:trusty
    docker pull solr:5.3.1
    docker pull nginx:stable
}

background() {
    docker build \
         -t myjobsdev/revproxy \
         nginx-proxy
    docker run \
        --net=myjobs \
        --name solr53 \
        -d \
        --volumes-from solrdata53 \
        -p 8983:8983 \
        solr:5.3.1
    docker run \
        --net=myjobs \
        --name mysql55 \
        -d \
        -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
        --volumes-from mysqldata55 \
        --expose=3306 \
        -p 3306:3306 \
        mysql:5.5
    docker run \
        --net=myjobs \
        --name revproxy-simple \
        -d \
        -p 80:80 -p 443:443 \
        -v $(pwd)/revproxy/certs:/etc/nginx/certs \
        -v /var/run/docker.sock:/tmp/docker.sock:ro \
        myjobsdev/revproxy
}

backgroundstop() {
    docker stop mysql55 || true
    docker stop solr53 || true
    docker stop revproxy-simple || true
    docker rm mysql55 || true
    docker rm solr53 || true
    docker rm revproxy-simple || true
}

bgrst() {
    backgroundstop || true
    background || true
}

restartsecure() {
    docker stop django-secure || true
    docker rm django-secure || true
    runsecure || true
}

restartmicrosites() {
    docker stop django-microsites || true
    docker rm django-microsites || true
    runmicrosites || true
}

maint() {
    docker run \
        --rm \
        --net=myjobs \
        --volumes-from solrdata53 \
        --volumes-from mysqldata55 \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        -w=/MyJobs \
        -it \
        "$1" \
        /bin/bash
}

rebuilddev() {
    cp -p ../requirements.txt dev
    time docker build -t myjobsdev/dev dev
}

doruncd() {
    dir="$1"
    shift
    docker run \
        --net=myjobs \
        --rm \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        $portarg \
        $pythonpatharg \
        $dockerenvarg \
        --user $(id -u):$(id -g) \
        -w /MyJobs/"$dir" \
        -e PATH="$dev_path" \
        -e npm_config_unsafe_perm=1 \
        -i -t \
        myjobsdev/dev "$@"
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
        --net=myjobs \
        --name $virthost \
        --expose=8000 \
        --rm \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        $pythonpatharg \
        $dockerenvarg \
        --user $(id -u):$(id -g) \
        -w /MyJobs \
        -i -t \
        myjobsdev/dev \
        python manage.py runserver 0.0.0.0:8000
}

runmicrosites() {
    pythonpatharg="-e PYTHONPATH=settings_dseo" \
        runserver "django-microsites"
}

runsecure() {
    pythonpatharg="-e PYTHONPATH=settings_myjobs" \
        runserver "django-secure"
}

rundevserver() {
    docker run \
        --net=myjobs \
        --name webpack-devserver \
        --rm \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        $pythonpatharg \
        $dockerenvarg \
        --user $(id -u):$(id -g) \
        -p 8080:8080 \
        -w /MyJobs/gulp \
        -i -t \
        myjobsdev/dev \
        npm run devserver
}

"$@"
