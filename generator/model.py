from abc import ABC, abstractmethod
from typing import List,Dict, Union
import openai
import time
from openai import OpenAI
from utils import setup_logger

class DecoderBase(ABC):
    def __init__(
        self,
        name: str,
        logger,
        batch_size: int = 1,
        temperature: float = 0.8,
        max_new_tokens: int = 1024,
    ) -> None:
        print("Initializing model ...")
        self.name = name
        self.logger = logger
        self.batch_size = batch_size
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens

    @abstractmethod
    def codegen(self, message: str, num_samples: int = 1) -> List[dict]:
        pass

    @abstractmethod
    def is_direct_completion(self) -> bool:
        pass

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def create_config(
        self,
        message: str,
        max_tokens: int,
        model: str,
        temperature: float = 0.8,
        batch_size: int = 1,
        system_message: str = "You are a helpful assistant.",
    ) -> Dict:
        config = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "n": batch_size,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": message},
            ],
        }
        return config
    
    def request_engine(self,config, logger, base_url=None, api_key=None,max_retries=10, timeout=100):
        ret = None
        retries = 0

        client = openai.OpenAI(base_url=base_url,api_key=api_key)

        while ret is None and retries < max_retries:
            try:
                # Attempt to get the completion
                logger.info("Creating API request")

                ret = client.chat.completions.create(**config)

            except openai.OpenAIError as e:
                if isinstance(e, openai.BadRequestError):
                    logger.info("Request invalid")
                    print(e)
                    logger.info(e)
                    raise Exception("Invalid API Request")
                elif isinstance(e, openai.RateLimitError):
                    print("Rate limit exceeded. Waiting...")
                    logger.info("Rate limit exceeded. Waiting...")
                    print(e)
                    logger.info(e)
                    time.sleep(5)
                elif isinstance(e, openai.APIConnectionError):
                    print("API connection error. Waiting...")
                    logger.info("API connection error. Waiting...")
                    print(e)
                    logger.info(e)
                    time.sleep(5)
                else:
                    print("Unknown error. Waiting...")
                    logger.info("Unknown error. Waiting...")
                    print(e)
                    logger.info(e)
                    time.sleep(1)

            retries += 1

        logger.info(f"API response {ret}")
        return ret

class OpenAIChatDecoder(DecoderBase):
    def __init__(self, name: str, logger, **kwargs) -> None:
        super().__init__(name, logger, **kwargs)

    def codegen(self, message: str, num_samples: int = 1) -> List[dict]:
        if self.temperature == 0:
            assert num_samples == 1
        batch_size = min(self.batch_size, num_samples)

        config = self.create_config(
            message=message,
            max_tokens=self.max_new_tokens,
            temperature=self.temperature,
            batch_size=batch_size,
            model=self.name,
        )
        ret = self.request_engine(config, self.logger,api_key="")
        if ret:
            responses = [choice.message.content for choice in ret.choices]
            completion_tokens = ret.usage.completion_tokens
            prompt_tokens = ret.usage.prompt_tokens
        else:
            responses = []
            completion_tokens = 0
            prompt_tokens = 0
        return responses
    
    def is_direct_completion(self) -> bool:
        return False

class DeepSeekChatDecoder(DecoderBase):
    def __init__(self, name: str, logger, **kwargs) -> None:
        super().__init__(name, logger, **kwargs)
        self.model="deepseek-chat"

    def codegen(self, message: str, num_samples: int = 1) -> List[dict]:
        if self.temperature == 0:
            assert num_samples == 1

        for _ in range(num_samples):
            config = self.create_config(
                message=message,
                max_tokens=self.max_new_tokens,
                temperature=self.temperature,
                batch_size=1,
                model=self.model,
            )
            ret = self.request_engine(
                config, self.logger, base_url="https://api.deepseek.com/v1",api_key=""
            )
            if ret:
                return [ret.choices[0].message.content]
            else:
                return []
            
    def is_direct_completion(self) -> bool:
        return False

class LocalLlama31(DecoderBase):
    def __init__(self, name: str, logger, **kwargs) -> None:
        super().__init__(name, logger, **kwargs)
        self.model="llama3.1:latest"

    def call_llama(self,config,logger):
        ret = None
        retry = 0
        while ret is None and retry<10:
            try:
                client = OpenAI(
                    base_url="http://localhost:11434/v1/",
                    api_key='ollama'
                )
                ret=client.chat.completions.create(**config)
            except Exception as e:
                print(e)
                logger.info(e)
                raise Exception("Invalid Llama Request")
            retry+=1
        return ret
    
    def codegen(self, message: str, num_samples: int = 1) -> List[Dict]:
        if self.temperature == 0:
            assert num_samples==1
        batch_size=min(self.batch_size,num_samples)
        config = self.create_config(
            message=message,
            max_tokens=self.max_new_tokens,
            temperature=self.temperature,
            batch_size=batch_size,
            model=self.model,
        )
        ret = self.call_llama(config,logger=self.logger)
        if ret:
            responses = [choice.message.content for choice in ret.choices]
            completion_tokens = ret.usage.completion_tokens
            prompt_tokens = ret.usage.prompt_tokens
        else:
            responses = []
            completion_tokens = 0
            prompt_tokens = 0
        return responses
    
    def is_direct_completion(self) -> bool:
        return False
    
def make_model(
    model: str,
    backend: str,
    logger,
    batch_size: int,
    max_tokens: int,
    temperature: float,
):
    if backend == "openai":
        return OpenAIChatDecoder(
            name=model,
            logger=logger,
            batch_size=batch_size,
            max_new_tokens=max_tokens,
            temperature=temperature,
        )
    elif backend == "deepseek":
        return DeepSeekChatDecoder(
            name=model,
            logger=logger,
            batch_size=batch_size,
            max_new_tokens=max_tokens,
            temperature=temperature,
        )
    elif backend == "llama":
        return LocalLlama31(
            name=model,
            logger=logger,
            batch_size=batch_size,
            max_new_tokens=max_tokens,
            temperature=temperature,
        )
    else:
        raise NotImplementedError

if __name__ == '__main__':
    message = '''
    You are an expert in the field of program analysis, especially data flow analysis, tasked to help me generate some loop invariant clauses about a program.

    ### Background ###
    A valid loop invariant expression is composed of many clauses and operators, \
    and must hold true when program runs in pre-conditions, loop body and post-condition. 

    ### Your Task ###
    I will give you a "Program" which is a complete function. \
    You should carefully analyze the program and try to understand how this program works.
    Your Task is to generate some clauses which you think should be components of a valid loop invariant expression correspond to the program.
    A good clause should be laconic and contains important information about the data flow constriant, which help me ensure the program is designed as expected.

    Note:
    1. MUST return ONLY clauses without other words.
    2. DO NOT return clauses contain variables which not appear in the program.
    3. Even if you can generate the whole loop invariant expression, Please split them and returns each clause separately

    ### Program ###
    int main() {
        // variable declarations
        int n;
        int x;
        // pre-conditions
        x = 0;
        // loop body
        while (x < n) {
            x  = (x + 1);
        }
        // post-condition
        if (n >= 0){
            assert (x == n);
        }
    }

    ### Format ###
    The returned clauses should be separated by new lines ordered by most to least importmant.
    For example:
    ```
    0<x<n
    x>=0
    x<=n
    x==n
    n>=(x+x)
    ```

    '''
    logger=setup_logger("./a.log")
    model = make_model(
        model="1",
        backend='deepseek',
        logger=logger,
        batch_size=1,
        max_tokens=4096,
        temperature=0
    )
    res=model.codegen(message,num_samples=1)
    print(res)
