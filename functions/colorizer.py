class Colorizer:
    def __init__(self, text: str):
        self.text = text
        self.text_color_dict = {
            "<gray>": "[0;30m",
            "<red>": "[0;31m",
            "<green>": "[0;32m",
            "<yellow>": "[0;33m",
            "<blue>": "[0;34m",
            "<pink>": "[0;35m",
            "<cyan>": "[0;36m",
            "<white>": "[0;37m",
            "<bg_dblue>": "[0;40m",
            "<bg_orange>": "[0;41m",
            "<bg_lblue>": "[0;42m",
            "<bg_turquoise>": "[0;43m",
            "<bg_gray>": "[0;44m",
            "<bg_indigo>": "[0;45m",
            "<bg_lgray>": "[0;46m",
            "<bg_white>": "[0;47m",
            "<end>": "[0;0m"
        }

    def colorize(self):
        for key, value in self.text_color_dict.items():
            self.text = self.text.replace(key, value)
        colorized_text = f"```ansi\n" + self.text + "```"
        return colorized_text
