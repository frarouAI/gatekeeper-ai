from engines.v1 import EngineV1
from engines.v2 import EngineV2

ENGINE_REGISTRY = {
    "v1": EngineV1,
    "v2": EngineV2,
}


def get_engine(engine_name: str):
    if engine_name not in ENGINE_REGISTRY:
        raise ValueError(
            f"Unknown engine '{engine_name}'. "
            f"Available engines: {list(ENGINE_REGISTRY.keys())}"
        )

    return ENGINE_REGISTRY[engine_name]
