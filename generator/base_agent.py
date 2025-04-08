from model import make_model
from utils import setup_logger
from abc import ABC,abstractmethod
from base_model import BaseLLM,ChatMessage
from typing import Optional,Tuple,List

SYSTEM_PROMPT_JSON_INSTRUCTION="""\
## RESPONSE FORMAT ##

Your Response MUST be in the following JSON format:
```
{json_schema}
```

## Your Response ##
"""


INVALID_JSON_OBJECT_MESSAGE="""\
**FAILURE** : Your response is not a valid JSON object:{err_message}

Your response should strictly do follow the following JSON format:
```
{json_schema}
```
Please fix the above shown issues and response again.

## Your Response ##

"""

VIOLATED_JSON_FORMAT_MESSAGE="""\
**FAILURE** : Your responded JSON object violates the given JSON format :{error_message}

Your response should strictly do follow the following JSON format:
```
{json_schema}
```
Please fix the above shown issues and response again.

## Your Response ##

"""


class BaseAgent(ABC):
    def __init__(
            self,
            llm:BaseLLM,
            json_schema:str,
            *,
            max_chat_round=5
            ) -> None:
        self.llm=llm
        self.json_schema=json_schema
        self.max_chat_round=max_chat_round

    def get_history(self) -> List[ChatMessage]:
        return self.llm.get_history()

    def run(self,system_prompt,*args,**kwargs):
        self.llm.clear_history()
        self.llm.append_user_message(
            system_prompt + SYSTEM_PROMPT_JSON_INSTRUCTION.format(json_schema=self.json_schema)
        )
        
        for _ in range(self.max_chat_round):
            #JSON格式错误
            response,err_msg = self.llm.parse_json_response(self.llm.query())
            # print(response, err_msg)
            if response is None:
                self.llm.append_user_message(
                    INVALID_JSON_OBJECT_MESSAGE.format(
                        err_message=err_msg,
                        json_schema=self.json_schema
                    )
                )
                continue
            #格式错误
            formated,err_msg=self._check_format(response,*args,**kwargs)
            if not formated:
                self.llm.append_user_message(
                    VIOLATED_JSON_FORMAT_MESSAGE.format(
                        err_message=err_msg,
                        json_schema=self.json_schema
                    )
                )
                continue
            #语义错误
            valid,err_prompt=self._check_semantics(response,*args,**kwargs)
            if not valid:
                self.llm.append_user_message(err_prompt)
                continue
            #读取答案
            return self._parse_response(response,*args,**kwargs)
        return self._reach_max_round()
    
    @abstractmethod
    def _check_format(self,response,*args,**kwargs):
        ...

    @abstractmethod
    def _check_semantics(self,response,*args,**kwargs):
        ...

    @abstractmethod
    def _parse_response(self,response,*args,**kwargs):
        ...

    @abstractmethod
    def _reach_max_round(self,response,*args,**kwargs):
        ...
