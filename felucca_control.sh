#!/bin/bash
SERVICE_NAME=felucca
FRONTEND_PATH_NAME=/tmp/Felucca/frontend-pid
BACKEND_PATH_NAME=/tmp/Felucca/backend-pid
DOC_PATH_NAME=/tmp/Felucca/doc-server-pid
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

case $1 in
    start)
        echo "Starting $SERVICE_NAME ..."
        echo "Starting backend ..."
        if [ ! -f $BACKEND_PATH_NAME ]; then
            . /tmp/Felucca/env/venv/bin/activate &&
            cd $DIR/felucca/backend &&
            nohup python3 server.py >> backend.out 2>&1 &
            echo $! > $BACKEND_PATH_NAME
            echo "$SERVICE_NAME backend started ..."
        else
            echo "$SERVICE_NAME backend is already running ..."
        fi

        echo "Starting frontend ..."
        if [ ! -f $FRONTEND_PATH_NAME ]; then
            cd $DIR/felucca/frontend &&
            nohup ng serve --host=0.0.0.0 --configuration=production --disable-host-check >> frontend.out 2>&1  &
            echo $! > $FRONTEND_PATH_NAME
            echo "$SERVICE_NAME frontend started ..."
        else
            echo "$SERVICE_NAME frontend is already running ..."
        fi

    ;;
    stop)
        if [ -f $BACKEND_PATH_NAME ]; then
            PID=$(cat $BACKEND_PATH_NAME);
            echo "$SERVICE_NAME backend stoping ..."
            echo "killing $PID"
            kill $PID
            echo "$SERVICE_NAME backend stopped ..."
            echo "$BACKEND_PATH_NAME"
            rm -f $BACKEND_PATH_NAME
        else
            echo "$SERVICE_NAME backend is not running ..."
        fi

        if [ -f $FRONTEND_PATH_NAME ]; then
            PID=$(cat $FRONTEND_PATH_NAME);
            echo "$SERVICE_NAME frontend stoping ..."
            echo "killing $PID"
            kill $PID
            echo "$SERVICE_NAME frontend stopped ..."
            echo "$FRONTEND_PATH_NAME"
            rm -f $FRONTEND_PATH_NAME
        else
            echo "$SERVICE_NAME frontend is not running ..."
        fi

        if [ -f $DOC_PATH_NAME ]; then
            PID=$(cat $DOC_PATH_NAME);
            echo "$SERVICE_NAME doc server stoping ..."
            echo "killing $PID"
            kill $PID
            echo "$SERVICE_NAME doc server stopped ..."
            echo "$DOC_PATH_NAME"
            rm -f $DOC_PATH_NAME
        else
            echo "$SERVICE_NAME doc server is not running ..."
        fi
    ;;
esac
