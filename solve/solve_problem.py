import re
import fire
from typing import List
import pytest

from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team

def parse_code(rsp: str) -> str:
    """从响应中提取Python代码"""
    pattern = r"```python(.*)```"
    match = re.search(pattern, rsp, re.DOTALL)
    code_text = match.group(1) if match else rsp
    return code_text.strip()

class WriteCode(Action):
    """编写代码的Action"""
    name: str = "WriteCode"
    
    async def run(self, problem: str):
        prompt = f"""
        Write a Python function that solves this problem:
        {problem}
        
        Requirements:
        1. The function should handle large numbers (n <= 50)
        2. Use Python's built-in support for large integers
        3. Implement efficient factorial calculation
        4. Return the sum of factorials from 1! to n!
        5. Handle edge cases properly
        
        Return the implementation in a code block like:
        ```python
        your_code_here
        ```
        No other text, just the code block.
        """
        rsp = await self._aask(prompt)
        return parse_code(rsp)

class WriteTest(Action):
    """编写测试用例的Action"""
    name: str = "WriteTest"
    
    async def run(self, context: str):
        prompt = f"""
        Here is a function implementation:
        {context}
        
        Write pytest test cases to thoroughly test this function.
        Include edge cases like empty list, list with no even numbers, etc.
        Return ONLY the test code in a code block like:
        ```python
        your_test_code_here
        ```
        """
        rsp = await self._aask(prompt)
        return parse_code(rsp)

class FixCode(Action):
    """修复代码的Action"""
    name: str = "FixCode"
    
    async def run(self, code: str, test_output: str):
        prompt = f"""
        The current implementation:
        {code}
        
        Failed these tests:
        {test_output}
        
        Fix the code to pass all tests.
        Return ONLY the fixed code in a code block like:
        ```python
        your_fixed_code_here
        ```
        """
        rsp = await self._aask(prompt)
        return parse_code(rsp)

class Engineer(Role):
    """工程师角色"""
    name: str = "Engineer"
    profile: str = "Python Engineer"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([UserRequirement])
        self.set_actions([WriteCode, FixCode])
        self.current_code = ""
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        
        if isinstance(todo, WriteCode):
            # 从problem.md读取问题
            with open("problem.md", "r") as f:
                problem = f.read()
            
            code = await todo.run(problem)
            self.current_code = code
            return Message(content=code, role=self.profile, cause_by=type(todo))
            
        elif isinstance(todo, FixCode):
            # 获取最新的测试输出并修复代码
            memories = self.get_memories()
            last_msg = memories[-1]
            code = await todo.run(self.current_code, last_msg.content)
            self.current_code = code
            return Message(content=code, role=self.profile, cause_by=type(todo))

class Tester(Role):
    """测试工程师角色"""
    name: str = "Tester"
    profile: str = "Test Engineer"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteTest])
        self._watch([WriteCode, FixCode])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        memories = self.get_memories()
        
        # 获取最新的代码实现
        code_msg = memories[-1]
        code = code_msg.content
        
        # 生成测试代码
        test_code = await todo.run(code)
        
        # 创建临时Python文件来执行测试
        with open("temp_solution.py", "w") as f:
            f.write(code)
        with open("test_solution.py", "w") as f:
            f.write("from temp_solution import *\n\n" + test_code)
            
        try:
            # 运行测试
            pytest.main(["test_solution.py", "-v"])
            return Message(content="All tests passed!", role=self.profile, cause_by=type(todo))
        except Exception as e:
            # 测试失败,返回错误信息
            return Message(content=str(e), role=self.profile, cause_by=type(todo))

async def main(investment: float = 3.0, n_round: int = 5):
    team = Team()
    team.hire([Engineer(), Tester()])
    team.invest(investment)
    
    # 从problem.md读取问题
    with open("problem.md", "r") as f:
        problem = f.read()
    
    team.run_project(problem)
    await team.run(n_round=n_round)

if __name__ == "__main__":
    fire.Fire(main)
