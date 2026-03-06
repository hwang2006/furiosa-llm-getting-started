# Model Fit Matrix: NPU PE Count vs. Tensor Parallelism

## Check Available PEs
```bash
furiosa-smi status   # list NPU devices and PE count
furiosa-smi ps       # show processes currently holding PEs
```

## Rule: TP ≤ Available PEs
| Available PEs | Valid TP values |
|--------------|-----------------|
| 8 | 1, 2, 4, 8 |
| 4 | 1, 2, 4 |
| 2 | 1, 2 |
| 1 | 1 |

## Model Fit Table

| Model | Params | Default TP | Min PEs | HF License |
|-------|--------|-----------|---------|------------|
| furiosa-ai/Qwen2.5-0.5B-Instruct | 0.5B | 1 | 1 | No |
| furiosa-ai/Qwen2.5-1.5B-Instruct | 1.5B | 1 | 1 | No |
| furiosa-ai/Qwen2.5-7B-Instruct   | 7B   | 4 | 4 | No |
| furiosa-ai/Qwen3-32B-FP8         | 32B  | 8 | 8 | No |
| furiosa-ai/Llama-3.2-1B-Instruct | 1B   | 1 | 1 | Yes |
| furiosa-ai/Llama-3.2-3B-Instruct | 3B   | 2 | 2 | Yes |
| furiosa-ai/Llama-3.1-8B-Instruct | 8B   | 8 | 8 | Yes |

> Default TP may vary between SDK releases. Verify with `furiosa-llm info <model>`.

## Custom TP Build
```bash
furiosa-llm build \
    --model furiosa-ai/Llama-3.1-8B-Instruct \
    --tensor-parallel-size 4 \
    --output-dir ./artifacts/llama-3.1-8b-tp4

furiosa-llm serve ./artifacts/llama-3.1-8b-tp4
```

## Multi-NPU
2 × RNGD (8 PEs each) = 16 total PEs → supports TP up to 16.
```bash
furiosa-llm serve furiosa-ai/Qwen3-32B-FP8 --tensor-parallel-size 16
```
