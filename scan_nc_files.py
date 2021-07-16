import subprocess
import os,re

def list_files_content(directory = '../Lingyun-data/'):
   
   for name in os.listdir(directory):   # nlist
      if name[-2:]=='nc':
         txt = subprocess.Popen(["ncdump","-v","CurrentT,CurrentH",name], stdout=subprocess.PIPE, text=True,cwd=directory)
         result = txt.communicate()
         outstr = name
         dlist = result[0].split(';')
         start = 0
         indata = 0
         for i in range(0,len(dlist)):
            if (start==0)&(dlist[i].find('ALockin')>1):
               start=1
            if (start==1)&(dlist[i].find('Active ')>3):
               if dlist[i].find('\"T\"')>3:
                  outstr = outstr+','+ dlist[i-1][3:].split(':')[0] + dlist[i-1][3:].split('=')[1]
            if dlist[i].find('Comments')>3:
               outstr = outstr+','+dlist[i][4:]
            if (indata==0)&('data:' in dlist[i]):
               indata=1  
            if (dlist[i].find('CurrentT')>0)&(indata==1):
               line = re.sub('\n','',dlist[i])
               Tlist = line.split('=')[1].split(',')
               FirstT = float(Tlist[0])
               LastT = float(Tlist[-1])
               Tstr = ', FirstT = {:4.1f} mK, LastT = {:4.1f} mK'.format(FirstT,LastT)
               outstr = outstr+Tstr
            if (dlist[i].find('CurrentH')>0)&(indata==1):
               line = re.sub('\n','',dlist[i])
               Hlist = line.split('=')[1].split(',')
               FirstH = float(Hlist[0])
               LastH = float(Hlist[-1])
               Hstr = ', FirstH = {:4.1f} T, LastH = {:4.1f} T'.format(FirstH,LastH)
            outstr = outstr+Hstr

      return outstr
