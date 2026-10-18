"""Optional official Agent subclass; importing it does not start inference."""
from harbor.agents.terminus_2.terminus_2 import Terminus2


class CompatibleTerminus2(Terminus2):
    @staticmethod
    def _parse_skill_frontmatter(content):
        return Terminus2._parse_skill_frontmatter(content.replace('\r\n', '\n').replace('\r', '\n'))
