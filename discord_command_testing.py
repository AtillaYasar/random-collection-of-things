commands_dict = {}  # stores commands
command_prefix = '-'  # need to type "-{command_name}" to do a command

# for registering a command
def command(func):
    commands_dict[func.__name__] = func
    def wrapper(input_string):
        return func(input_string)
    return wrapper

# technically a listener, i think?
def handle_input(input_string):
    if input_string[0] == command_prefix:  # checks if the input starts with the right prefix,
        command_name = input_string[1:].split(' ')[0]
        command_input = ' '.join(input_string[1:].split(' ')[1:])
        func = commands_dict.get(command_name, None)  # check if the command is registered
        if func != None:
            func(command_input)  # then calls the function using command_input

@command
def _example_command(inp):
    """Registers a command for sending a message.

    Analogous to:
    async def _example_command(ctx, *, inp):
        await ctx.send(f'your input was:{inp}')
    """
    print(f'your input was:{inp}')

# this is like launching the bot and going to discord to type stuff.
def start_loop():
    # for debugging/clarity purposes.
    print(f'command_prefix:{command_prefix}')
    print(f'available commands:')
    print('\n'.join([f'  {key}' for key in commands_dict.keys()]))
    print(f'-'*10)
    print(f'-'*10)
    # the loop simulates typing in discord
    while True:
        i = input()
        handle_input(i)
