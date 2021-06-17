import pexpect
'''
Note that in order to use this class you must include the MtiaeScoreAgent directory provided by Migue
in it's entirety in the App/ dir. The MtiaeScoreAgent directory is included in .gitignore until we 
get permission to include it in a public repository.
'''
class Fingerprint:

    def __init__(self):
        self.checker = pexpect.spawn('wine score2K.exe', encoding='utf-8')
        print("Checker Init")

    def check_xml(self, filename):
        end = '\r\n'
        print("Checker Started")
        self.checker.expect('Enter*')
        print("Enter found")
        self.checker.sendline(filename+end)
        print("Checker Input Given")
        self.checker.expect('Score: ')
        score = self.checker.readline().strip()
        print("Score: ", score)
        return score

