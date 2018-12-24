'''
To be done:
array
free() and dangling pointers
heap
proper visualisation
'''
from subprocess import *
import subprocess
from time import sleep
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read
import string
import re
import sys
from tabulate import tabulate
import copy

mo=[]
mp=[]
ml=[]
lnc=0
#above are temporarily used lists during data processing
vall=[]#stores variable address
vallv=[]#stores variable value
hista=[]#stores variable, value, address; for each iteration
histac=[]
val=[]
fname=[]#function name
fadd=[]#function address
#below are temporarily used lists and counters during data processing
sv=[]
svc=[]
ap=[]
tsav=[]
tsav2=[]
tsav11=[]
tsav22=[]
cc11=0
counter=0
gn=0
sn=0
an=0

sep = ['+','-','=','*','/',';','[','.']
global_name_list = []
stop = 0
ret = 0
scanf = 0
func = re.compile("\w+ \(((\w+\=\w+), )*(\w+\=\w+)?\)")

my_file = raw_input('Enter C Program Name (with ./ if in local directory): ')

subprocess.call(["gcc","-g","-static",my_file])

p_glob = Popen(['gdb', 'a.out'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
p_glob.stdin.write('info variables\n')
op = p_glob.communicate()
glob_list = op[0].split('\n')

i = glob_list.index('File '+my_file+':') + 1
while glob_list[i]!='':
	x = glob_list[i].split(' ')[1].replace(";",'').replace("\n",'')
	if x[0] == '*':
		x = x[1:]
	name = ''
	for j in range(0,len(x)):
		if x[j] in sep:
			break
		name = name + x[j]
	global_name_list.append(name)
	i += 1
gn=len(global_name_list)
p1 = Popen(['gdb', 'a.out'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
flags = fcntl(p1.stdout, F_GETFL) # get current p.stdout flags
fcntl(p1.stdout, F_SETFL, flags | O_NONBLOCK)

print 'Hit Enter to Begin'

def tr():#function name
	p1.stdin.write('bt\n')
	my_out1 = ''
	sleep(0.5)
	while True:
		try:
			my_out1 = read(p1.stdout.fileno(), 1024)
		except OSError:
			break
	my_out1 = string.replace(my_out1,'(gdb)','').strip()
	my_out2 = my_out1.split(" ")
	s = "p &"+my_out2[2]+"\n"
	p1.stdin.write(s)	
	my_out = ''
	sleep(0.5)
	while True:
		try:
			my_out = read(p1.stdout.fileno(), 1024)
		except OSError:
			break
	my_out = string.replace(my_out,'(gdb)','').strip()
	my_out = my_out.split("\n")
	my_out = [ x.split('=') for x in my_out ]
	for x in range(len(my_out)):
		my_out[x] = [ y.strip() for y in my_out[x] ]
	my_out = filter(lambda a : len(a) == 2,my_out)
	mo = copy.deepcopy(my_out)	
	if len(my_out2)>2:
		if len(mo)>0:
			if len(mo[0])>0:
				mo[0][0]=my_out2[2]
	if len(my_out2)>1:
		return mo

def pdisp(rv):#for further display
	'''
	rv contains [gl,sl,al,ln,fn,tdisp,tsdispv]

	gl: global variables list
	sl: local variables list
	al: argument variables list
	Above lists contain [Variable, Value, Address]

	ln: Line Number (Eg: Line 5)
	fn: Function Name/Address
	tsdispv: pointer display; filtered data

	tdisp: List containing each iteration pointer link structured data
	Display Format should be modified from tdisp
	tdisp contains only pointer data if existing; else there would be an empty list or no correspondence
	'''
	#print rv

def vdisp(gl,sl,al,ln,fname,rv):#Line no.,Function Name/Address, Global, Local and Argument Variables, Pointers Display
	#rv contains gl,sl,al,ln,fname, function can be altered with lesser arguments
	print "\n",ln
	fn=copy.deepcopy(fname)
	if len(fname)>0:
		fn=fname[-1]
	if len(fn)>1:
		print "\nFunction Name: ",fn[0],"\nFunction Address: ",fn[1]
	if len(gl)>0:
		print '\n(Global Variables)'
		heading = ["VARIABLE","VALUE","ADDRESS"]
		print(tabulate(gl,headers=heading,tablefmt="psql"))
	if len(sl)>0:
		print '\n(Stack Frame)'
		heading = ["VARIABLE","VALUE","ADDRESS"]
		print(tabulate(sl,headers=heading,tablefmt="psql"))
	if len(al)>0:
		print '\n(Arguments)'
		heading = ["VARIABLE","VALUE","ADDRESS"]
		print(tabulate(al,headers=heading,tablefmt="psql"))
	if len(rv[6])>0:
		print '\n-Pointers-'
		#heading = ["Line\nNo.","Function\nName/Address\n(Pointer)","Pointer\nName","Variable\nPointed to\nName","Value of\nVariable\nPointed to","Function\nName/Address\n(Variable Pointed to)"]
		heading = ["Line\nNo.","Function\nName/Address\n(Pointer)","Pointer\nName/Address/Value","Variable\nPointed to\nName/Address","Value of\nVariable\nPointed to","Function\nName/Address\n(Variable Pointed to)"]
		print(tabulate(rv[6],headers=heading,tablefmt="psql"))

def vla2(lisag):#updates pointer data
	if len(lisag)>0:
		for i in lisag:
			s = "p *"+i[2]+"\n"
			p1.stdin.write(s)	
		my_out = ''
		sleep(0.1)
		while True:
			try:
				my_out = read(p1.stdout.fileno(), 1024)
			except OSError:
				break
		my_out = string.replace(my_out,'(gdb)','').strip()
		my_out = my_out.split("\n")
		my_out = [ x.split('=') for x in my_out ]
		for x in range(len(my_out)):
			my_out[x] = [ y.strip() for y in my_out[x] ]
		my_out = filter(lambda a : len(a) == 2,my_out)
		mo = copy.deepcopy(my_out)
		tsav30=copy.deepcopy(lisag)
		c1=0
		for j in my_out:
			if len(my_out)>0:
				if len(my_out[c1])>0 and len(tsav30[c1])>0:
					ab=str(mo[c1][1])
					if " " in ab and len(ab)>3:
						ab1=ab.split(" ")
						ab=ab1[2]
					tsav30[c1][6]=ab
					c1+=1
		return tsav30
	return []

def linkall(gl,sl,al,ln,fn):#links pointers and displays it
	global tsav2
	global tsav11
	global cc11
	ck=[]
	c=0
	if len(fn)>0:
		fn=fn[-1]
	a4=[]
	tsav11.append(a4)
	fnc=copy.deepcopy(fn)
	cf=set()
	global tsav
	global tsav22
	for i in gl:
		for j in gl:
			tv=j[2].split(" ")
			tv=tv[2]
			if i[1]==tv:
				ck.append([ln,fn,i[0],i[1],i[2],j[0],j[1],j[2],fn])
			c+=1
	for i in sl:
		for j in gl:
			tv=j[2].split(" ")
			tv=tv[2]
			if i[1]==tv:
				ck.append([ln,fn,i[0],i[1],i[2],j[0],j[1],j[2],fn])
			c+=1
	for i in sl:
		for j in sl:
			tv=j[2].split(" ")
			tv=tv[2]
			if i[1]==tv:
				ck.append([ln,fn,i[0],i[1],i[2],j[0],j[1],j[2],fn])
			c+=1
	for i in sl:
		for j in al:
			tv=j[2].split(" ")
			tv=tv[2]
			if i[1]==tv:
				ck.append([ln,fn,i[0],i[1],i[2],j[0],j[1],j[2],fn])
			c+=1
	for i in al:
		for j in gl:
			tv=j[2].split(" ")
			tv=tv[2]
			if i[1]==tv:
				cf.add(i[0])
				ck.append([ln,fn,i[0],i[1],i[2],j[0],j[1],j[2],fn])
			c+=1
	for i in al:
		for j in sl:
			tv=j[2].split(" ")
			tv=tv[2]
			if i[1]==tv:
				cf.add(i[0])
				ck.append([ln,fn,i[0],i[1],i[2],j[0],j[1],j[2],fn])
	for i in al:
		for j in al:
			tv=j[2].split(" ")
			tv=tv[2]
			if i[1]==tv:
				cf.add(i[0])
				ck.append([ln,fn,i[0],i[1],i[2],j[0],j[1],j[2],fn])
	for i in gl:
		tsav22.append(["","","","","",i[0],i[1],i[2],fn])
	for i in sl:
		tsav22.append(["","","","","",i[0],i[1],i[2],fn])
	for i in al:
		tsav22.append(["","","","","",i[0],i[1],i[2],fn])	
	s1=''
	s2=[]
	if len(tsav)>0:
		tsav14=copy.deepcopy(tsav11)
		if len(tsav11[-1])==0:
			tsav12=copy.deepcopy(tsav11)
			cz=0
			for iz in tsav12:
				if len(iz)==0:
					del tsav12[cz]
				cz+=1
			cz=0
			if len(tsav12)>0:
				tsav14=copy.deepcopy(tsav12)
		ckc2=[]
		for ui in tsav14[-1]:
			z=ui
			n=z[2]
			a=z[3]
			k1=z[4]
			for il in al:
				ac=il[1].split(" ")
				if " " in il[1] and len(il[1])>3:
					ac=ac[2]
				if a==ac[0]:
					lc1=ui
					if fnc!=z[8]:
						cf.add(il[0])
						ckc2.append([ln,fnc,il[0],z[3],z[4],z[5],z[6],z[7],z[8]])
					lc1=[]
				c+=1
		cf=list(cf)
		for i in al:
			if i[0] not in cf:
				if len(str(i[1]))>1 and i[1][1]=='x':
					tsav20=copy.deepcopy(tsav)
					tsav21=tsav20[::-1]
					tc1=1
					for j in tsav21:
						tvc1=j[7].split(" ")
						tvc2=tvc1[2]
						if tvc2==i[1]:
							ckc2.append([ln,fnc,i[0],i[1],i[2],j[5],j[6],j[7],j[8]])
							tc1=0
							break
					if tc1==1:
						for j in tsav22[::-1]:
							tvc1=j[7].split(" ")
							tvc2=tvc1[2]
							if tvc2==i[1]:
								ckc2.append([ln,fnc,i[0],i[1],i[2],j[5],j[6],j[7],j[8]])
								tc1=0
								break
		s=set()
		cf=[]
		for t in ckc2:
			gcv=t[2:3]
			w=tuple(sorted(gcv))
			if not w in s:
				cf.append(t[2])
				ck.append(t)
				s.add(w)
		ckc2=[]
	if len(ck)>0:
		for i in ck:
			if len(i)>0:
				tsav.append(i)
				tsav11[cc11].append(i)
	fr=[]
	if len(tsav11)>0:
		fr=vla2(tsav11[-1])
		tsav11.pop()
		tsav11.append(fr)
	tsav2=copy.deepcopy(tsav)
	z=[]
	tsavd=[]
	cc11+=1
	tsdisp=copy.deepcopy(tsav11[-1])
	tsdispv=[]
	if len(tsdisp)>0:
		for i in tsdisp:
			tsdispv.append([i[0],i[1][0],i[2],i[5],i[6],i[8][0]])
			#tsdispv.append(["",i[1][1],"","","",i[8][1]])
			tsdispv.append(["",i[1][1],i[4],i[7],"",i[8][1]])
			tsdispv.append(["","",i[3],"","",""])
			tsdispv.append(["-----","","","","",""])
	return [gl,sl,al,ln,fn,tsav11,tsdispv]
	
def output(p1,flag):#display (stack frame, arguments..)
	global stop
	my_out = ''
	sleep(0.1)
	while True:
		try:
			my_out = read(p1.stdout.fileno(), 1024)
		except OSError:
			# the os throws an exception if there is no data
			# print '[No more data]'
			break
	if "scanf" in my_out:
		global scanf
		scanf = 1
	if "printf" in my_out:
		print "Output from printf is:"
		op_string = my_out[11:len(my_out)-9].split(",")
		i = 0
		i_args = 1
		format_string = op_string[0]
		format_string = string.replace(format_string,'"','')
		while i<len(format_string):
			if format_string[i] == '%':
				temp = 'print '+op_string[i_args]+'\n'
				p1.stdin.write(temp)
				output(p1,5)
				i_args += 1
				i +=2
				continue
			sys.stdout.write(format_string[i])
			i += 1
		print '\n'		
	global ret
	m = func.match(my_out)
	if m is not None:
		my_out = m.group()
		func_name,my_out = my_out.split('(')
		my_out = my_out.split(')')[0]
		my_out = my_out.split(',')
		func_name = string.replace(func_name,' ','')
		fname.append([func_name])
		var_tab = []
		for arg in my_out:
			var_tab.append(arg.strip().split("="))
		if len(var_tab)>1:
			print "-----------\nFunction '",func_name,"' called, with Arguments:"
			heading = ["ARGUMENT","VALUE"]
			print(tabulate(var_tab,headers=heading,tablefmt="psql"))
		else:
			print "Function '",func_name,"' called."
		mp = copy.deepcopy(my_out)	
		s = "p &"+func_name+"\n"
		p1.stdin.write(s)	
		my_out = ''
		sleep(0.1)
		while True:
			try:
				my_out = read(p1.stdout.fileno(), 1024)
			except OSError:
				break
		my_out = string.replace(my_out,'(gdb)','').strip()
		my_out = my_out.split("\n")
		my_out = [ x.split('=') for x in my_out ]
		for x in range(len(my_out)):
			my_out[x] = [ y.strip() for y in my_out[x] ]
		my_out = filter(lambda a : len(a) == 2,my_out)
		mo = copy.deepcopy(my_out)	
		mo[0][0]=func_name
		print "Function Name/Address: ",mo
		mo = []
		return
	if 'result = 0' in my_out:
		stop = 1
		return
	if 'Value returned is' in my_out:
		my_out = my_out.split(' ')
		print '\n\nReturn Value:',my_out[len(my_out)-2].split('\n')[0],'\n'
		ret = 0
		return
	if 'return' in my_out:
		ret = 1
		return 
	if flag == 6:
		my_out = my_out.split('=')[1]
		my_out = string.replace(my_out,'(gdb)','')
		my_out = string.replace(my_out,'\n','')
		return my_out
	if flag == 5:
		my_out = my_out.split('=')[1]
		my_out = string.replace(my_out,'(gdb)','')
		my_out = string.replace(my_out,'\n','')
		sys.stdout.write(my_out)
	elif flag == 2:
		my_out = string.replace(my_out,'(gdb)','')
		my_out = my_out.split(' ')
		my_out = my_out[:2]
		ln=' '.join(my_out)
		#print "\n"
		#print ln
		global lnc
		lnc=ln
	elif flag == 1:
		if my_out != 'No symbol table info available.\n(gdb) ':
			my_out = string.replace(my_out,'(gdb)','')
			#print '\n(Stack Frame)'
			my_out = my_out.split('\n')
			my_out = [ x.split('=') for x in my_out ]
			for x in range(len(my_out)):
				my_out[x] = [ y.strip() for y in my_out[x] ]
			prev = 0
			if len(my_out)==2 and len(my_out[0])==1:
				print " "
			else:	
				for x in range(len(my_out)):
					if len(my_out[x])!= 2:
						if len(my_out[x]) == 1:
							my_out[prev][1] += my_out[x][0]
					else:
						prev = x
				my_out = filter(lambda a: len(a) ==2, my_out)
				mp = copy.deepcopy(my_out)
				#heading = ["VARIABLE","VALUE"]
				#print(tabulate(my_out,headers=heading,tablefmt="psql"))
				global sn
				sn=len(my_out)
				for i in mp:
					vallv.append(i)
				mp = []
				mo = []
				ml = []
				mp = copy.deepcopy(my_out)	
				for j in my_out:
					s = "p &"+j[0]+"\n"
					p1.stdin.write(s)	
				my_out = ''
				sleep(0.2)
				while True:
					try:
						my_out = read(p1.stdout.fileno(), 1024)
					except OSError:
						break
				my_out = string.replace(my_out,'(gdb)','').strip()
				my_out = my_out.split("\n")
				my_out = [ x.split('=') for x in my_out ]
				for x in range(len(my_out)):
					my_out[x] = [ y.strip() for y in my_out[x] ]
				my_out = filter(lambda a : len(a) == 2,my_out)
				mo = copy.deepcopy(my_out)	
				c = 0
				for i in mp:
					a = mo[c][1]
					ml.append([i[0],a])
					c+=1
				c = 0
				#print ml
				for i in ml:
					vall.append(i)
		else:
			stop =1
	elif flag == 4:
		my_out = string.replace(my_out,'(gdb)','').strip()
		if my_out != "No arguments.":
			#print "\n(Arguments)"
			my_out = my_out.split("\n")
			my_out = [ x.split('=') for x in my_out ]
			for x in range(len(my_out)):
				my_out[x] = [ y.strip() for y in my_out[x] ]
			my_out = filter(lambda a : len(a) == 2,my_out)
			mp = []
			mo = []
			ml=[]
			mp = copy.deepcopy(my_out)
			if my_out>0:
				#heading = ["ARGUMENT","VALUE"]
				#print(tabulate(my_out,headers=heading,tablefmt="psql"))
				print ""
			global an
			an=len(my_out)
			for i in mp:
				vallv.append(i)
			for j in my_out:
				s = "p &"+j[0]+"\n"
				p1.stdin.write(s)	
			my_out = ''
			sleep(0.1)
			while True:
				try:
					my_out = read(p1.stdout.fileno(), 1024)
				except OSError:
					break
			my_out = string.replace(my_out,'(gdb)','').strip()
			my_out = my_out.split("\n")
			my_out = [ x.split('=') for x in my_out ]
			for x in range(len(my_out)):
				my_out[x] = [ y.strip() for y in my_out[x] ]
			my_out = filter(lambda a : len(a) == 2,my_out)
			mo = copy.deepcopy(my_out)	
			c = 0
			for i in mp:
				a = mo[c][1]
				ml.append([i[0],a])
				c+=1
			c = 0
			#print ml
			for i in ml:
				vall.append(i)

p1.stdin.write('break main\n')
output(p1,0)
p1.stdin.write('run\n')
output(p1,0)

while True:
	inp = raw_input()
	mo=[]
	mp=[]
	ml=[]
	if(inp=='exit' or inp=='quit' or inp=='q'):
		break
	p1.stdin.write('step\n')
	counter+=1
	hista.append([str(counter)])
	if scanf == 1:
		print "Enter input for scanf:\n"
		p1.stdin.write(str(input())+'\n')
		scanf = 0
	output(p1,0)
	p1.stdin.write('info line\n')
	output(p1,2)
	#print '\n(Global Variables)'
	var_tab=[]
	#heading = ["VARIABLE","VALUE"]
	for i in global_name_list:
		p1.stdin.write('print '+i+'\n')
		var_tab.append([i,output(p1,6)])
	#print(tabulate(var_tab,headers=heading,tablefmt="psql"))
	vallv = copy.deepcopy(var_tab)
	for i in mp:
		vallv.append(i)
	mp = copy.deepcopy(var_tab)		
	for j in var_tab:
		s = "p &"+j[0]+"\n"
		p1.stdin.write(s)
	my_out = ''
	sleep(0.1)
	while True:
		try:
			my_out = read(p1.stdout.fileno(), 1024)
		except OSError:
			break
	my_out = string.replace(my_out,'(gdb)','').strip()
	my_out = my_out.split("\n")
	my_out = [ x.split('=') for x in my_out ]
	for x in range(len(my_out)):
		my_out[x] = [ y.strip() for y in my_out[x] ]
	my_out = filter(lambda a : len(a) == 2,my_out)
	mo=copy.deepcopy(my_out)
	c = 0
	for i in mp:
		a = mo[c][1]
		ml.append([i[0],a])
		c+=1
	c = 0
	#print ml
	vall = copy.deepcopy(ml)
	mo=[]
	mp=[]
	ml=[]
	p1.stdin.write('info locals\n')
	output(p1,1)
	p1.stdin.write('info args\n')
	output(p1,4)
	fname.extend(tr())
	sv.extend([counter])
	sv.extend(fname)
	svc.extend(sv)
	sv=[]
	cl=0
	for u in vallv:
		val.append([u[0],u[1],vall[cl][1]])
		cl+=1
	cl=0	
	hista.append(fname)
	hista.append(val)
	val=[]
	if gn>0:
		hista[2].insert(0,["#G"])
	if sn>0:
		hista[2].insert(gn+1,["#S"])
	if an>0:
		hista[2].insert(gn+sn+2,["#A"])
	gvp1=[]
	svp1=[]
	avp1=[]
	gvc1=0
	svc1=0
	avc1=0
	for i in hista[2]:
		if gvc1<=gn:
			gvp1.append(i)
			gvc1+=1
		elif svc1<=sn:
			svp1.append(i)
			svc1+=1
		elif avc1<=an:	
			avp1.append(i)
			avc1+=1
	if len(gvp1)>0:
		del gvp1[0]
	if len(svp1)>0:
		del svp1[0]
	if len(avp1)>0:
		del avp1[0]
	rv=linkall(gvp1,svp1,avp1,lnc,fname)
	vdisp(gvp1,svp1,avp1,lnc,fname,rv)
	pdisp(rv)
	lnc=0
	sn=0
	an=0
	histac.append(hista)
	hista=[]
	fname=[]
	if stop == 1:
		break
	if ret == 1:
		p1.stdin.write('finish\n')
		output(p1,3)
	print '\nHit Enter to Continue, exit/quit to stop\n'
	
	


