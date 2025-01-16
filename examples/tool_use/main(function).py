# main.py
import asyncio
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.libs import calculate_factorial


async def main(requirement: str):
    # integrate the tool
    role = DataInterpreter(tools=["calculate_factorial"])
    await role.run(requirement)

if __name__ == "__main__":
    requirement = "Please calculate the factorial of 5."
    asyncio.run(main(requirement))
