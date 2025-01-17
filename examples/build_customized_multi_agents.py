"""
文件名: MetaGPT/examples/build_customized_multi_agents.py
创建日期: 2023年11月15日，星期三，19:12:39
作者: garylin2099
"""

# 正则表达式
import re

# Fire 用于命令行接口
import fire

# MetaGPT
from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team

# 从输入字符串中提取 Python 代码


def parse_code(rsp):
    pattern = r"```python(.*)```"  # 匹配代码块的正则表达式
    match = re.search(pattern, rsp, re.DOTALL)  # 匹配整个字符串，包括换行符
    code_text = match.group(1) if match else rsp  # 如果找到匹配，提取代码；否则返回原文本
    return code_text


# 写代码Action
class SimpleWriteCode(Action):
    PROMPT_TEMPLATE: str = """
    Write a python function that can {instruction}.
    Return ```python your_code_here ``` with NO other texts,
    your code:
    """
    name: str = "SimpleWriteCode"

    # 异步运行Action，返回代码
    async def run(self, instruction: str):
        prompt = self.PROMPT_TEMPLATE.format(
            instruction=instruction)  # 将instruction插入到prompt中
        rsp = await self._aask(prompt)  # 使用 MetaGPT 的异步询问功能获取响应
        code_text = parse_code(rsp)  # 提取代码块
        return code_text


# 写代码Role
class SimpleCoder(Role):
    name: str = "Alice"
    profile: str = "SimpleCoder"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # 调用父类（Role）的构造函数
        self._watch([UserRequirement])  # 监听用户需求
        self.set_actions([SimpleWriteCode])  # Action = SimpleWriteCode


# 写测试Action
class SimpleWriteTest(Action):
    PROMPT_TEMPLATE: str = """
    Context: {context}
    Write {k} unit tests using pytest for the given function, assuming you have imported it.
    Return ```python your_code_here ``` with NO other texts,
    your code:
    """
    name: str = "SimpleWriteTest"  # 动作的名称

    # 异步运行Action
    async def run(self, context: str, k: int = 3):
        prompt = self.PROMPT_TEMPLATE.format(
            context=context, k=k)  # 将context插入到prompt中
        rsp = await self._aask(prompt)  # 使用异步询问功能获取响应
        code_text = parse_code(rsp)  # 提取代码块
        return code_text


# 写测试Role
class SimpleTester(Role):
    name: str = "Bob"
    profile: str = "SimpleTester"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteTest])  # Action = SimpleWriteTest
        self._watch([SimpleWriteCode, SimpleWriteReview])  # 监听其他动作

    # 重写行为逻辑，返回Message
    async def _act(self) -> Message:
        logger.info(
            f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        context = self.get_memories()  # 获取所有的记忆作为上下文
        code_text = await todo.run(context, k=5)  # 执行任务并指定参数
        msg = Message(content=code_text, role=self.profile,
                      cause_by=type(todo))
        return msg


# 评审Action （对测试用例的评审）
class SimpleWriteReview(Action):
    PROMPT_TEMPLATE: str = """
    Context: {context}
    Review the test cases and provide one critical comments:
    """
    name: str = "SimpleWriteReview"

    # 异步运行Action
    async def run(self, context: str):
        prompt = self.PROMPT_TEMPLATE.format(context=context)
        rsp = await self._aask(prompt)
        return rsp


# 评审Role （对测试用例的评审）
class SimpleReviewer(Role):
    name: str = "Charlie"
    profile: str = "SimpleReviewer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteReview])  # Action = SimpleWriteReview
        self._watch([SimpleWriteTest])  # 监听SimpleWriteTest


async def main(
    idea: str = "write a function that calculates the product of a list",
    investment: float = 3.0,
    n_round: int = 5,
    add_human: bool = False,
):
    logger.info(idea)

    team = Team()  # 创建团队对象
    team.hire(
        [
            SimpleCoder(),  # 招募编码Role
            SimpleTester(),  # 招募测试Role
            # SimpleReviewer(is_human=add_human),  # 招募评审Role
            SimpleReviewer(is_human=True),
        ]
    )

    team.invest(investment=investment)  # 投资团队
    team.run_project(idea)  # 开始项目
    await team.run(n_round=n_round)  # 运行多个回合


if __name__ == "__main__":
    fire.Fire(main)  # Fire 构建命令行入口
