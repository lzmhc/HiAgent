import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict

import yaml

from agents.base_llm_adapter import create_adapter
from config.global_config import GlobalConfig

# skills目录
SKILLS_DIR = Path(__file__).parent.parent / "skills"
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
@dataclass
class Skill:
    """技能实体类"""
    skill_id: str               # 唯一技能标识
    name: str                   # 技能名称
    description: str            # 技能描述
    prompt_file: Path           # 技能专属系统提示词
    root_dir: Path              # 根目录
    system_prompt: str          # 提示词
    extra_config: Dict = field(default_factory=dict)  # 扩展配置

class SkillRouter:
    def __init__(self, skills: List[Skill], config: GlobalConfig):
        self.adapter = create_adapter(
            model=config.get_config().get_model(),
            api_key=config.get_config().get_api_key(),
            base_url=config.get_config().get_base_url(),
            timeout=config.get_config().get_timeout(),
            temperature=config.get_config().get_temperature(),
            max_tokens=config.get_config().get_max_tokens(),
        )
        self.messages = []
        skill_dict_list = [
            {
                "skill_id": s.skill_id,
                "name": s.name,
                "description": s.description
            }
            for s in skills
        ]
        skills_json = json.dumps(skill_dict_list, ensure_ascii=False, indent=2)
        self.prompt = f"""
            你是一个 Skill Router。

            你的唯一职责是根据用户请求选择需要加载的 Skill。
            
            禁止：
            - 回答用户的问题
            - 解释
            - 给出建议
            - 输出 Markdown
            - 输出除 JSON 外任何内容
            
            已有 Skill：
            {skills_json}
            
            返回格式
            [
                {{
                    "skill_id":"linux"
                }}
            ]
            
            如果没有匹配：

            []
            
            除了 JSON，不允许输出任何字符。
            '''
        """.strip()
        self.messages.append(
            {"role": "system", "content": self.prompt}
        )
    def router_skill(self, message):
        result = ""
        self.messages.append(message)
        stream = self.adapter.stream_invoke(messages=self.messages, tools=None)
        for chunk in stream:
            if hasattr(chunk, "choices") and chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    result += content
        return result

class SkillManage:
    def __init__(self, config: GlobalConfig):
        self.skill_list = self.load_enabled_skills()
        self.skillRouter = SkillRouter(self.skill_list, config)
    # 解析md文件
    def load_skill_from_md(self, file_path: str | Path) -> dict:
        content = Path(file_path).read_text(encoding="utf-8")
        match = FRONTMATTER_PATTERN.match(content)
        if not match:
            raise ValueError("文件无 YAML Frontmatter")
        front_yaml = match.group(1)
        doc_body = content[match.end():]
        meta = yaml.safe_load(front_yaml)
        return {
            "meta": meta,
            "docs": doc_body.strip()
        }

    # 读取skills
    def load_skills(self) -> List[Skill]:
        skills = []
        if not SKILLS_DIR.exists():
            return skills
        for md_file in SKILLS_DIR.glob("*/SKILL.md"):
            try:
                data = self.load_skill_from_md(str(md_file))
                meta = data["meta"]
                skill_name = meta["name"]
                skill_desc = meta["description"]
                doc_content = data["docs"]
                skill = Skill(
                    skill_id=skill_name,
                    name=skill_name,
                    description=skill_desc,
                    prompt_file=md_file,
                    root_dir=md_file.parent,
                    system_prompt=doc_content
                )
                skills.append(skill)
            except Exception as e:
                print(f"加载技能 {md_file.name} 失败: {e}")
        return skills

    # 读取已启用的skills
    def load_enabled_skills(self) -> List[Skill]:
        result = []
        for skill in self.load_skills():
            result.append(skill)
        return result

    # 匹配skills
    def match_skills(self, message):
        ids = self.skillRouter.router_skill(message)
        result = []
        for skill in self.skill_list:
            if skill.skill_id in ids:
                result.append(skill)
        return result

if __name__ == "__main__":
    skillManage = SkillManage()
    message = {
        "role": "user",
        "content": "使用浏览器打开b站"
    }
    print(skillManage.match_skills(message))