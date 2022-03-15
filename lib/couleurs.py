"""Messages colorés sur l'écran"""

class couleurs:
    __VERSION = '0.01'

    @classmethod
    def get_VERSION(self):
        return self.__VERSION

class bcolors:
    OK = '\033[92m' # GREEN
    WARNING = '\033[93m' # YELLOW
    FAIL = '\033[91m' # RED
    INFO = '\033[94m' # BLUE
    RESET = '\033[0m' # RESET COLOR
    BOLD = '\033[1m' # BOLD
    #BLINK = '\033[5m'  # BLINK
    UNDERLINE  = '\033[4m'  # UNDERLINE
    PINK = '\033[95m'  # PINK


class AffichageColor():

    def msg_FAIL(self, msg, bold=False, under=False):
        print(bcolors.FAIL+self.bold(bold)+'-' * 79)
        print(self.under(under)+msg+f'{bcolors.RESET}{bcolors.FAIL}'+self.bold(bold))
        print('-' * 79, f'{bcolors.RESET}')

    def msg_WARNING(self, msg, bold=False, under=False):
        print(bcolors.WARNING + self.bold(bold) + '-' * 79)
        print(self.under(under) + msg + f'{bcolors.RESET}{bcolors.WARNING}' + self.bold(bold))
        print('-' * 79, f'{bcolors.RESET}')

    def msg_OK(self, msg, bold=False, under=False):
        print(bcolors.OK + self.bold(bold) + '-' * 79)
        print(self.under(under) + msg + f'{bcolors.RESET}{bcolors.OK}' + self.bold(bold))
        print('-' * 79, f'{bcolors.RESET}')

    def msg_INFO(self, msg, bold=False, under=False):
        print(bcolors.INFO+self.bold(bold)+'-' * 79)
        print(self.under(under)+msg+f'{bcolors.RESET}{bcolors.INFO}'+self.bold(bold))
        print('-' * 79, f'{bcolors.RESET}')

    def msg_DEBUG(self, msg, bold=False, under=False):
        print(bcolors.PINK+self.bold(bold)+'-' * 79)
        print(self.under(under)+msg+f'{bcolors.RESET}{bcolors.PINK}'+self.bold(bold))
        print('-' * 79, f'{bcolors.RESET}')

    def bold(self, b):
        if b:
            return f'{bcolors.BOLD}'
        return ''

    def under(self, b):
        if b:
            return f'{bcolors.UNDERLINE}'
        return ''


def __main():

    AffichageColor().msg_DEBUG('toto', False, True)
    AffichageColor().msg_OK('toto', False, False)
    AffichageColor().msg_WARNING('toto', True, True)
    AffichageColor().msg_FAIL('toto', True, False)

if __name__ == "__main__": __main()