
import sys
from random import randint


def checkExpressions(line, vars):
	args = line.split(" ")
	for pos, arg in enumerate(args):
		if arg.startswith("%var"):
			args[pos] = str(vars[arg[5:-1]])

	return args


def checkIf(val1, val2, operator):
	if operator == "==":
		if str(val1) == str(val2):
			return True
		else:
			return False
	if operator == "!=":
		if str(val1) != str(val2):
			return True
		else:
			return False
	if operator == ">":
		if int(val1) > int(val2):
			return True
		else:
			return False
	if operator == "<":
		if int(val1) < int(val2):
			return True
		else:
			return False
	if operator == ">=":
		if int(val1) >= int(val2):
			return True
		else:
			return False
	if operator == "<=":
		if int(val1) <= int(val2):
			return True
		else:
			return False
	raise Exception('Unknown comparasion operator encountered.')



def runCode(code, positions, vars2):
	codeLen = len(code)
	curLine = 0
	loopComp = {}
	vars = vars2
	while curLine < codeLen:

		args = code[curLine].split(" ")

		for pos, arg in enumerate(args):
			if '\t' in arg:
				args[pos] = arg.replace("\t", '')
			if '\\n' in arg:
				args[pos] = arg.replace("\\n", '\n')
			if arg.startswith('%var'):
				if arg[5:-1].startswith("%var"):
					var2 = arg[5:-1]
					args[pos] = str(vars[vars[var2[5:-1]]])
				else:
					args[pos] = str(vars[arg[5:-1]])
			if arg.startswith('%' + "chr"):
				args[pos] = str(chr(vars[arg[5:-1]]))
			if arg.startswith('%' + "ascii"):
				args[pos] = str(ord(vars[arg[7:-1]]))
			if arg.startswith("%" + "eval"):
				args[pos] = str(eval(arg[6:-1]))
			if arg.startswith("%" + "len"):
				args[pos] = str(len(vars[arg[5:-1]]))

		if args[0] == "println":
			args.pop(0)
			print(str(' '.join(args)))

		if args[0] == "print":
			args.pop(0)
			print(str(' '.join(args)), end='')

		if args[0] == "define":
			if args[3] == "text":
				vars[args[1]] = "Empty String"
				vars[args[1] + "_type"] = "text"
			elif args[3] == "number":
				vars[args[1]] = 0
				vars[args[1] + "_type"] = "number"

		if args[0] == "set":
			if args[1] == "text":
				if vars[args[3] + "_type"] == "text":
					x = 0
					var = args[3]
					for x in range(5):
						args.pop(0)
					vars[var] = ' '.join(args)
			elif args[1] == "number":
				if vars[args[3] + "_type"] == "number":
					x = 0
					var = args[3]
					for x in range(5):
						args.pop(0)
					vars[var] = int(eval(' '.join(args)))
		if all(elem in args  for elem in ['get', 'input', 'and', 'save', 'it', 'as']):
			if args[6] == "text":
				x = input()
				if len(x) > 0:
					vars[args[8]] = x
				else:
					vars[args[8]] = "No Input"

			elif args[6] == "number":
				x = input()
				if len(x) > 0:
					vars[args[8]] = int(x)
				else:
					vars[args[8]] = 0
		if args[0] == "goto":
			curLine = positions[args[1]]

		if all(elem in args  for elem in ['check', 'if']):
			if args[3] not in ['not', 'exists']:
				if not checkIf(args[2], args[4], args[3]):
					curLine = positions[curLine] 
			elif args[3] == "exists":
				if not args[2] in vars.keys():
					curLine = positions[curLine]
			elif args[3] == "not":
				#print(vars)
				if args[2] in vars.keys():
					curLine = positions[curLine]

		if all(elem in args  for elem in ['stop', 'running']):
			if checkIf(loopComp[curLine][0], loopComp[curLine][1], loopComp[curLine][2]):
				curLine = positions[curLine]-1

		if all(elem in args  for elem in ['run', 'this', 'while']):
			if not checkIf(args[3], args[5], args[4]):
				curLine = positions[curLine]
			else:
				loopComp[positions[curLine]] = [str(args[3]), str(args[5]), str(args[4])]

		if all(elem in args  for elem in ['trim']):
			if args[1] in vars.keys():
				vars[args[1]] = vars[args[1]][int(args[2]):int(args[3])]

		if all(elem in args  for elem in ['combine']):
			if args[1] in vars.keys():
				varT = args[1]
				args.pop(0)
				args.pop(0)
				vars[varT] = vars[varT] + str(' '.join(args)).replace('\n', '')

		if all(elem in args  for elem in ['generate', 'random', 'between']):
			vars[args[10]] = str(randint(int(args[3]), int(args[5])))

		#print(vars)
		curLine +=1








def find_loops_and_ifs(code):
	positions = {}
	tmpIfs = []
	tmpLoops = []
	for pos, line in enumerate(code):
		line2 = line.replace("\n", "")
		line2 = line2.replace("\t", "")
		args = line2.split(" ")
		try:
			chr1 = args[0]
			if chr1[0] == ':':
				positions[chr1[1:]] = pos
			if all(elem in args  for elem in ['check', 'if']):
				tmpIfs.append(pos)
			if all(elem in args  for elem in ['end', 'statement']):
				if len(tmpIfs) != 0:
					lastPos = tmpIfs.pop()
					positions[pos] = lastPos
					positions[lastPos] = pos
			if all(elem in args  for elem in ['run', 'this', 'while']):
				tmpLoops.append(pos)
			if all(elem in args  for elem in ['stop', 'running']):
				if len(tmpLoops) != 0:
					lastPos = tmpLoops.pop()
					positions[pos] = lastPos
					positions[lastPos] = pos
		except:
			pass
	return positions


def setup(code, vars):

	splitCode = code.split("\n")
	pos = find_loops_and_ifs(splitCode)
	codeResult = runCode(splitCode, pos, vars)
	sys.exit()


if len(sys.argv) >= 2:
	code = open(sys.argv[1], "r").read()
	args = sys.argv
	vars = {}
	args.pop(0)
	args.pop(0)
	for pos, arg in enumerate(args):
		vars['argv' + str(pos+1)] = arg
		vars['argv' + str(pos+1) + "_type"] = "text"
	setup(code, vars)