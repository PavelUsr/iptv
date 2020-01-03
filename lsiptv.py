#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  lsiptv.py
#
#  Copyright 2018 pavel <pavel@pavel-comp>
#	ver 2.0 beta
#
# Список файлов листов

import sys
import requests
import time
import pickle

blstp = []  # Лист состоящий [group-title,tvg-id,tvg-logo,tvg-name,upl]
mas = [] # Масив blstp

def sort_col(i):
	return i[3]

    # Ключом является первый символ в каждой строке, сортируем по нему

def chconnect():
	n=0
	while n < (len (mas)-1):
		l = mas[n]
		start_time = time.time()
		if connected_to_internet(l[4]) :
			st = (time.time() - start_time)
			print ('%i\t%s\t connect : %s' %(n,st,l[4]))
			n +=1
		else :
			st = (time.time() - start_time)
			print ('\033[01;95m%i\t%s\t no connect: %s\033[00m' %(n,st,l[4]))
			mas.pop(n)            

def connected_to_internet(url, timeout=(2,2)):
    try:
        req = requests.head(url, timeout=timeout)
        return True
    except requests.RequestException:
        return False
    return False

def loadpllists (flcfg):
	filpl = []
	with open(flcfg,"r")as filel:
		for ls in filel :
			ls = clearstr(ls)
			filen = (ls.split("/")[-1]) #Получение имени файла со строки url
			if download(ls,filen):
				print ("Загружен :%s"%ls)
				filpl.append(filen)
			else :
				print ("Не загружен :%s"%ls)
	return filpl 	# Список загруженных файлов

def download(url, file_name): # Загрузка файла, ели без ошибок то True
	try:
			# get request
		response = requests.get(url,allow_redirects = True)
		print ("Status code :%s"%response.status_code)
#		print (response.headers)
		if response.status_code == 200 :
			# open in binary mode
			# write to file
			with open(file_name, "wb") as filel:
				filel.write(response.content)
				return True
		return False
	except requests.ConnectionError:
		print ("Ошибка закачки по адр : %s"%url)
		print response.status_code
		return False

def clearstr (st):
	st=st.strip()
	st=st.rstrip("\n")
	st=st.rstrip("\r")
	return st


def shstr (stru,ichstr) : #Функция ищет в строке ключ и возращает значение
	stu =''
	f = True
	ls = []
	ls = stru.split(',')
	stru = ls[0]
	namchan = ls[1]
	if ichstr == 'tvg-name':
		return clearstr(namchan)
	for s in stru :
		if s=='"':
			f = not (f)
			stu = stu + s
		elif (s ==' ')and (f):
			if stu.find(ichstr)<>-1:
				ls = stu.split("=")
				return clearstr(ls[1])
			stu = ''
		else :
			stu = stu + s
	if stu.find(ichstr)<>-1:
		ls = stu.split("=")
		return clearstr(ls[1])
	return ""

def msfile (nfile): # Читает с файла и заносит в базу  лист
	filels = open (nfile,"r")
	lsf =[]
	lsf = [clearstr(l) for l in filels]
	n=0
	while n<> len(lsf):
		line = lsf[n]
		if line.find("#EXTM3U")<>-1 :
			print ('Start file to base %s'% nfile)
			n+=1
			line=lsf[n]
		if line.find("#EXTGRP")<>-1 :
			n+=1
			line=lsf[n]
			pass
		if line.find("#EXTINF")<>-1 :
			grouptitle  = shstr (line,"group-title")
			tvgid = shstr (line,"tvg-id")
			tvglogo = clearstr(shstr (line,"tvg-logo"))
			tvgname = shstr (line,"tvg-name")
			n+=1
			line=lsf[n]
		if line.find("http")==0 :
			if line.find(".mp4")<> -1:
				pass
			else :
				upl = clearstr(line)
				blstp = [grouptitle,tvgid,tvglogo,tvgname,upl]
				mas.append(blstp)
		if line.find("rtmp")==0 :
			pass
		n+=1
	filels.close
	print ('Stop file %s'% nfile)
	return mas

def checkbase (chbase) :
	print ("Проверка базы на повторение адресов...")
	n = 0
	nn =1
	s1 =""
	ss1 =""
	sn = 0
	while n < (len (chbase)-1):
		s1 = chbase [n] [4]
		while nn < (len (chbase)-1):
			ss1 = chbase [nn] [4]
			if s1 == ss1 :
				sn +=1
				chbase.pop (nn)
				nn -=1
			nn +=1
		s1 = chbase [n] [3] # Имя канала
		if s1[0]in ['#','-','=','+'] :
			chbase.pop (n)
			sn +=1
			n -=1
		n += 1
		nn = n +1
	print ("Проходов %s совподений %s текущая база %s" % (n, sn, len(mas)))

def savebase (lfile,bas):
	with open(lfile, 'wb') as f:
		pickle.dump(bas, f)
	print ('База сохранена.')
	return

def exportlist (basaFile,mlist):
	pmy_file = open(basaFile, "w")
	pmy_file.write ("#EXTM3U\n")
	for hl in mlist :
		if hl[0] =="":
			si = "#EXTINF:-1,%s\n"%hl[3]
			u = hl[4]+"\n"
			pmy_file.write (si)
			pmy_file.write (u)
		else :
			si = '#EXTINF:-1 group-title=%s tvg-id=%s tvg-logo=%s tvg-name=%s,%s\n'%(hl[0],hl[1],hl[2],hl[3],hl[3])
			sg = '#EXTGRP:%s\n'%hl[0]
			u = hl[4]+"\n"
			pmy_file.write (si)
			pmy_file.write (sg)
			pmy_file.write (u)
	pmy_file.close

def main(args):
	lsfiles = loadpllists ("url.cfg")
	for fil in lsfiles :
		msfile (fil)
	l = len (mas)
	print ("Всего в базе %s записей" %l)
	checkbase (mas)
	chconnect()
	print ("Tекущая база %s" % (len(mas)))
	print ("Сортировка ...")
	mas.sort(key=sort_col) #сортируем массив
	print ("Tекущая база %s" % (len(mas)))
	print ("сохраняем базу...")
	savebase ("myiptv.mb",mas)
	print ("сохраняем лист...")
	exportlist("myiptv.m3u",mas)
	print ('Ok')
	return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
