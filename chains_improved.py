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

def load_system_prompt(path: str = "system_prompt_improved.txt") -> str:
    """Загружает улучшенный системный промпт"""
    global _system_prompt
    if _system_prompt is None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                _system_prompt = f.read().strip()
        except Exception as e:
            logging.error(f"Error loading system prompt: {e}")
            _system_prompt = "Ты — ассистент отдела продаж. Отвечай ТОЛЬКО на основе предоставленной информации."
    return _system_prompt

def init_llm_pipeline():
    """Инициализация оптимизированного LLM пайплайна"""
    global _llm_pipe
    if _llm_pipe is not None:
        return _llm_pipe

    model_id = os.getenv("MODEL_NAME", "Qwen/Qwen2-1.5B-Instruct")
    cache_dir = os.getenv("HF_HOME")

    # Загружаем токенизатор
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        cache_dir=cache_dir,
        trust_remote_code=True,
        use_fast=False  # Для стабильности
    )

    # Загружаем модель на CPU с оптимизациями
    print(f"Loading optimized model {model_id} on CPU...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,  # Стабильность на CPU
        low_cpu_mem_usage=True,
        cache_dir=cache_dir,
        trust_remote_code=True
    )
    model = model.to('cpu')
    model.eval()  # Режим инференса
    print("Optimized model loaded on CPU")

    # Оптимизированный пайплайн
    text_generation_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,  # Уменьшено для скорости
        temperature=0.3,     # Меньше креативности, больше точности
        top_p=0.8,          # Более консервативная генерация
        repetition_penalty=1.1,
        return_full_text=False,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    
    _llm_pipe = HuggingFacePipeline(
        pipeline=text_generation_pipeline,
        model_kwargs={
            "temperature": 0.3,
            "max_new_tokens": 256
        }
    )
    
    logging.info("Optimized LLM pipeline initialized")
    return _llm_pipe

def init_qa_chain(retriever):
    """Инициализация улучшенной QA цепи"""
    llm_pipe = init_llm_pipeline()
    system_prompt = load_system_prompt()

    # УЛУЧШЕННЫЙ промпт с четкими инструкциями
    prompt_template = """<|im_start|>system
{system_prompt}

КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:
{context}

ПРАВИЛА ОТВЕТА:
1. Используй ТОЛЬКО информацию из контекста выше
2. НЕ добавляй информацию, которой нет в контексте
3. Если информации недостаточно - скажи об этом честно
4. Ответ должен быть кратким (до 150 слов)
5. Используй структурированный формат с эмодзи
<|im_end|>
<|im_start|>user
Вопрос: {question}
<|im_end|>
<|im_start|>assistant
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
        partial_variables={"system_prompt": system_prompt}
    )

    # Улучшенная QA цепь с более строгими параметрами
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm_pipe,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={
            "prompt": prompt,
            "document_prompt": PromptTemplate(
                input_variables=["page_content"],
                template="ДОКУМЕНТ: {page_content}"
            ),
            "document_variable_name": "context",
            "verbose": False
        },
        return_source_documents=False,
        input_key="question",
        output_key="result",
        verbose=False
    )

    logging.info("Improved QA chain initialized successfully")
    return qa_chain
