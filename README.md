# Buffalo Interface

The Buffalo Interface is a unified interface for running machine learning models, designed to allow blockchain integration with machine learning. Specifically, it defines a set of tasks grouped together by API, i.e. the format of the inputs and outputs. Each API supports community implementation of arbitrary models that follow the input/output interface.

In addition to hosting the model repository, this codebase also includes a celery scheduling system for calling the supported ML APIs. This system is made up of two parts, the Sequencer and the Worker.

## Setup

Create a conda environment:
```
conda create --name buffalo python=3.8
```

Inside the conda environment install pytorch: https://pytorch.org/get-started/locally/

E.g.
```
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
```

Install requirements:
```
pip install -r requirements.txt
```

#### Required environment variables:

`RINKEBY_HTTP_PROVIDER` - blockchain node URL

`CHAINAI_ADDRESS` - Address of ChainAI Oracle contract

`RINKEBY_PRIVATE_KEY` - Hex digest (prefixed with 0x) private key for the account calling blockchain functions

#### Required key files:

Currently, a Solana account is used to fund the bundlr uploads. The private key for the account will be automatically generated at `keys/private_key.sol` and `keys/public_key.sol` if a key does not exist, but you will need to manually transfer funds to the Solana account. Bundlr maintains a separate funding account, this code handles automatically funding the bundlr account from the generated solana account as needed for uploads so the only thing you need to do is make sure the generated solana account remains funded.

## Model Repository

The model repository code is located at `buffalo_models/`. Each interface has its own subdirectory (e.g. `TextConditionalImageGeneration`), and each architecture that implements the interface is located within that subdirectory (e.g. `TextConditionalImageGeneration/CLIPGuidedDiffusion.py`).

To load models by their name, each interface should list the implemented architectures in their respective `__init__.py` file, for example:

`TextConditionalImageGeneration/__init__.py`
```
from .CLIPGuidedDiffusion import CLIPGuidedDiffusion

architectures = [
    CLIPGuidedDiffusion
]
```

Then the architectures should be loaded for each interface in the top-level `__init__.py`, for example:

`__init__.py`
```
from .TextConditionalImageGeneration \
        import architectures as TextConditionalImageGeneration_architectures

architecture_index = [
    TextConditionalImageGeneration_architectures
]
```

Each interface should be defined by subclassing `ModelClass`, defining the inputs and outputs of a `run` function, and setting the class variables `input_data_type`, and `output_data_type`. Data type classes are defined in `interface.py`. 

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

The celery listener that queries the subgraph and distributes jobs is at `sequencer/off_chain_sequencer/listener.py`. The listener uses a redis backend and an RabbitMQ message broker to send messages to workers, managed with celery. The listener puts jobs in the worker queue as needed, and workers pull from the queue. The worker jobs are linked to a follow-up job on success and an error job, one of which is performed by the listener after the job ends depending on the status.

To setup redis, follow https://redis.io/docs/getting-started/installation/install-redis-on-linux/.

To setup RabbitMQ, follow https://www.rabbitmq.com/download.html.

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

The worker listens for `run_inference` jobs, builds the correct model from the config file, and runs inference. It acts as a wrapper around the model and utility functions defined in the model repository.

Run workers:
```
celery -A worker_celery worker --loglevel=INFO -Q inference -P solo --concurrency=1 -n gpu_worker
```

The worker also runs with concurrency 1 to avoid overloading one GPU. Currently, to use multiple GPUs, you will need multiple workers each with concurrency 1.

