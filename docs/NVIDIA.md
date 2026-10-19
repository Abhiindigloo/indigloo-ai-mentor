# NVIDIA integration

The NVIDIA skill finder was used to inspect the live skill catalog. The app integrates the documented OpenAI-compatible NIM chat-completions interface. No NVIDIA service has been provisioned, no key is embedded, and no remote inference benchmark is claimed.

Set these **server-side** environment variables after choosing a deployed NIM model:

```dotenv
MODEL_BASE_URL=https://integrate.api.nvidia.com/v1
MODEL_NAME=your-accessible-model-id
MODEL_API_KEY=your-secret-from-your-secret-manager
```

For a privately deployed NIM, use its base URL ending in `/v1` and its authentication configuration. Do not assume the Hugging Face LoRA adapter can be loaded by every NIM; architecture/adapter support must be checked for the selected serving stack. A separate OpenAI-compatible Hugging Face dedicated endpoint can be used with the same API adapter.

The Android phone does not require an NVIDIA GPU. NVIDIA acceleration belongs on the server/training machine. This MVP's local tutor runs authored sample responses without an LLM.

Official references:
- https://github.com/NVIDIA/skills/tree/main/skills
- https://docs.nvidia.com/nim/large-language-models/latest/function-calling.html
- https://docs.api.nvidia.com/nim/reference/llm-apis
