from base_agent import BaseAgent
from base_model import BaseLLM
from llm_factory import LLMConfig,LLMFactory,SupportLLM
import re

# I will give you a program. \
# You Task is to give me assertions during the running process of this program. \
# Split generated assertions and return them in a list from the most important to the least important.

SYSTEM_PROMPT = '''\
### Your Task ###
I will provide you with a program.
Your task is to generate assertions based on the program's execution.
Please split the generated assertions and return them in a list, ordered from the most generalizable to the least generalizable for {attention}.

### Notes ###
1. Try to find more complex assertions involving multiple variables with longer expressions.
2. Prioritize finding generalizable assertions that hold true across a wider range of situations.
3. Limit operators in the assertions to "==", "!=", "<", ">", "<=", ">=".
4. Avoid using operators like "&&", "and", "||", "or", "==>", "->", "=>", "implies" and "^".

### Program ###
{program}
'''

# 3. All the variables in assertions should have appeared in the program.

### Existing Clauses ###
# {existing_clauses}

JSON_SCHEMA="""\
{
    "clause_list": [<clause_1>,<clause_2>,...],     # Your generate clauses,
}\
"""



NOT_LIST_MESSAGE="""\
**FAILURE** : The clause_list you give is NOT a list.

Your response should strictly do follow the following JSON format:
```
{json_schema}
```
Please fix the above shown issues and response again.

## Your Response ##
"""



NO_MORE_CLAUSE_MESSAGE="""\
**FAILURE** : The clause_list you give should contain new clauses other than those generated before.
Please generate some new clauses.
If you cannot, please return an empty list.
"""

# Existing clauses are shown below:
# {existing_clauses}
# """

# Your response should strictly follow the following JSON format:
# ```
# {json_schema}
# ```
# Please fix the above shown issues and response again.

# ## Your Response ##
# """

# Hints = """\
# Here are some hints:
# 1. Try to find more complex assertions with more variables and constants, and these assertions can hold true during the total running process.
# """
# 2. When variables change at fixed rates, it's helpful to combine them with coefficients that reflect their rates of change.

# 4. Avoid using logical operators like "&&", "||", "==>", "->", "if", "=>", "or", and "and".

class Re_Clause_generater(BaseAgent):
    def __init__(
        self,
        program,
        existing_clauses,
        generate_llm:BaseLLM,
        *args,**kwargs
    ):
        super().__init__(llm=generate_llm,json_schema=JSON_SCHEMA,*args,**kwargs)
        self.program=program
        self.existing_clauses=set()
        self.ce_type = None
        self.attention="pre-conditions, loop body, and post-conditions"

    def generate(self):
        attention_temp=self.attention
        # self.attention = "pre-conditions, loop body, and post-conditions"
        return self.run(
            SYSTEM_PROMPT.format(
                program=self.program,
                # existing_clauses=self.existing_clauses,
                attention=attention_temp
            )
        )
        
    def _check_format(self,response,*args,**kwargs):
        for field in ["clause_list"]:
            if field not in response:
                return False,f"'{field}' is missing in the JSON object"
        return True, None
    
    def _check_semantics(self,response,*args,**kwargs):
        clause_list=response['clause_list']
        if type(clause_list) is not list:
            return False, NOT_LIST_MESSAGE.format(
                json_schema=self.json_schema
            )
        variables = set()
        for clause in clause_list:
            # pattern = r"(\(?\w+(\s*[-+*/%]\s*\w+)*)\s*([<>!=]=?|==)\s*(\w+(\s*[-+*/%]\s*\w+)*\)?)"
            # match = re.match(pattern, clause)
            # if not match:
            #     return False, f'"{clause}" is not in the correct format'
            pattern = r'\b[a-zA-Z_]\w*\b'
            variables.update(re.findall(pattern, clause))
            if not any(op in clause for op in ['==','!=','<','>','<=','>=']):
                return False, f'"{clause}" contains invalid operators'
            pattern = r'(==|!=|>=|<=|>|<)'
            matches = re.findall(pattern, clause)
            if len(matches) > 1:
                return False, f'"{clause}" is illegal, split results like this into clauses and return!'
            for op in ['&&', '||', "==>", "->", "if", "=>", "()", " or ", " and ", "^", " implies ", " for ", " when ", " where ", "?"]:
            # for op in ["==>", "->", "if", "=>", "()", " or ", " and ", "^", " implies ", " for ", " when ", " where ", "?"]:
                if op in clause:
                    return False, f'"{op}" cannot be used'
            # if any(op in clause for op in ['&&','||',"==>","->","if","=>","()"]):
            #     return False, f'"{op}" cannot be used'
        program_vars = re.findall(r'\b[a-zA-Z_]\w*\b', self.program)
        for var in variables:
            if var not in program_vars:
                return False, f'"{var}"" cannot be used'

        if clause_list==[]:
            return True,None
            # return False, Hints
        
        diff=[item for item in clause_list if item not in self.existing_clauses]
        if len(diff)==0:
            return False, NO_MORE_CLAUSE_MESSAGE.format(
                existing_clauses=self.existing_clauses,
                json_schema=self.json_schema
            )
        return True,None

    def _parse_response(self,response,*args,**kwargs):
        clause_list = response['clause_list']
        return clause_list
        # diff=[item for item in clause_list if item not in self.existing_clauses]
        # return diff

    def _reach_max_round(self,*args,**kwargs):
        return []
    # ,"The model have reached the max number of chat round"
    
if __name__ == "__main__":
    message = '''
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
    '''
    existing_clauses=[]
    llm=LLMConfig(SupportLLM("deepseek-chat"),debug_mode=True,temperature=0.8)
    agent=Re_Clause_generater(
        program=message,
        existing_clauses=existing_clauses,
        generate_llm=LLMFactory.create(llm)
    )
    agent.generate()