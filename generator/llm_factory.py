from dataclasses import dataclass,field
from enum import Enum,unique
from typing import List
from base_model import BaseLLM



@unique
class SupportLLM(Enum):
    GPT_o1='o1-mini'
    GPT_35='gpt-3.5'
    GPT_4='gpt-4'
    GPT_4o='gpt-4o'
    GPT_4o_mini='gpt-4o_mini'
    Deepseek_chat='deepseek-chat'
    Deepseek_coder='deepseek-coder'
    LOCAL_Llama='local-llama3.1'
    Qwen_Plus="qwen-plus"
    Qwen_Turbo="qwen-turbo"
    GLM_4="glm-4"
    BAIDU='baidu'

    @classmethod
    def values(cls):
        return [x.value for x in cls]
    
    @classmethod
    def names(cls):
        return [x.name for x in cls]
    

@dataclass
class LLMConfig:
    llm:SupportLLM
    debug_mode:bool = field(default=False)
    temperature:float=field(default=0.8)
    sample:int=field(default=1)
    max_tokens:int=field(default=4096)

class LLMFactory:
    _created_llms:List[BaseLLM]=[]

    @classmethod
    def create(cls,config:LLMConfig,*args,**kwargs):
        if config.llm == SupportLLM.Deepseek_chat:
            from deepseek import DeepSeek_Chat
            create_model=DeepSeek_Chat
        elif config.llm == SupportLLM.Deepseek_coder:
            from deepseek import DeepSeek_Coder
            create_model=DeepSeek_Coder
        elif config.llm == SupportLLM.GPT_o1:
            from openai_model import GPT_o1
            create_model=GPT_o1
        elif config.llm == SupportLLM.GPT_35:
            from openai_model import GPT_35
            create_model=GPT_35
        elif config.llm == SupportLLM.GPT_4o:
            from openai_model import GPT_4o
            create_model=GPT_4o
        elif config.llm == SupportLLM.GPT_4o_mini:
            from openai_model import GPT_4o_mini
            create_model=GPT_4o_mini
        elif config.llm == SupportLLM.GPT_4:
            from openai_model import GPT_4
            create_model=GPT_4
        elif config.llm == SupportLLM.LOCAL_Llama:
            from ollama import Llama31
            create_model=Llama31
        elif config.llm == SupportLLM.Qwen_Plus:
            from qwen import Qwen_Plus
            create_model = Qwen_Plus
        elif config.llm == SupportLLM.Qwen_Turbo:
            from qwen import Qwen_Turbo
            create_model = Qwen_Turbo
        elif config.llm == SupportLLM.GLM_4:
            from glm import GLM_4
            create_model = GLM_4
        elif config.llm == SupportLLM.BAIDU:
            from ernie import ERNIE_Speed
            create_model = ERNIE_Speed
        else:
            raise NotImplementedError("Not supported:"+config.llm.name)
        llm=create_model(
            debug_mode=config.debug_mode,
            temperature=config.temperature,
            sample=config.sample,
            max_tokens=config.max_tokens,
            *args,**kwargs
        )
        cls._created_llms.append(llm)
        return llm
    
    @classmethod
    def destroy(cls,llm):
        llm.destroy()


