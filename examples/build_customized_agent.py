"""
文件名: MetaGPT/examples/build_customized_agent.py
创建日期: 2023年9月19日 星期二 下午6:52:25
作者: garylin2099
"""

import asyncio
import re
import subprocess

import fire

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.roles.role import Role, RoleReactMode
from metagpt.schema import Message


class SimpleWriteCode(Action):
    """
    基于提供的指令生成Python代码的动作类。

    属性:
        PROMPT_TEMPLATE (str): 用于生成代码编写提示的模板。
        name (str): 动作名称。
    """

    PROMPT_TEMPLATE: str = """
    Write a python function that can {instruction} and provide two runnable test cases.
    Return ```python your_code_here ``` with NO other texts,
    your code:
    """
    name: str = "SimpleWriteCode"

    async def run(self, instruction: str):
        """
        根据指令生成Python代码。

        参数:
            instruction (str): 描述要实现功能的指令。

        返回:
            str: 从模型响应中提取的Python代码。
        """
        prompt = self.PROMPT_TEMPLATE.format(instruction=instruction)
        rsp = await self._aask(prompt)
        code_text = SimpleWriteCode.parse_code(rsp)
        return code_text

    @staticmethod
    def parse_code(rsp):
        """
        从响应中提取包含在markdown代码块中的Python代码。

        参数:
            rsp (str): 包含代码块的响应字符串。

        返回:
            str: 提取的Python代码，如果未找到代码块，则返回原始响应。
        """
        pattern = r"```python(.*)```"
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else rsp
        return code_text


class SimpleRunCode(Action):
    """
    运行Python代码并捕获其输出的动作类。

    属性:
        name (str): 动作名称。
    """

    name: str = "SimpleRunCode"

    async def run(self, code_text: str):
        """
        子进程运行Python代码，捕获输出。

        参数:
            code_text (str): 要执行的Python代码。

        返回:
            str: 运行代码的输出结果。
        """
        result = subprocess.run(
            ["python3", "-c", code_text], capture_output=True, text=True
        )
        code_result = result.stdout
        logger.info(f"{code_result=}")
        return code_result


class SimpleCoder(Role):
    """
    表示一个能够根据指令编写Python代码的角色。

    属性:
        name (str): 角色名称。
        profile (str): 角色标识。
    """

    name: str = "Alice"
    profile: str = "SimpleCoder"

    def __init__(self, **kwargs):
        """
        初始化SimpleCoder角色，并设置可用的动作。
        """
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteCode])

    async def _act(self) -> Message:
        """
        执行当前动作，并生成对应的消息。

        返回:
            Message: 包含生成代码的消息。
        """
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo  # 当前要执行的动作
        msg = self.get_memories(k=1)[0]  # 获取最近的一条消息
        code_text = await todo.run(msg.content)
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))
        return msg


class RunnableCoder(Role):
    """
    表示一个能够编写和运行Python代码的角色。

    属性:
        name (str): 角色名称。
        profile (str): 角色标识。
    """

    name: str = "Alice"
    profile: str = "RunnableCoder"

    def __init__(self, **kwargs):
        """
        初始化RunnableCoder角色，设置可用的动作和响应模式。
        """
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteCode, SimpleRunCode])
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)

    async def _act(self) -> Message:
        """
        按顺序执行动作，并生成对应的消息。

        返回:
            Message: 包含生成代码或执行结果的消息。
        """
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo  # 当前要执行的动作
        msg = self.get_memories(k=1)[0]  # 获取最近的一条消息
        result = await todo.run(msg.content)
        msg = Message(content=result, role=self.profile, cause_by=type(todo))
        self.rc.memory.add(msg)
        return msg


def main(msg="write a function that calculates the product of a list and run it"):
    """
    主函数，用于初始化角色并执行其动作。

    参数:
        msg (str): 提供给角色处理的指令消息。
    """
    role = RunnableCoder()  # 实例化RunnableCoder角色
    logger.info(msg)
    result = asyncio.run(role.run(msg))
    logger.info(result)


if __name__ == "__main__":
    fire.Fire(main)
