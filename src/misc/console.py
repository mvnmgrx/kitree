"""Console proxy

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from misc.colors import Color
from misc.logger import Logger

class Console():
    """This class is used to proxy console input and output to the CLI
    """
    IndentationLevel = 0
    Commands = {}
    IsRunning = True
    Log = Logger.Create(__name__)

    @staticmethod
    def In() -> str:
        """Querys the user for input to the CLI

        Returns:
            str: User input
        """
        print('  ' * (Console.IndentationLevel), end='', flush=True)
        print('> ', end='', flush=True)
        return input()

    @staticmethod
    def Out(message: str, color: Color = Color.End, newline = True):
        """Writes the given message to the CLI with the given indentation level

        Args:
            message (str): Message to write to the CLI
        """
        print('  ' * (Console.IndentationLevel), end='', flush=True)
        print('  ', end='', flush=True)
        if newline:
            print(f'{color}{message}{Color.End}')
        else:
            print(f'{color}{message}', end='', flush=True)

        # Console.Log.info(f'[ Console ] {message}')

    @staticmethod
    def Append(message: str, finish = True):
        """Appends a message to the current line in the CLI. Used after Out(newline=False)
        to append a message to the CLI.

        Args:
            message (str): The message
            finish (bool, optional): Set when the line is complete to start a newline. Defaults to True.
        """
        if finish:
            print(f'{message}{Color.End}', flush=True)
        else:
            print(f'{message}', end='', flush=True)

    @staticmethod
    def Print(message: str):
        """Prints the given message to the CLI without indentation

        Args:
            message (str): Message to write to the CLI
        """
        print(message)

    @staticmethod
    def Inc():
        """Increment the console indentation level by one
        """
        Console.IndentationLevel += 1

    @staticmethod
    def Dec():
        """Decrement the console indentation level by one
        """
        Console.IndentationLevel -= 1
        if Console.IndentationLevel < 0:
            Console.IndentationLevel = 0

    @staticmethod
    def AddCommand(command: str, function):
        if command in Console.Commands.keys():
            Console.Log.debug(f'Command {command} already in list of console commands! Skipping..')

        Console.Commands.update({command: function})
        Console.Log.debug(f'Added "{ command }" to command list')

    @staticmethod
    def ProcessInput(input: str):
        possibleCommands = []
        # Get all possible commands for the user's input
        for command in Console.Commands:
            if command.find(input) != -1:
                possibleCommands.append(command)

        if len(possibleCommands) == 0:
            # Check if the command is already found in the user's input
            for command in Console.Commands:
                if input.find(command) == 0:
                    possibleCommands.append(command)

        if len(possibleCommands) == 0:
            return Console.Out(f'{Color.Fail}Unknown command!')
        elif len(possibleCommands) == 1:
            # TODO: Remove this hack to get the arguments as list
            arguments = input.removeprefix(possibleCommands[0]).split(' ')[1:]
            arguments = [i.strip() for i in arguments]
            Console.Log.debug(f'Executing command "{ possibleCommands[0] }" at { str(Console.Commands[possibleCommands[0]]) }')
            Console.Log.debug(f'Using arguments: { str(arguments) }')
            Console.Commands[possibleCommands[0]](arguments)
        else:
            Console.Out('Unknown command, but those are known:')
            Console.Out(f'- {", ".join(possibleCommands)}')
