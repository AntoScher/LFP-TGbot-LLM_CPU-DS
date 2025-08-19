import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline
)
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import logging

# Глобальные переменные для кэширования
_llm_pipe = None
_system_prompt = None

def load_system_prompt(path: str = "knowledge_base/system_prompt.txt") -> str:
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
    """Оптимизированная инициализация LLM пайплайна для CPU."""
    global _llm_pipe
    if _llm_pipe is not None:
        return _llm_pipe

    # Оптимизированные настройки для CPU
    model_id = os.getenv("MODEL_NAME", "Qwen/Qwen2-0.5B-Instruct")
    max_length = int(os.getenv("MODEL_MAX_LENGTH", "256"))
    temperature = float(os.getenv("MODEL_TEMPERATURE", "0.5"))
    
    logging.info(f"Loading CPU-optimized model: {model_id}")
    logging.info(f"Max length: {max_length}, Temperature: {temperature}")

    # Загружаем токенизатор
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        trust_remote_code=True,
        use_fast=False  # Отключаем быстрый токенизатор для стабильности
    )

    # Оптимизированная загрузка модели для CPU
    logging.info("Loading model with CPU optimizations...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,  # Используем float32 для CPU
        low_cpu_mem_usage=True,
        trust_remote_code=True
    )
    
    # Принудительно перемещаем на CPU
    model = model.to('cpu')
    model.eval()  # Переводим в режим оценки
    
    logging.info("Model loaded successfully on CPU")

    # Оптимизированный пайплайн
    text_generation_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=max_length,
        temperature=temperature,
        top_p=0.9,
        repetition_penalty=1.1,
        return_full_text=False,  # Возвращаем только новый текст
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    
    _llm_pipe = HuggingFacePipeline(
        pipeline=text_generation_pipeline,
        model_kwargs={"temperature": temperature, "max_length": max_length}
    )
    
    logging.info("CPU-optimized pipeline initialized successfully")
    return _llm_pipe

def init_qa_chain(retriever):
    """Инициализация QA цепочки с оптимизированными настройками."""
    llm_pipe = init_llm_pipeline()
    system_prompt = load_system_prompt()

    # Оптимизированный промпт шаблон
    prompt_template = """<|im_start|>system
{system_prompt}
<|im_end|>
<|im_start|>user
Context:
{context}

Question: {question}
<|im_end|>
<|im_start|>assistant
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question", "system_prompt"]
    )

    # Оптимизированная QA цепочка
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm_pipe,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={
            "prompt": prompt,
            "verbose": False  # Отключаем подробный вывод для производительности
        },
        return_source_documents=True,
        verbose=False
    )

    logging.info("QA chain initialized with CPU optimizations")
    return qa_chain
