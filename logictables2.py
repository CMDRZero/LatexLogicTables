import sys
from time import sleep
from threading import Thread
import os

def maketable(ary, merge = 0, nconcl = 0):
    rows = len(ary)
    cols = len(ary[0])

    pre = '%Auto generated table begin:\n\\begin{center}\n\\begin{tabular}{'
    if merge != 0:
        top = ' '.join(['c' for i in range(merge)]) \
            + ' || ' + ' | '.join(['c' for c in range(cols-merge-nconcl)]) \
            + ((' || ' + ' | '.join(['c' for c in range(nconcl)])) if nconcl else '')
        frow,ary = ary[0],ary[1:]
        post = '}\n'
        fbody = ' & '.join(['$ '+str(col)+' $' for col in frow])
        fbody += '\\\\ \\hline\\hline\n'
        body = ' \\\\ \\hline\n'.join([' & '.join(['$ '+str(col)+' $' for col in row]) for row in ary])
        postbody = '\n\\end{tabular}\n\\end{center}\n%Auto generated table end'
        return pre + top + post + fbody + body + postbody
    else:
        top = ' | '.join(['c' for c in range(cols)])
        post = '}\n'
        body = ' \\\\ \n\\hline\n'.join([' & '.join(['$ '+str(col)+' $' for col in row]) for row in ary])
        postbody = '\n\\end{tabular}\n\\end{center}\n%Auto generated table end'
        return pre + top + post + body + postbody


ands = ['and', '^', '&', '&&', '*']
ors = ['or', 'v', '|', '||', '+']
impl = ['only if', 'then', 'impl', 'implies', '->', '-->']
reimpl = ['if', '<-', '<--']
bicond = ['if and only if', '<->', '<-->', '==', 'is']
nots = ['not', '!', '-']

l_and = '\\wedge'
l_or = '\\vee'
l_impl = '\\rightarrow'
l_reimpl = '\\leftarrow'
l_bicond = '\\leftrightarrow'
l_not = '\\neg'


def parseexpr(txt):
    words = ' '.join(txt.split())
    for word in bicond:
        words=words.replace(word, l_bicond)
    for word in impl:
        words=words.replace(word, l_impl)
    for word in ands:
        words=words.replace(word, l_and)
    for word in ors:
        words=words.replace(word, l_or)
    for word in reimpl:
        words=words.replace(word, l_reimpl)
    for word in nots:
        words=words.replace(word, l_not)
    return words

def then(a, b):
    if not a:
        return 1
    else:
        return b

def evalexpr(txt):
    words = txt.split()
    out = []
    buf = []
    paren = 0
    for word in words:
        if paren == 0:
            if word == '(':
                paren = 1
            else:
                out.append(word)
        else:
            if word == '(':
                paren += 1
            elif word == ')':
                paren -= 1
                if paren == 0:
                    out.append(evalexpr(' '.join(buf)))
                    buf = []
            else:
                buf.append(word)
    words = ' '.join(out)
##    print(f'Stiched as {words=}')
    for l in [0, 1]:
        words = words.replace(f'{l_not} {l}', str(0 + (not l)))
    for l in [0, 1]:
        for r in [0, 1]:
            words = words.replace(f'{l} {l_and} {r}', str(l and r))
    for l in [0, 1]:
        for r in [0, 1]:
            words = words.replace(f'{l} {l_or} {r}', str(l or r))
    for l in [0, 1]:
        for r in [0, 1]:
            words = words.replace(f'{l} {l_impl} {r}', str(then(l, r)))
    for l in [0, 1]:
        for r in [0, 1]:
            words = words.replace(f'{l} {l_reimpl} {r}', str(then(r, l)))
    for l in [0, 1]:
        for r in [0, 1]:
            words = words.replace(f'{l} {l_bicond} {r}', str(int(l == r)))
    
    return words

def Tab(exprs, words, nconcl = 0):
    formulas = [parseexpr(expr) for expr in exprs]
    reses=[]
    reses.append(words+formulas)
    for i in range(2**len(words)):
        cfs = formulas[:]
        vs=[]
        for word in words:
            vs.append(str(1-(i%2)))
            for j in range(len(cfs)):
                cfs[j] = cfs[j].replace(word, vs[-1])
            i >>= 1
        res = [evalexpr(cf) for cf in cfs]
        try:
            for j in range(nconcl):
                j += 1
                if res[-j] == '0' and not sum([1-int(r) for r in res[:-nconcl]]):
                    res[-j]+='*'
        except:
            print(f'{res!r}')
            raise RuntimeError('Something in the processor went wrong')
        reses.append(vs+res)
    return reses

def tune(inp):
    inp = inp.replace('!', ' ! ')
    inp = inp.replace('<->', '<~>')
    inp = inp.replace('<-->', '<~~>')
    inp = inp.replace('->', '~>')
    inp = inp.replace('<-', '<~')
    inp = inp.replace('-', ' - ')
    inp = inp.replace('<~>', ' <-> ')
    inp = inp.replace('<~~>', ' <--> ')
    inp = inp.replace('~>', ' -> ')
    inp = inp.replace('<~', ' <- ')
    inp = inp.replace('(', ' ( ')
    inp = inp.replace(')', ' ) ')
    return inp

inp = None

def monitor_input():
    global inp
    
    while True:
        inp = input().strip()
        if inp == "q":
            os._exit(1)

fName = sys.argv[1] if len(sys.argv) > 1 else input("Program File: ")
if __name__ == "__main__":
    with open(fName) as f:
        verb = "--verb" in sys.argv[2:]
        if "--monitor" in sys.argv[2:]:
            Thread(target=monitor_input).start()
            
            contents = None
            while True:
                sleep(.1)
                f.seek(0)
                newContents = f.read()
                
                if newContents != contents:
                    inp = None
                    contents = newContents

                    if (platform := sys.platform) == 'win32':
                        os.system("cls")
                    elif platform == 'darwin':
                        os.system("clear")
                    else:
                        exit('Unsupported Operating System `' + platform +'`')
                    prems = []
                    alph = []
                    nconcl = None
                    for line in contents.split('\n'):
                        if line == '' or line[0]=='#':
                            continue
                        if line[:3] == '===':
                            nconcl = 0
                            continue
                        if nconcl != None:
                            nconcl += 1
                        inp = tune(line)
                        prems.append(inp)
                        for wd in inp.split():
                            if wd[0] != wd[0].lower() and wd not in alph:
                                alph.append(wd)
                    try:
                        nconcl = nconcl if nconcl else 0
                        print(maketable(Tab(prems, alph, nconcl), len(alph), nconcl))
                    except Exception as e:
                        print('Caught error: '+e)
        else:
            contents = f.read()
            prems = []
            alph = []
            nconcl = None
            for line in contents.split('\n'):
                if line == '' or line[0]=='#':
                    continue
                if line[:3] == '===':
                    nconcl = 0
                    continue
                if nconcl != None:
                    nconcl += 1
                inp = tune(line)
                prems.append(inp)
                for wd in inp.split():
                    if wd[0] != wd[0].lower() and wd not in alph:
                        alph.append(wd)
            try:
                nconcl = nconcl if nconcl else 0
                print(maketable(Tab(prems, alph, nconcl), len(alph), nconcl))
            except Exception as e:
                print('Caught error: '+e)

