import requests

class OllamaLLM:
    """
    Minimal wrapper for interacting with a local Ollama model.
    Default host: http://localhost:11434
    """

    def __init__(self, model="llama3.1", host="http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def chat(self, system: str, user: str) -> str:
        url = f"{self.host}/api/generate"
        prompt = f"<|system|>\n{system}\n<|user|>\n{user}\n<|assistant|>\n"
        resp = requests.post(
            url,
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
