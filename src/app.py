from dataclasses import dataclass, field

from misc.config import Config
from misc.console import Console
from project.project import Project

@dataclass
class App():
    config: Config = field(default_factory=lambda: Config())
    project: Project = field(default_factory=lambda: Project())
    console: Console = field(default_factory=lambda: Console())

    def __post_init__(self):
        self.console.parent_app = self
        self.project.parent_app = self

    def run(self):
        pass

    def init_project():
        pass
