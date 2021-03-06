#This is the script for checking oracle status,include JOB,Alert Log and Lcok .Then send mail to destination
#coding=utf-8
#coding=gbk
from django.core.management.base import BaseCommand
from oracle.models import oraclelist
import os
from oracle.monitor.getoracleinfo import *
from oracle.monitor.sendmail import *
class Command(BaseCommand):
    def handle(self, *args, **options):
	mailcontent=[]
	ip=oraclelist.objects.all().order_by('tnsname')
	for i in ip:
	    if i.monitor_type==1:
		    ipaddress=i.ipaddress
		    username=i.username
		    password=i.password
		    port=i.port
		    tnsname=i.tnsname
		    try:
			db = cx_Oracle.connect(username+'/'+password+'@'+ipaddress+':'+port+'/'+tnsname ,mode=cx_Oracle.SYSDBA)
		    except Exception , e:
			content= (i.tnsname+' is Unreachable,The reason is '+str(e)).strip()
			mailcontent.append(content)
			print mailcontent
		    else:
			cursor = db.cursor()
			job=checkjob(cursor)
			if job =='nojob':
			    #print 'There Is No Job On ' + i.tnsname
			    pass
			elif job=='error':   
			    jobresult=  'The Job Have Errors On  '+i.tnsname
			    mailcontent.append(jobresult)
			alert=checkalert(cursor)
			if alert!='normal':
			    alert_log='\n'.join(alert)
			    alertresult=  'The Alert Log Have Errors On '+i.tnsname+'\n'+alert_log
			    mailcontent.append(alertresult)
			elif alert=='nolog':
			    #print 'There Is No Alert Log On '+i.tnsname
			    pass
			lock=checklock(cursor)
			if lock!='normal':
			    lockresult= 'The '+i.tnsname +' Have Locks for '+str(lock)+' minutes'
			    mailcontent.append(lockresult)
			cursor.close()
			db.close()
        if len(mailcontent) != 0:
	    mailcontent='\n'.join(mailcontent)
	    send_mail(to_list,' ORACLE Database Monitor Status',mailcontent)
