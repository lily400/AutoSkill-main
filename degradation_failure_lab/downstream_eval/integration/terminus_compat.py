"""Optional official Agent subclass; importing it does not start inference."""
from typing import Literal
from pydantic import model_validator
from harbor.agents.terminus_2.terminus_2 import Terminus2, Terminus2Options
from .p1_observer import P1ObservationMixin


class CompatibleTerminus2Options(Terminus2Options):
    p1_mode: Literal['probe', 'paid'] | None = None
    p1_profile: str | None = None
    p1_manifest: str | None = None

    @model_validator(mode='after')
    def require_p1_inputs(self):
        if self.p1_mode and (not self.p1_profile or not self.p1_manifest):
            raise ValueError('P1 requires a frozen profile and Skill manifest')
        return self


class CompatibleTerminus2(P1ObservationMixin, Terminus2):
    options_model = CompatibleTerminus2Options
    @staticmethod
    def _parse_skill_frontmatter(content):
        return Terminus2._parse_skill_frontmatter(content.replace('\r\n', '\n').replace('\r', '\n'))
