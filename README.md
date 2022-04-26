# Buffalo Interface

The Buffalo Interface is a unified interface for running machine learning models, designed to allow blockchain integration with machine learning. Specifically, it defines a set of tasks grouped together by API, i.e. the format of the inputs and outputs. Each API supports community implementation of arbitrary models that follow the input/output interface.

In addition to hosting the model repository, this codebase also includes a celery scheduling system for calling the supported ML APIs. This system is made up of two parts, the Sequencer and the Worker.

## Model Repository

## Sequencer

The Sequencer listens to contract events from the on-chain Oracle contract via a subgraph and distributes jobs that need to be run to workers. 

### Subgraph

The subgraph is located at `sequencer/chainai-notifier`. It listens to `JobCreated` events from the Oracle contract and returns information about each job. The subgraph is deployed at https://thegraph.com/studio/subgraph/chainai-notifier/. TheGraph has very good documentation on how to setup and deploy subgraphs. Roughly, the steps are:

1. Authenticate:
```
graph auth --studio $GRAPH_DEPLOY_KEY
```

2. Build:
```
graph codegen && graph build
```

3. Deploy:
```
graph deploy --studio chainai-notifier
```

When you deploy you will need to select a version, and the combination of the subgraph and version defines a unique URL for the REST API that can be queried.

### Job Management

The celery listener that queries the subgraph and distributes jobs is at `sequencer/off_chain_sequencer/listener.py`. The listener uses a redis backend and an RabbitMQ message broker to send messages to workers, managed with celery. 

#### Redis Setup

To setup redis, follow https://redis.io/docs/getting-started/installation/install-redis-on-linux/.

#### RabbitMQ Setup

To setup RabbitMQ, follow https://www.rabbitmq.com/download.html.

#### Running the listener

Delete Redis cache and reset listener:
```
cd sequencer/off_chain_sequencer/
python listener.py
```

Run listener:
```
celery -A listener worker -B -n listener --concurrency=1
```

The listener currently runs with concurrency 1 to avoid race conditions. It uses celery beat to schedule a graph query every 30 seconds.

## Worker

