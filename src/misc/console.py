"""Console proxy

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass, field
from typing import Callable, Dict

from misc.colors import Color as C
from misc.logger import Logger


@dataclass
class Console:
    """This class is used to proxy console input and output to the CLI"""

    indentationLevel: int = 0
    commands: Dict[str, Callable] = field(default_factory=dict)
    isRunning: bool = True
    log = Logger.Create(__name__)
    parent_app = None

    def read(self) -> str:
        """Querys the user for input to the CLI

        Returns:
            - str: User input
        """
        print("  " * (self.indentationLevel), end="", flush=True)
        if self.parent_app.project.isLoaded:
            print(
                f"{C.OkCyan}{self.parent_app.project.name}{C.End}> ", end="", flush=True
            )
        else:
            print(f"> ", end="", flush=True)
        return input()

    def write(self, message: str, color: C = C.End, newline=True):
        """Writes the given message to the CLI with the given indentation level

        Args:
            - message (str): Message to write to the CLI
        """
        print("  " * (self.indentationLevel), end="", flush=True)
        print("  ", end="", flush=True)
        if newline:
            print(f"{color}{message}{C.End}")
        else:
            print(f"{color}{message}", end="", flush=True)

    def append(self, message: str, finish=True):
        """Appends a message to the current line in the CLI. Used after Out(newline=False)
        to append a message to the CLI.

        Args:
            - message (str): The message
            - finish (bool, optional): Set when the line is complete to start a newline. Defaults to True.
        """
        if finish:
            print(f"{message}{C.End}", flush=True)
        else:
            print(f"{message}", end="", flush=True)

    def print(self, message: str):
        """Prints the given message to the CLI without indentation

        Args:
            - message (str): Message to write to the CLI
        """
        print(message)

    def inc(self):
        """Increment the console indentation level by one"""
        self.indentationLevel += 1

    def dec(self):
        """Decrement the console indentation level by one"""
        self.indentationLevel -= 1
        if self.indentationLevel < 0:
            self.indentationLevel = 0

    def add_command(self, command: str, function: Callable):
        if command in self.commands.keys():
            self.log.debug(f"Command {command} already in list of console commands! Skipping..")

        self.commands.update({command: function})
        self.log.debug(f'Added "{ command }" to command list')

    def process_input(self, input: str):
        # Split input into its parts
        arguments = input.split(" ")
        arguments = [i.strip() for i in arguments]

        for command in self.commands.keys():
            if command == arguments[0]:
                self.log.debug(f"Executing command '{command}' at {str(self.commands[command])}")
                self.log.debug(f"Using arguments: {str(arguments)}")
                self.commands[command](self.parent_app, arguments[1:])
                break
        else:
            self.write("Unknown command, but those are known:")
            self.inc()
            self.write(f"{', '.join(self.commands.keys())}")
            self.dec()
