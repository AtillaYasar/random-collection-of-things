import tkinter as tk
import colorsys

default_text = '''
Well, let's be frank here. MIRI didn't solve AGI alignment and at least knows that it didn't. Paul Christiano's incredibly complicated schemes have no chance of working in real life before DeepMind destroys the world. Chris Olah's transparency work, at current rates of progress, will at best let somebody at DeepMind give a highly speculative warning about how the current set of enormous inscrutable tensors, inside a system that was recompiled three weeks ago and has now been training by gradient descent for 20 days, might possibly be planning to start trying to deceive its operators.

Management will then ask what they're supposed to do about that.

Whoever detected the warning sign will say that there isn't anything known they can do about that.  Just because you can see the system might be planning to kill you, doesn't mean that there's any known way to build a system that won't do that.  Management will then decide not to shut down the project - because it's not certain that the intention was really there or that the AGI will really follow through, because other AGI projects are hard on their heels, because if all those gloomy prophecies are true then there's nothing anybody can do about it anyways.  Pretty soon that troublesome error signal will vanish.

When Earth's prospects are that far underwater in the basement of the logistic success curve, it may be hard to feel motivated about continuing to fight, since doubling our chances of survival will only take them from 0% to 0%.

That's why I would suggest reframing the problem - especially on an emotional level - to helping humanity die with dignity, or rather, since even this goal is realistically unattainable at this point, die with slightly more dignity than would otherwise be counterfactually obtained.

Consider the world if Chris Olah had never existed.  It's then much more likely that nobody will even try and fail to adapt Olah's methodologies to try and read complicated facts about internal intentions and future plans, out of whatever enormous inscrutable tensors are being integrated a million times per second, inside of whatever recently designed system finished training 48 hours ago, in a vast GPU farm that's already helpfully connected to the Internet.

It is more dignified for humanity - a better look on our tombstone - if we die after the management of the AGI project was heroically warned of the dangers but came up with totally reasonable reasons to go ahead anyways.

Or, failing that, if people made a heroic effort to do something that could maybe possibly have worked to generate a warning like that but couldn't actually in real life because the latest tensors were in a slightly different format and there was no time to readapt the methodology.  Compared to the much less dignified-looking situation if there's no warning and nobody even tried to figure out how to generate one.
'''[1:-1]

def int_to_hexadecimal(number):
    """Takes an integer between 0 and 255, returns the hexadecimal representation."""

    if number < 0 or number > 255:
        raise ValueError('must be between 0 and 255')

    digits = list("0123456789ABCDEF")
    first = number // 16
    second = number%16
    return ''.join(map(str,(digits[first],digits[second])))

def hsv_to_hexcode(hsv, scale=1):
    """Takes a list of 3 numbers, returns hexcode.

    Divides each number by scale, multiplies by 255, rounds it, converts to 2-digit hex number

    Scale divides each number to make it a fraction.
        (So with scale=500, you can pass numbers between 0 and 500, instead of between 0 and 1.)
    """
    numbers = list(map(lambda n:n/scale, (hsv)))
    rgb = colorsys.hsv_to_rgb(*numbers)
    hexcode = '#' + ''.join(map(lambda n:int_to_hexadecimal(int(n*255)), rgb))
    return hexcode

def analyze(widget):
    # start of word highlighting, inspired by https://twitter.com/InternetH0F/status/1656853851348008961

    # helper functions
    def convert_range(pair):
        """take normal range, return tkinter range"""
        assert len(pair) == 2
        assert len(pair[0]) == 2
        assert len(pair[1]) == 2
        def conv(tup):
            line, char = tup
            string = f'{line+1}.{char}'
            return string

        str1, str2 = map(conv, pair)
        tkinter_range = (str1, str2)

        return tkinter_range
    def get_hsv(color):
        rgb = tuple((c/65535 for c in widget.winfo_rgb(color)))
        hsv = colorsys.rgb_to_hsv(*rgb)
        return hsv
    def change_color(color, changers):
        # changers should be 3 callables, each taking a number between 0 and 1, and returning a number between 0 and 1
        # will be applied to hue/saturation/value, in that order.
        # (to make darker, reduce value)
        hsv = get_hsv(color)
        new_hsv = tuple(map(lambda n:changers[n](hsv[n]), range(3)))
        new_color = hsv_to_hexcode(new_hsv, scale=1)
        return new_color

    # define "changers". currently, it will keep everything the same, and just make the text darker.
    def third_fg_changer(n):
        # make darker
        n = max(0.1, n/2)
        return n
    fg_changers = [
        lambda n:n,
        lambda n:n,
        third_fg_changer,
    ]
    bg_changers = [
        lambda n:n,
        lambda n:n,
        lambda n:n,
    ]

    to_analyze = widget.get(1.0, 'end')[:-1]

    # get indices of words
    word_indices = []
    lines = to_analyze.split('\n')
    for line_n, line in enumerate(lines):
        idx = 0
        words = line.split(' ')
        for word in words:
            indices = ( (line_n,idx), (line_n,idx+len(word)) )
            word_indices.append(indices)
            idx += len(word) + 1  # +1 is for the space

    for pair in word_indices:
        ranges = convert_range(pair)
        widget.tag_add('wordstart', ranges[0], ranges[0]+' +2c')


    # apply changes
    fg = widget.cget('fg')
    new_fg = change_color(fg, fg_changers)

    bg = widget.cget('bg')
    new_bg = change_color(bg, bg_changers)

    widget.tag_config('wordstart', foreground=new_fg, background=new_bg)

# test
root = tk.Tk()
text = tk.Text(root)
text.pack()
text.insert(1.0, default_text)
text.config(bg='black', fg='violet')

analyze(text)

root.mainloop()