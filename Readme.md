
# Build

    cd docker
    docker build -t gluedev . 

# Run

    docker run -it --rm --name gluedev -p 8080:8080 -p 7077:7077 -p 9001:9001 -v $PWD/logs:/logs -v $PWD/notebook:/notebook -e ZEPPELIN_LOG_DIR='/logs' -e ZEPPELIN_NOTEBOOK_DIR='/notebook' -v /Users/alain/.aws:/root/.aws:ro gluedev



