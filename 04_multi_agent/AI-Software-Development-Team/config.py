import json
import time

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)


def invoke_with_retry(invoke, attempts: int = 3):
    last_error = None
    for attempt in range(attempts):
        try:
            return invoke()
        except Exception as error:
            last_error = error
            if attempt < attempts - 1:
                is_rate_limit = "RateLimit" in type(error).__name__ or "429" in str(error)
                time.sleep(10 * (attempt + 1) if is_rate_limit else 2**attempt)
    raise RuntimeError(f"Model call failed after {attempts} attempts") from last_error


def structured_invoke(schema, prompt):
    model = llm.with_structured_output(schema, method="json_mode")
    schema_text = json.dumps(schema.model_json_schema(), indent=2)
    structured_prompt = f"""{prompt}

Return only valid JSON matching this schema:
{schema_text}
"""
    try:
        return invoke_with_retry(lambda: model.invoke(structured_prompt))
    except RuntimeError:
        raw_prompt = f"""{prompt}

Return only one valid JSON object matching this schema. Do not use markdown
fences or explanatory text:
{schema_text}
"""
        raw_response = invoke_with_retry(lambda: llm.invoke(raw_prompt))
        content = raw_response.content.strip()
        if content.startswith("```"):
            content = content.removeprefix("```").removeprefix("json").strip()
            content = content.removesuffix("```").strip()
        start = content.find("{")
        end = content.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("Model fallback did not return a JSON object")
        return schema.model_validate(json.loads(content[start : end + 1]))