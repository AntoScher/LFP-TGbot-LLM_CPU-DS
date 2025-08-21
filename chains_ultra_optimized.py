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

def init_ultra_optimized_llm():
    """УЛЬТРА-оптимизированный LLM пайплайн"""
    global _llm_pipe
    if _llm_pipe is not None:
        return _llm_pipe

    model_id = "microsoft/DialoGPT-small"  # Намного меньшая модель!
    
    print(f"Loading ULTRA-LIGHT model {model_id} on CPU...")
    
    # Загружаем сверхлегкую модель
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    )
    model = model.to('cpu')
    model.eval()
    
    # Сверхбыстрый пайплайн
    text_generation_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=64,    # ОЧЕНЬ короткие ответы
        temperature=0.1,      # Минимальная креативность
        top_p=0.7,
        do_sample=True,
        return_full_text=False,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    
    _llm_pipe = HuggingFacePipeline(
        pipeline=text_generation_pipeline,
        model_kwargs={"temperature": 0.1, "max_new_tokens": 64}
    )
    
    print("ULTRA-LIGHT model loaded successfully!")
    logging.info("Ultra-optimized LLM pipeline initialized")
    return _llm_pipe

def init_cached_qa_chain(retriever):
    """QA цепь с кэшированием результатов"""
    llm_pipe = init_ultra_optimized_llm()
    system_prompt = load_system_prompt()

    # МИНИМАЛИСТИЧНЫЙ промпт для скорости
    prompt_template = """Контекст: {context}

Вопрос: {question}

Краткий ответ (до 50 слов):"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm_pipe,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
        verbose=False
    )

    logging.info("Ultra-optimized QA chain initialized")
    return qa_chain
