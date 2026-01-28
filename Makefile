install:
    pip install -e .
test:
    gatekeeper submissions/*.py --gate
docker:
    docker build -t gatekeeper .
