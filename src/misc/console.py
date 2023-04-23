"""Console proxy

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Dict

from misc.colors import Color
from misc.logger import Logger

@dataclass
class Console():
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
        print('  ' * (self.indentationLevel), end='', flush=True)
        print('> ', end='', flush=True)
        return input()

    def write(self, message: str, color: Color = Color.End, newline = True):
        """Writes the given message to the CLI with the given indentation level

        Args:
            - message (str): Message to write to the CLI
        """
        print('  ' * (self.indentationLevel), end='', flush=True)
        print('  ', end='', flush=True)
        if newline:
            print(f'{color}{message}{Color.End}')
        else:
            print(f'{color}{message}', end='', flush=True)

        # self.log.info(f'[ Console ] {message}')

    def append(self, message: str, finish = True):
        """Appends a message to the current line in the CLI. Used after Out(newline=False)
        to append a message to the CLI.

        Args:
            - message (str): The message
            - finish (bool, optional): Set when the line is complete to start a newline. Defaults to True.
        """
        if finish:
            print(f'{message}{Color.End}', flush=True)
        else:
            print(f'{message}', end='', flush=True)

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
            self.log.debug(f'Command {command} already in list of console commands! Skipping..')

        self.commands.update({command: function})
        self.log.debug(f'Added "{ command }" to command list')

    def process_input(self, input: str):
        possibleCommands = []
        # Get all possible commands for the user's input
        for command in self.commands:
            if command.find(input) != -1:
                possibleCommands.append(command)

        if len(possibleCommands) == 0:
            # Check if the command is already found in the user's input
            for command in self.commands:
                if input.find(command) == 0:
                    possibleCommands.append(command)

        if len(possibleCommands) == 0:
            return self.write(f'{Color.Fail}Unknown command!')

        elif len(possibleCommands) == 1:
            # TODO: Remove this hack to get the arguments as list
            arguments = input.removeprefix(possibleCommands[0]).split(' ')[1:]
            arguments = [i.strip() for i in arguments]
            self.log.debug(f'Executing command "{ possibleCommands[0] }" at { str(self.commands[possibleCommands[0]]) }')
            self.log.debug(f'Using arguments: { str(arguments) }')
            self.commands[possibleCommands[0]](self.parent_app, arguments)
        else:
            self.write('Unknown command, but those are known:')
            self.write(f'- {", ".join(possibleCommands)}')
