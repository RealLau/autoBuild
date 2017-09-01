#coding=utf-8
import svn.remote, svn.local
import re
import os
import time
import smtplib
import email.mime.multipart
import email.mime.text
import subprocess
import shutil
import configparser
import sys

class Helper:
    @classmethod
    def updateSourceCode(self, localDir = "C:/SVNAndroidSourceCode3.1"):
        os.chdir(localDir)
        localClie = svn.local.LocalClient(localDir)
        localClie.update()
    
    @classmethod    
    def getSVNLatestVersion(self, remoteDir="https://192.168.1.10/svn/rearview3.1/Rearview3.1/trunk"):
        r = svn.remote.RemoteClient(remoteDir)
        i = r.info()
        svnLatestVersion = i["entry#revision"]
        print(svnLatestVersion)
        return "svnlatest"+str(svnLatestVersion)
    
    @classmethod
    def getGradleAppVersion(self, localDir):
        gradleExecutableDir = os.path.join(localDir, "cyb","build.gradle")
        with open(gradleExecutableDir, "r", encoding="utf-8") as f:
            gradleInfo = f.read()
            p = re.compile(r'versionName ".*')
            resultGradleInfo = p.findall(gradleInfo)
            if resultGradleInfo:
                firstResultGradleInfo = resultGradleInfo[0]
                print(firstResultGradleInfo)
                return firstResultGradleInfo.split(" ")[1].replace('"', "")
    
    @classmethod        
    def buildApk(self, localDir, apkGenerateDir, release = False):
        os.chdir(apkGenerateDir)
        cmd = None
        if release:
            if os.path.exists(os.path.join(apkGenerateDir,"cyb-release.apk")):
                os.remove("cyb-release.apk")
            os.chdir(localDir)
            cmd = "gradlew assembleRelease"
        else:
            if os.path.exists(os.path.join(apkGenerateDir,"cyb-debug.apk")):
                os.remove("cyb-debug.apk")
            os.chdir(localDir)
            cmd = "gradlew assembleDebug"
        print(cmd)
        s = subprocess.Popen(cmd, shell=True)
        s.wait()
    
    @classmethod
    def copyApkAndRename(self, sourceFileFullPath, release = False, localSvnApkDir="C:/SVNProject/testForAutomation/", localDir=None, remoteDir=None):
        prefix = None
        if release:
            prefix = "Review_release_"
        else:
            prefix = "Review_debug_" 
        apkV = self.getGradleAppVersion(localDir=localDir)
        timeStr = time.strftime('%Y%m%d%H%M',time.localtime(time.time()))
        desFileFullPath = os.path.join(localSvnApkDir,prefix+apkV+timeStr+self.getSVNLatestVersion(remoteDir=remoteDir)+".apk")
        print(desFileFullPath)
        shutil.copy(sourceFileFullPath, desFileFullPath)
        return os.path.basename(desFileFullPath)
    
    @classmethod
    def addAndCommitApk(self, localSvnApkDir = "C:/SVNProject/testForAutomation/", fileName=None):
        os.chdir(localSvnApkDir)
        localClie = svn.local.LocalClient(localSvnApkDir)
        localClie.add(os.path.join(localSvnApkDir,fileName))
        localClie.commit("automation commit test")
    
    @classmethod
    def sendEmail(self, toList, fullContent, emailserver, emailuserName, emailpwd): 
        msg=email.mime.multipart.MIMEMultipart()  
        msg['from']=emailuserName  
        msg['to']=toList 
        msg['subject']='test'  
        txt=email.mime.text.MIMEText(fullContent)  
        msg.attach(txt)   
        
        smtp=smtplib.SMTP()  
        smtp.connect(emailserver,25)  
        smtp.login(emailuserName,emailpwd)  
        smtp.sendmail(from_addr=emailuserName, to_addrs=toList.split(",") , msg=msg.as_string())
        smtp.quit()  
    
    @classmethod
    def readAndSetPreSettings(self):
        config = configparser.ConfigParser()
        config.read("conf.ini")
        return config
    
    @classmethod
    def writeNewSettings(self, sectionName, sectionOption, newValue):
        config = configparser.ConfigParser()
        config.read("conf.ini")
        print(config.sections())
        config.set(sectionName,sectionOption, newValue)
        with open("conf.ini", "w") as conf:
            config.write(conf)
            conf.close()
            
def runTask():
    pars = sys.argv[1:]
    release, sourceCodeRemoteField, localDir, apkGenerateDir, localSvnApkDir, apkRemoteField, emailServerField,emailUserNameField,emailPwdField,emailReceiversField,emailPrefixField, updadeSourceCode, buildApk, submitApk, sendEmail = pars
    currentTime = time.strftime('%I:%M:%S %p',time.localtime(time.time()))
    fileName = None
    if updadeSourceCode=="True":
        try:
            print("=======step 1: 正在使用svn更新apk源码...=======")
            Helper.updateSourceCode(localDir=localDir)
            print("=======step 1: 使用svn更新apk源码成功=======\n\n")
        except Exception:
            print("=======step 1: 更新apk源码失败=======")
            return
        print(buildApk)
        if buildApk=="True":
            try:
                print("=======step 2: Gradle编译生成apk...=======")
                Helper.buildApk(localDir=localDir, apkGenerateDir=apkGenerateDir, release=release)
                print("=======step 2: Gradle编译生成apk成功=======\n\n")
            except Exception:
                print("=======step 2: Gradle编译生成apk失败=======")
                return
        if submitApk=="True":
            try:
                print("=======step 3: 正在复制生成的apk到svn apk文件存放目录...=======")
                lastFix = None
                if release:
                    lastFix = "cyb-release.apk"
                else:
                    lastFix = "cyb-debug.apk"
                sourceFileFullPath = os.path.join(localDir, "cyb","build","outputs","apk",lastFix)
                fileName = Helper.copyApkAndRename(sourceFileFullPath=sourceFileFullPath, release=release, localSvnApkDir=localSvnApkDir, localDir=localDir, remoteDir=sourceCodeRemoteField)
                print("=======step 3: 复制生成的apk到svn apk文件存放目录成功=======\n\n")
            except Exception:
                print("=======step 3: 复制生成的apk到svn apk文件存放目录失败=======")
                return
            try:
                print("=======step 4: svn提交生成apk...=======")
                Helper.addAndCommitApk(localSvnApkDir=localSvnApkDir, fileName=fileName)
                print("=======step 4: svn提交生成apk成功=======\n\n")
            except Exception:
                print("=======step 4: svn提交生成apk失败=======")
                return    
        if sendEmail=="True":         
            try:
                print("=======step 5: 邮件发送中...=======")
                fullContent = emailPrefixField+":\n"+apkRemoteField+fileName
                toList = emailReceiversField
                Helper.sendEmail(toList, fullContent, emailserver=emailServerField, emailuserName=emailUserNameField, emailpwd=emailPwdField)
                print("=======step 5: 邮件发送成功=======\n\n")
            except Exception:
                print("=======step 5: 邮件发送失败=======")
                return
        print("\n\n☆☆☆☆☆☆当前任务执行完毕☆☆☆☆☆☆☆")
        
if __name__=="__main__":
    runTask()
