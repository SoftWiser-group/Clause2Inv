from abc import ABC, abstractmethod
from typing import List,Dict, Union
import openai
import time
from openai import OpenAI
from utils import setup_logger
from base_model import BaseLLM


class DeepSeek(BaseLLM):
    def __init__(self, model: str, *args,**kwargs) -> None:
        super().__init__(*args,**kwargs)
        self.model=model

    def call_deepseek(self,model_name,messages,*,temperature,sample,max_tokens):
        config = {
            "model": model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "n": sample,
            "messages": messages,
        }
        ret = None
        retries = 0
        client = openai.OpenAI(base_url="https://api.deepseek.com/v1",api_key="YOUR_API_KEY")
        
        while ret is None and retries < 5:
            try:
                ret = client.chat.completions.create(**config)
            except Exception as e:
                print(e)

            retries += 1
            
        return ret.choices[0].message.content

    def do_query(self) -> str:
        return self.call_deepseek(
            self.model,
            [m.to_json() for m in self.history],
            temperature=self.temperature,
            sample=self.sample,
            max_tokens=self.max_tokens
        )

class DeepSeek_Chat(DeepSeek):
    def __init__(self, *args, **kwargs):
        super().__init__(model='deepseek-chat',*args, **kwargs)

class DeepSeek_Coder(DeepSeek):
    def __init__(self, *args, **kwargs):
        super().__init__(model='deepseek-coder',*args, **kwargs)



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
    model_=DeepSeek_Chat(debug_mode=True)
    model_.append_user_message(message)
    model_.query()
