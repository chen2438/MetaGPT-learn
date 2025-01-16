# main.py
import asyncio
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.libs import calculator

async def main(requirement: str):
    role = DataInterpreter(tools=["Calculator"]) # integrate the tool
    await role.run(requirement)

if __name__ == "__main__":
    requirement = "Please calculate 5 plus 3 and then calculate the factorial of 5."
    asyncio.run(main(requirement))