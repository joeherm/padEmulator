#!/usr/bin/python
#aconnect for midi connections
#F for file menu; m for midi menu; right click to load
import pygame
from pygame import *
from pygame import midi
import easygui as eg
##lower buffer for less latency issues
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()
pygame.midi.init()
pygame.init()
midD=pygame.midi.Input(pygame.midi.get_default_input_id())
##video stuff/load images
pygame.display.set_caption("padEmulator")
screen=display.set_mode((480,480))
pad_down=pygame.image.load("pad-down.jpg")
pad_up=pygame.image.load("pad-up.jpg")
button_imgs=[]
button_imgs.append((pygame.image.load("button00.png"),pygame.image.load("button01.png")))
button_imgs.append((pygame.image.load("button10.png"),pygame.image.load("button11.png")))
button_imgs.append((pygame.image.load("button20.png"),pygame.image.load("button21.png")))
font = pygame.font.Font(None, 20)
pfont = pygame.font.Font(None, 18)
##Class for samples
##sType: 0=single shot; 1=sustain; 2=inf. loop
class Smpl:
	def renderButtons(self,button0,button1,button2):
		screen.blit(button_imgs[0][button0],(self.x-21,self.y-36))
		screen.blit(button_imgs[1][button1],(self.x+10,self.y-36))
		screen.blit(button_imgs[2][button2],(self.x+42,self.y-36))
	def __init__(self,i,f,xp,yp):
		self.sid=i
		self.fid=pygame.mixer.Sound(f)
		self.fid_text=''
		self.fid_text_l=''
		self.isPlaying=False
		self.x=xp+52
		self.y=yp+52
		self.sType=0
		text = font.render("Pad "+str(i), 1, (255, 255, 255))
		textb = pfont.render(self.fid_text, 1, (255, 0, 0))
		screen.blit(pad_up,(self.x,self.y))
		screen.blit(text,(self.x+12,self.y-52))
		screen.blit(textb,(self.x+8,self.y+20))
		self.renderButtons(1,0,0)
	def getSample(self,sFile):
		self.fid.stop()
		if sFile!=None:
			self.fid=pygame.mixer.Sound(sFile)
			self.fid_text_l=sFile
			self.fid_text=sFile[sFile.rfind('/')+1:len(sFile)-4]
			if(len(self.fid_text)>8):
				self.fid_text=self.fid_text[0:8]
			self.stopSample()
	def stopSample(self):
		if self.sType!=0:
			self.fid.stop()
		self.isPlaying=False
		screen.blit(pad_up,(self.x,self.y))
		textb = pfont.render(self.fid_text, 1, (255, 0, 0))
		screen.blit(textb,(self.x+8,self.y+20))
		pygame.display.flip()
	def playSample(self):
		if self.sType==0:
			self.fid.play(0)
			self.isPlaying=True
		elif self.sType==1:
			self.fid.play(-1)
			self.isPlaying=True
		elif self.sType==2:
			if(self.isPlaying):
				self.stopSample()
				self.isPlaying=False
			else:
				self.fid.play(-1)
				self.isPlaying=True
		if self.isPlaying==True:
			screen.blit(pad_down,(self.x,self.y))
			pygame.display.flip()

##Setup pads
i=0
smplOld=-1
smplList=[]
midiList=[60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75]
for y in range(0,464,116):
	for x in range(0,464,116):
		i+=1
		smplList.append(Smpl(i,'',x,y))
pygame.display.flip()	
##Custom functions
def parseMouse((x,y),eventbutton):
	for s in smplList:
		#if clicked pad
		if(x>s.x and x<s.x+64 and y>s.y and y<s.y+64):
			print s.sid
			if eventbutton==3:
				sFile=eg.fileopenbox(msg='',title='Select a Sample',default='*',filetypes=[["*.wav", "*.ogg", "Samples"]])
				s.getSample(sFile)
			if eventbutton==1:
				s.playSample()
			return s.sid
		elif(x>s.x-21 and x<s.x+9 and y>s.y-36 and y<s.y-2):
			print "SS:" + str(s.sid)
			s.sType=0
			s.renderButtons(1,0,0)
			pygame.display.flip()
		elif(x>s.x+10 and x<s.x+41 and y>s.y-36 and y<s.y-2):
			print "L:" + str(s.sid)
			s.sType=1
			s.renderButtons(0,1,0)
			pygame.display.flip()
		elif(x>s.x+42 and x<s.x+73 and y>s.y-36 and y<s.y-2):
			print "IL:" + str(s.sid)
			s.sType=2
			s.renderButtons(0,0,1)
			pygame.display.flip()
			
			
	return -1
##
def midiMap(midiList):
	##do easygui multibox
	msg         = "Enter the MIDI Binding for Each Pad"
	title       = "MIDI Settings"
	fieldNames  = []
	for i in range(0,16):
		fieldNames.append("Pad "+str(i+1)+":")
	fieldValues=eg.multenterbox(msg,title, fieldNames,midiList)
	if fieldValues==None:
		return midiList
	else:
		for i in range(0,16):
			if not fieldValues[i].isdigit():
				eg.msgbox("Error!  Please enter digits only!")
				return midiList
			else:
				fieldValues[i]=int(fieldValues[i])
		return fieldValues
def fileMenu():
	#new, save bank, save midi, load bank, load midi, exit
	msg     = "File Menu"
	choices = ["New Project","Save Bank","Save MIDI","Load Bank","Load MIDI","Cancel"]
	reply   = eg.indexbox(msg,title='padEmulator',choices=choices)	
	if reply==0:
		print "bew"
	elif reply==1:
		sFile=eg.filesavebox(msg='',title='Save Bank',default='bank',filetypes=[["*.bdat", "Sample Bank"]])
		if sFile:
			tempFile=open(sFile,'w')
			for temp in range(0,16):
				if smplList[temp].fid_text_l!="":
					tempFile.write(smplList[temp].fid_text_l)
					tempFile.write("\n")
				else:
					tempFile.write("None\n")
			tempFile.close()
	elif reply==2:
		sFile=eg.filesavebox(msg='',title='Save MIDI',default='midi',filetypes=[["*.mdat", "MIDI Map"]])
		if sFile:
			tempFile=open(sFile,'w')
			for temp in range(0,16):
					tempFile.write(str(midiList[temp]))
					tempFile.write("\n")
			tempFile.close()
	elif reply==3:
		for temp in range(0,16):
			smplList[temp].stopSample()
		sFile=eg.fileopenbox(msg='',title='Load Bank',default='*',filetypes=[["*.bdat", "Sample Bank"]])
		if sFile:
			tempFile=open(sFile)
			lines=tempFile.readlines()
			tempFile.close()
			for temp in range(0,16):
					fileName=lines[temp][0:len(lines[temp])-1]
					if fileName!="None":
						smplList[temp].getSample(fileName)
					else:
						smplList[temp].fid=pygame.mixer.Sound('')
						smplList[temp].fid_text_l=''
						smplList[temp].fid_text=''
	elif reply==4:
		sFile=eg.fileopenbox(msg='',title='Load MIDI',default='*',filetypes=[["*.mdat", "MIDI Map"]])
		if sFile:
			tempFile=open(sFile)
			lines=tempFile.readlines()
			tempFile.close()
			for temp in range(0,16):
					midiName=lines[temp][0:len(lines[temp])-1]
					if midiName.isdigit():
						midiList[temp]=int(midiName)
					else:
						midiList[temp]=60
		
##Main game loop
while 1:
	for event in pygame.event.get():
		if event.type==pygame.quit:
			sys.exit()
		if event.type==KEYDOWN:
			if event.dict['unicode']=='m':
				midiList=midiMap(midiList)
			if event.dict['unicode']=='f':
				fileMenu()
		if event.type==MOUSEBUTTONDOWN:
			smplOld=parseMouse(pygame.mouse.get_pos(),event.button)
		if event.type==MOUSEBUTTONUP and event.button==1 and smplList[smplOld-1].sType!=2:
			smplList[smplOld-1].stopSample()
			smplOld=-1

	if(midD.poll()):
		#print signal
		signal=midD.read(10)
		if signal[0][0][2]==0:
			for mKey in range(0,16):
				if midiList[mKey]==signal[0][0][1] and smplList[mKey].sType!=2:
					smplList[mKey].stopSample()
		else:
			if (signal[0][0][0]==144):
				for mKey in range(0,16):
					if midiList[mKey]==signal[0][0][1]:
						smplList[mKey].playSample()
		#################################################
			
