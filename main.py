#!/usr/bin/python
#aconnect for midi connections
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
##video
screen=display.set_mode((336,336))
pad_down=pygame.image.load("pad-down.jpg")
pad_up=pygame.image.load("pad-up.jpg")
font = pygame.font.Font(None, 20)
pfont = pygame.font.Font(None, 18)
##Class for samples
class Smpl:
	def __init__(self,i,f,xp,yp):
			self.sid=i
			self.fid=pygame.mixer.Sound(f)
			self.fid_text=''
			self.x=xp+16
			self.y=yp+16
			screen.blit(pad_up,(self.x,self.y))
			text = font.render("Pad "+str(i), 1, (255, 255, 255))
			textb = pfont.render(self.fid_text, 1, (255, 0, 0))
			screen.blit(text,(self.x+12,self.y-16))
			screen.blit(textb,(self.x+8,self.y+20))
	def getSample(self):
		self.fid.stop()
		sFile=eg.fileopenbox(msg='',title='Select a Sample',default='*',filetypes=[["*.wav", "*.ogg", "Samples"]])
		if sFile!=None:
			self.fid=pygame.mixer.Sound(sFile)
			self.fid_text=sFile[sFile.rfind('/')+1:len(sFile)-4]
			if(len(self.fid_text)>8):
				self.fid_text=self.fid_text[0:8]
			self.stopSample()
	def playSample(self,loops):
		self.fid.play(loops)
		screen.blit(pad_down,(self.x,self.y))
		pygame.display.flip()
	def stopSample(self):
		self.fid.stop()
		screen.blit(pad_up,(self.x,self.y))
		textb = pfont.render(self.fid_text, 1, (255, 0, 0))
		screen.blit(textb,(self.x+8,self.y+20))
		pygame.display.flip()
##Setup pads
i=0
smplOld=-1
smplList=[]
for y in range(0,320,80):
	for x in range(0,320,80):
		i+=1
		smplList.append(Smpl(i,'',x,y))
pygame.display.flip()	
##Custom functions
def parseMouse((x,y),eventbutton):
	for s in smplList:
		if(x>s.x and x<s.x+64 and y>s.y and y<s.y+64):
			print s.sid
			if eventbutton==3:
				s.getSample()
			if eventbutton==1:
				s.playSample(0)
			if eventbutton==2:
				s.stopSample()
				s.playSample(-1)
			return s.sid
	return -1
##Main game loop
while 1:
	for event in pygame.event.get():
		if event.type==pygame.quit:
			sys.exit()
		if event.type==MOUSEBUTTONDOWN:
			smplOld=parseMouse(pygame.mouse.get_pos(),event.button)
		if event.type==MOUSEBUTTONUP and event.button==1:
			smplList[smplOld-1].stopSample()
			smplOld=-1

	if(midD.poll()):
		#print signal
		signal=midD.read(11)
		if (signal[0][0][0]==144):
			if(signal[0][0][1]==60):
				smplList[0].playSample(0)
			elif(signal[0][0][1]==62):
				smplList[1].playSample(0)
			elif(signal[0][0][1]==64):
				smplList[2].playSample(0)
			elif(signal[0][0][1]==65):
				smplList[3].playSample(0)
		#################################################
		if (signal[0][0][0]==128):
			if(signal[0][0][1]==60):
				smplList[0].stopSample()
			elif(signal[0][0][1]==62):
				smplList[1].stopSample()
			elif(signal[0][0][1]==64):
				smplList[2].stopSample()
			elif(signal[0][0][1]==65):
				smplList[3].stopSample()
		
