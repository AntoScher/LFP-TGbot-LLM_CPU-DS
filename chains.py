import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline
)
# Импорты для Intel Extension for Transformers
try:
    from intel_extension_for_transformers.transformers import (
        AutoModelForCausalLM as AutoModelForCausalLM_ITREX
    )
    from intel_extension_for_transformers.transformers.llm.quantization.quantization_config import (
        QuantizationConfig,
        RtnConfig
    )
    from intel_extension_for_transformers.transformers.llm.quantization.utils import (
        convert_dtype_str2torch,
        convert_dtype_torch2str,
    )
    ITREX_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Intel Extension for Transformers not available: {e}")
    ITREX_AVAILABLE = False

# Импорт OpenVINO backend (опционально)
try:
    from optimum.intel.openvino import OVModelForCausalLM
    OPENVINO_AVAILABLE = True
except Exception as e:
    print(f"OpenVINO backend not available: {e}")
    OPENVINO_AVAILABLE = False

from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import logging

# Глобальные переменные для кэширования
_llm_pipe = None
_qa_chain = None

# Проверка доступности Intel XPU
XPU_AVAILABLE = hasattr(torch, 'xpu') and torch.xpu.is_available()
if XPU_AVAILABLE:
    print(f"XPU is available: {torch.xpu.get_device_name(0)}")
else:
    print("XPU is not available, falling back to CPU")

# Глобальные переменные для кэширования
_llm_pipe = None
_system_prompt = None


def load_system_prompt(path: str = "system_prompt.txt") -> str:
    global _system_prompt
    if _system_prompt is None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                _system_prompt = f.read().strip()
        except Exception as e:
            logging.error(f"Error loading system prompt: {e}")
            _system_prompt = "Ты — ассистент отдела продаж. Отвечай на вопросы клиентов."
    return _system_prompt


def init_llm_pipeline():
    """Инициализация LLM пайплайна с возможностью выбора бэкенда (OpenVINO / Torch)."""
    global _llm_pipe
    if _llm_pipe is not None:
        return _llm_pipe

    model_id = os.getenv("MODEL_NAME", "Qwen/Qwen2-1.5B-Instruct")
    cache_dir = os.getenv("HF_HOME")
    backend = os.getenv("INFERENCE_BACKEND", "auto").lower()  # openvino | xpu | cpu | auto

    # Загружаем токенизатор
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        cache_dir=cache_dir,
        trust_remote_code=True
    )

    # Ветка OpenVINO
    if backend in ["openvino", "ov"] or (backend == "auto" and OPENVINO_AVAILABLE):
        if not OPENVINO_AVAILABLE:
            logging.warning("OpenVINO selected but not available. Falling back to Torch CPU.")
        else:
            ov_device = os.getenv("OPENVINO_DEVICE", "CPU")  # CPU | GPU
            logging.info(f"Loading model {model_id} with OpenVINO on {ov_device}...")
            ov_model = OVModelForCausalLM.from_pretrained(
                model_id,
                export=True,
                compile=True,
                device=ov_device,
                cache_dir=cache_dir,
                trust_remote_code=True
            )
            text_generation_pipeline = pipeline(
                task="text-generation",
                model=ov_model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                return_full_text=True,
            )
            _llm_pipe = HuggingFacePipeline(pipeline=text_generation_pipeline)
            logging.info("OpenVINO pipeline initialized")
            return _llm_pipe

    # Ветка Torch (CPU/XPU)
    device = os.getenv("DEVICE", "xpu" if XPU_AVAILABLE and ITREX_AVAILABLE else "cpu")
    try:
        if ITREX_AVAILABLE and device == "xpu":
            # Настройки квантования для Intel Arc (ITREX)
            quant_config = QuantizationConfig(
                approach="weight_only",
                op_type_dict={
                    ".*": {
                        "weight": {
                            "dtype": "int4_fullrange",
                            "bits": 4,
                            "group_size": 128,
                            "scheme": "sym",
                            "algorithm": "RTN"
                        }
                    }
                },
                recipes={
                    "rtn_args": {"enable_full_range": True, "enable_mse_search": True}
                }
            )
            print(f"Loading model {model_id} on XPU with ITREX optimizations...")
            model = AutoModelForCausalLM_ITREX.from_pretrained(
                model_id,
                quantization_config=quant_config,
                device_map="auto",
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True,
                cache_dir=cache_dir,
                trust_remote_code=True
            )
            print("Model loaded on XPU with ITREX optimizations")
        else:
            if device == "xpu":
                print("ITREX not available, falling back to standard XPU loading")
                device_map = "auto"
                torch_dtype = torch.bfloat16
            else:
                device_map = None
                torch_dtype = torch.float32
            print(f"Loading model {model_id} on {device.upper()}...")
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map=device_map,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                cache_dir=cache_dir,
                trust_remote_code=True
            )
            if device == "cpu":
                model = model.to('cpu')
                print("Model loaded on CPU")
            else:
                print("Model loaded with standard device mapping")

        text_generation_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            return_full_text=False,  # Возвращаем только новый текст
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            device_map="auto" if device == "xpu" and ITREX_AVAILABLE else None,
        )
        _llm_pipe = HuggingFacePipeline(pipeline=text_generation_pipeline)
        return _llm_pipe

    except Exception as e:
        logging.error(f"Error initializing LLM pipeline: {e}")
        raise


def init_qa_chain(retriever):
    llm_pipe = init_llm_pipeline()
    system_prompt = load_system_prompt()

    # Упрощенный промпт шаблон без дублирования системного промпта в контексте
    prompt_template = """<|im_start|>system
{system_prompt}
<|im_end|>
<|im_start|>user
{context}

Вопрос: {question}

Дай четкий и структурированный ответ на основе предоставленной информации.
<|im_end|>
<|im_start|>assistant
"""

    # Фикс: system_prompt подставляем частично на этапе сборки, чтобы не передавать его в рантайме
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
        partial_variables={"system_prompt": system_prompt}
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm_pipe,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={
            "prompt": prompt,
            "document_prompt": PromptTemplate(
                input_variables=["page_content"],
                template="{page_content}"
            ),
            "document_variable_name": "context",
            "verbose": False  # Отключаем подробный вывод для производительности
        },
        return_source_documents=False,
        input_key="question",
        output_key="result",
        verbose=False
    )

    logging.info("QA chain initialized successfully")
    logging.info(f"Input key: {qa_chain.input_key}")
    logging.info(f"Output key: {qa_chain.output_key}")

    return qa_chain