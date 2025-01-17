from metagpt.config2 import Config
from metagpt.roles import Role
from metagpt.actions import Action
import asyncio
from metagpt.environment import Environment
from metagpt.team import Team


# gpt4o = Config.default() # 使用默认模型
gpt4 = Config.from_home("gpt-4o.yaml")  # ~/.metagpt/gpt-4o.yaml，使用来自文件的配置
gpt4t = Config.default()
gpt4t.llm.model = "gpt-4-turbo"  # 修改模型为 "gpt-4-turbo"
gpt35 = Config.default()
gpt35.llm.model = "gpt-3.5-turbo"  # 修改模型为 "gpt-3.5-turbo"

# 创建3个Action，其中a1的模型指定为gpt4t
a1 = Action(config=gpt4t, name="Say",
            instruction="Say your opinion with emotion and don't repeat it")
a2 = Action(
    name="Say", instruction="Say your opinion with emotion and don't repeat it")
a3 = Action(name="Vote",
            instruction="Vote for the candidate, and say why you vote for him/her")

# 创建3个Role. 代表 "民主党候选人," "共和党候选人," 和 "选民".
# 尽管A在Role配置中设置为使用gpt4，但由于Action配置的设置，它将使用带有模型gpt4的a1的配置。
A = Role(name="A", profile="Democratic candidate",
         goal="Win the election", actions=[a1], watch=[a2], config=gpt4)
# 由于B在Role配置中设置为使用gpt35，且a2无Action配置，因此B和a2都会使用Role配置，即gpt35。
B = Role(name="B", profile="Republican candidate",
         goal="Win the election", actions=[a2], watch=[a1], config=gpt35)
# 由于C没有设置任何配置，且a3也没有设置配置，因此C和a3都会使用全局配置，即gpt4o配置。
C = Role(name="C", profile="Voter", goal="Vote for the candidate",
         actions=[a3], watch=[a1, a2])

# 创建一个被描述为“美国大选现场直播”的环境。
env = Environment(desc="US election live broadcast")
team = Team(investment=10.0, env=env, roles=[A, B, C])
# 运行team，观察他们之间的协作。
asyncio.run(team.run(
    idea="Topic: climate change. Under 80 words per message.", send_to="A", n_round=3))
# await team.run(idea="Topic: climate change. Under 80 words per message.", send_to="A", n_round=3) # 若在Jupyter Notebook中运行
