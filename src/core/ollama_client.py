import requests

OLLAMA_CLOUD_URL = "https://ollama.com"

VISION_KEYWORDS = ["llava", "cogvlm", "minicpm", "moondream", "fuyu", "vision",
                   "nanollava", "phi3", "pixtral", "vl", "multimodal", "gemma"]
AUDIO_KEYWORDS = ["whisper"]


class OllamaClient:
    def __init__(self, api_key=None, base_url=OLLAMA_CLOUD_URL):
        self.api_key = api_key or ""
        self.base_url = base_url.rstrip("/")
        self._models_cache = None

    def set_api_key(self, key):
        self.api_key = key
        self._models_cache = None

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def verify(self):
        if not self.api_key:
            return False, "API Key vacía"
        try:
            resp = requests.get(f"{self.base_url}/api/tags", headers=self._headers(), timeout=10)
            if resp.status_code == 200:
                return True, "Conexión exitosa"
            elif resp.status_code == 401:
                return False, "API Key inválida"
            else:
                return False, f"Error {resp.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar al servidor"
        except requests.exceptions.Timeout:
            return False, "Tiempo de espera agotado"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def list_models(self, force=False):
        if self._models_cache and not force:
            return self._models_cache
        try:
            resp = requests.get(f"{self.base_url}/api/tags", headers=self._headers(), timeout=10)
            if resp.status_code != 200:
                return []
            data = resp.json()
            models = []
            raw = data.get("models", [])
            for item in raw:
                mid = item.get("name", "")
                if not mid:
                    continue
                mid_lower = mid.lower()
                models.append({
                    "id": mid,
                    "has_vision": any(v in mid_lower for v in VISION_KEYWORDS),
                    "has_audio": any(a in mid_lower for a in AUDIO_KEYWORDS),
                })
            self._models_cache = models
            return models
        except Exception:
            return []

    def get_model_info(self, model_id):
        models = self.list_models()
        for m in models:
            if m["id"] == model_id:
                return m
        return {"id": model_id, "has_vision": False, "has_audio": False}

    def chat(self, model, messages, temperature=0.7, stream=False):
        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                headers=self._headers(),
                json=body,
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("message", {}).get("content", "")
                return True, content
            else:
                return False, f"Error {resp.status_code}: {resp.text}"
        except Exception as e:
            return False, f"Error: {str(e)}"
