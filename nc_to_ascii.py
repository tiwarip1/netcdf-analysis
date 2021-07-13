import subprocess
import os,re

# nlist = ["2018_12_22_05_327_000.nc", "2018_10_29_07_tin_000.nc", "2017_12_31_06_Sr327_002.nc"]
nlist = ["2017_02_06_01_SnO_000.nc",]
keep_comments = ["ALockin","BLockin","CLockin","DLockin","EVoltage","FVoltage","GVoltage","HVoltage"]
reject_var = ["ALockin","BLockin","CLockin","DLockin"]
for name in os.listdir():   # nlist
   if name[-2:]=='nc':
    if name < "2017_05_18_03_Sr327_001.nc":
      fout = open(name[0:-3]+'.dat','w')
      # txt = subprocess.Popen(["ncdump","-v","CurrentT,CurrentH",name], stdout=subprocess.PIPE, text=True)
      txt = subprocess.Popen(["ncdump",name], stdout=subprocess.PIPE, text=True)
      result = txt.communicate()
      outstr = '#'+name
      cname = '# CurrentT,CurrentH'
      dlist = result[0].split(';')
      indata = 0
      dvars = []
      vars = []; vindex = 0 
      for i in range(0,len(dlist)):
         if dlist[i].find('Active ')>0:
            comment = 0; reject = 0
            if dlist[i].find('\"T\"')>3:
               for cmt in keep_comments:
                  if dlist[i].find(cmt)>0:
                     comment=1
               if comment==1:
                  fout.write('#'+dlist[i-1][3:].split(':')[0] + dlist[i-1][3:].split('=')[1]+'\n')
               for rjt in reject_var:
                  if dlist[i].find(rjt)>0:
                     reject=1
               if reject==0: 
                  dvars.append( dlist[i][3:].split(':')[0] )
                  cname = cname +','+ dlist[i-1][3:].split(':')[0] # + dlist[i-1][3:].split('=')[1]
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
         if indata==1:
            for var in dvars:
               if (dlist[i].find(var)>0):
                  line = re.sub('\n','',dlist[i])
         #         fout.write('# '+str(vindex) + ' ' + line.split('=')[0] + '\n')
                  vars.append(line.split('=')[1].split(','))
                  vindex += 1

      fout.write(outstr+ '\n')
      fout.write(cname + '\n')
      print (name)
      try:
          print (len(vars),len(vars[0]))
      except:
          print ("no data points taken?")
      for i in range(0,len(Tlist)):
          outstr = '{:3.6f} {:3.6f} '.format(float(Tlist[i]),float(Hlist[i]))
          for j in range(0,vindex): 
             try:
                voltage = float(vars[j][i])
                outstr = outstr + '{:3.6f} '.format( voltage )
             except:
                outstr = outstr + ' - '
          fout.write(outstr + '\n')
      fout.close()
