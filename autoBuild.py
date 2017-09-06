import wx
from helper import Helper
import wx.lib.masked as masked
import subprocess 
import threading

class MyForm(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "autoBuild", size=(1000, 960))
        self.panel = wx.Panel(self) 
        self.versionControl = wx.StaticText(self.panel, -1, "版本控制:", pos=(20,20)) 
        self.radio1 = wx.RadioButton(self.panel, -1, "debug",pos=(80,20))  
        self.radio2 = wx.RadioButton(self.panel, -1, "release",pos=(160,20))  

        self.sourceCodeRemoteField = wx.TextCtrl(self.panel, 2, "https://192.168.1.10/svn/rearview3.1/Rearview3.1/trunk", pos=(20, 60), size=(251, 28))
        self.sourceCodeRemoteText = wx.StaticText(self.panel, 2, "apk源码SVN远端地址", pos=(300, 60))
        self.sourceCodeRemoteField.SetToolTip("示例: https://192.168.1.10/svn/rearview3.1/Rearview3.1/trunk")
        
        self.sourceCodeLocalField = wx.TextCtrl(self.panel, 3, "", pos=(20,100 ), size=(251, 28))
        self.sourceCodeLocalBtn = wx.Button(self.panel, 3, "apk源码SVN本地根目录", pos=(300, 100))
        self.Bind(wx.EVT_BUTTON, lambda event: self.setDirValue(event, self.sourceCodeLocalBtn.GetLabel()), self.sourceCodeLocalBtn)
        self.sourceCodeLocalField.SetToolTip(r"示例: C:\SVNAndroidSourceCode3.1")
        
        self.apkGeneratedDirField = wx.TextCtrl(self.panel, 4, "", pos=(20, 140), size=(251, 28))
        self.apkGeneratedDirBtn = wx.Button(self.panel, 4, "生成apk的所在的本地目录", pos=(300,140))
        self.Bind(wx.EVT_BUTTON, lambda event: self.setDirValue(event, self.apkGeneratedDirBtn.GetLabel()), self.apkGeneratedDirBtn)
        self.apkGeneratedDirField.SetToolTip(r"示例: C:\SVNAndroidSourceCode3.1\cyb\build\outputs\apk")
        
        self.apkCommitDirField = wx.TextCtrl(self.panel, 5, "", pos=(20, 180), size=(251, 28))
        self.apkCommitDirBtn = wx.Button(self.panel, 5, "apk生成后在本地哪儿提交", pos=(300, 180))
        self.Bind(wx.EVT_BUTTON, lambda event: self.setDirValue(event, self.apkCommitDirBtn.GetLabel()), self.apkCommitDirBtn)
        self.apkCommitDirField.SetToolTip(r"示例: C:\SVNProject\testForAutomation")
        
        self.apkRemoteField = wx.TextCtrl(self.panel, -1, r"https://192.168.1.10/svn/TestTM/Android待测/advertise/", pos=(20, 220), size=(251, 28))
        self.apkRemoteText = wx.StaticText(self.panel, -1, "生成的apk所在的SVN远端地址", pos=(300, 230))
        self.apkRemoteField.SetToolTip("示例(不要忘记最后的斜杠): https://192.168.1.10/svn/TestTM/Android待测/advertise/")
        
        self.timeCtrlText = wx.StaticText(self.panel, -1, "循环任务时间:", pos=(20,291)) 
        self.timeCtrlText.Enable(enable=False)
        self.timeCtrl = masked.TimeCtrl( self.panel, -1, name="timeCt",pos=(130,291), display_seconds = True )
        h = self.timeCtrl.GetSize().height
        spin1 = wx.SpinButton( self.panel, -1, (200,291), (-1,h), wx.SP_VERTICAL )
        self.timeCtrl.BindSpinButton( spin1 )
        
        self.emailServerText = wx.StaticText(self.panel, -1, "邮件服务器地址:", pos=(20, 340))
        self.emailServerField = wx.TextCtrl(self.panel, -1, "smtp.exmail.qq.com", pos=(130, 340), size=(280, 28))
        
        
        self.emailUserNameText = wx.StaticText(self.panel, -1, "邮件发送者账户名:", pos=(20, 380))
        self.emailUserNameField = wx.TextCtrl(self.panel, -1, "", pos=(130, 380), size=(280,28))
        
        self.emailPwdText = wx.StaticText(self.panel, -1, "邮件发送者密码:", pos=(20, 420))
        self.emailPwdField = wx.TextCtrl(self.panel, -1, "", pos=(130, 420), size=(280,28), style=wx.TE_PASSWORD)
        
        self.emailReceiversText = wx.StaticText(self.panel, -1, "邮件接收者\n(逗号分割):", pos=(20, 460))
        self.emailReceiversField = wx.TextCtrl(self.panel, -1, "", pos=(130, 460), size=(280,50), style=wx.TE_PASSWORD|wx.TE_MULTILINE)
        
        self.emailCCText = wx.StaticText(self.panel, -1, "邮件抄送给\n(逗号分割):", pos=(20, 540))
        self.emailCCField = wx.TextCtrl(self.panel, -1, "", pos=(130, 540), size=(280,50), style=wx.TE_PASSWORD|wx.TE_MULTILINE)
        
        self.emailPrefixText = wx.StaticText(self.panel, -1, "邮件正文前缀:", pos=(20, 620))
        self.emailPrefixField = wx.TextCtrl(self.panel, -1, "Ｄear All:\n\t本次主要更新内容为:xxxxx.\n\t地址如下:", pos=(130, 620), size=(280,150), style=wx.TE_PASSWORD|wx.TE_MULTILINE)
        
        self.logCtrl =  wx.TextCtrl(self.panel, -1, "", pos=(500, 20), size=(450,850), style=wx.TE_PASSWORD|wx.TE_MULTILINE)
        
        self.stepConf = wx.StaticText(self.panel, -1, "流程定制:", pos=(20, 800))
        self.checkboxUpdateApkSourceCode = wx.CheckBox(self.panel, 1, "更新源码",pos=(130, 800))
        self.checkboxBuildApk = wx.CheckBox(self.panel, 2, "编译生成APK",pos=(210, 800))
        self.checkboxSubmitApk = wx.CheckBox(self.panel, 3, "提交APK",pos=(310, 800))
        self.checkboxSendEmail = wx.CheckBox(self.panel, 4, "发送提醒邮件",pos=(390, 800))
        
        self.saveConfBtn = wx.Button(self.panel, 7, "保存配置", pos=(20, 840))
        self.saveConfBtn.Bind(wx.EVT_BUTTON, self.saveNewSettings)
        
        self.manuallyRunBtn = wx.Button(self.panel, 9, "手动执行(仅一次)", pos=(360, 840))
        self.manuallyRunBtn.Bind(wx.EVT_BUTTON, self.manuallyRun)
        
        self.statusbar = self.CreateStatusBar(number=1, style=wx.STB_DEFAULT_STYLE, id=0)
        self.statusbar.SetStatusText("autoBuild V1-20170831")
        self.t = None
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        
        #读取配置文件并设置初始化各个控件的值
        self.conf = Helper.readAndSetPreSettings()
        self.checkboxUpdateApkSourceCode.SetValue(eval(self.conf["stepSettings"]["updateapksourcedode"]))
        self.checkboxBuildApk.SetValue(eval(self.conf["stepSettings"]["buildapk"]))
        self.checkboxSubmitApk.SetValue(eval(self.conf["stepSettings"]["submitapktosvn"]))
        self.checkboxSendEmail.SetValue(eval(self.conf["stepSettings"]["sendemail"]))
        self.sourceCodeRemoteField.SetValue(self.conf["baseSettings"]["sourceCodeRemoteField"])
        self.radio2.SetValue(eval(self.conf["baseSettings"]["release"]))
        localDirV = self.conf["baseSettings"]["localDir"]
        apkGenerateDirV = self.conf["baseSettings"]["apkGenerateDir"]
        apkCommitDirFieldV = self.conf["baseSettings"]["apkCommitDirField"]
        apkCommitRemoteDirV = self.conf["baseSettings"]["apkCommitRemoteDir"]
        emailServerV = self.conf["emailSettings"]["emailServer"]
        emailUsernameV = self.conf["emailSettings"]["emailUsername"]
        emailPwdV = self.conf["emailSettings"]["emailPwd"]
        toListV = self.conf["emailSettings"]["toList"]
        ccListV = self.conf["emailSettings"]["emailCC"]
        loopTime = self.conf["loopTime"]["loopTime"]
        self.apkGeneratedDirField.SetValue(apkGenerateDirV if apkGenerateDirV!=None else "")
        self.apkCommitDirField.SetValue(apkCommitDirFieldV if apkCommitDirFieldV!=None else "")
        self.apkRemoteField.SetValue(apkCommitRemoteDirV if apkCommitRemoteDirV!=None else "")
        self.emailServerField.SetValue(emailServerV if emailServerV!=None else "")
        self.emailUserNameField.SetValue(emailUsernameV if emailUsernameV!=None else "")
        self.emailPwdField.SetValue(emailPwdV if emailPwdV!=None else "")
        self.emailReceiversField.SetValue(toListV if toListV!=None else "")
        self.emailCCField.SetValue(ccListV if ccListV!=None else "")
        with open("emailPrefix.txt", "r") as f:
            emailPrefixField = f.read()
            self.emailPrefixField.SetValue(emailPrefixField if emailPrefixField!=None else "")
        self.sourceCodeLocalField.SetValue(localDirV if localDirV!=None else "")
        self.timeCtrl.SetValue(loopTime if loopTime!='' else "02:00:00 AM")
        
    
    def combineCheck(self, evt):
        evtId = evt.GetId()
        if evt.IsChecked():
            checkboxChildren = [i for i in self.panel.GetChildren() if isinstance(i, wx.CheckBox)]
            for j in checkboxChildren:
                if j.Id<evtId:
                    j.SetValue(True)

    def saveNewSettings(self, evt):
        self.updateSourceCodeNewV = self.checkboxUpdateApkSourceCode.GetValue()
        Helper.writeNewSettings("stepSettings", "updateapksourcedode", str(self.updateSourceCodeNewV))
        self.buildAPKNewV = self.checkboxBuildApk.GetValue()
        Helper.writeNewSettings("stepSettings", "buildapk", str(self.buildAPKNewV))
        self.submitapktosvnNewV = self.checkboxSubmitApk.GetValue()
        Helper.writeNewSettings("stepSettings", "submitapktosvn", str(self.submitapktosvnNewV))
        self.sendemailNewV = self.checkboxSendEmail.GetValue()
        Helper.writeNewSettings("stepSettings", "sendemail", str(self.sendemailNewV))
        releaseNewV = self.radio2.GetValue()
        Helper.writeNewSettings("baseSettings", "release", str(releaseNewV))
        localDirNewV = self.sourceCodeLocalField.GetValue()
        Helper.writeNewSettings("baseSettings", "localDir", localDirNewV)
        apkGenerateDirNewV = self.apkGeneratedDirField.GetValue()
        Helper.writeNewSettings("baseSettings", "apkGenerateDir", apkGenerateDirNewV)
        apkCommitDirFieldNewV = self.apkCommitDirField.GetValue()
        Helper.writeNewSettings("baseSettings", "apkCommitDirField", apkCommitDirFieldNewV)
        apkRemoteFieldNewV = self.apkRemoteField.GetValue()
        Helper.writeNewSettings("baseSettings", "apkCommitRemoteDir", apkRemoteFieldNewV)
        emailServerFieldNewV = self.emailServerField.GetValue()
        Helper.writeNewSettings("emailSettings", "emailServer", emailServerFieldNewV)
        emailUsernameNewV = self.emailUserNameField.GetValue()
        Helper.writeNewSettings("emailSettings", "emailUsername", emailUsernameNewV)
        emailPwdNewV = self.emailPwdField.GetValue()
        Helper.writeNewSettings("emailSettings", "emailPwd", emailPwdNewV)
        toListNewV = self.emailReceiversField.GetValue()
        Helper.writeNewSettings("emailSettings", "toList", toListNewV)
        ccListNewV = self.emailCCField.GetValue()
        Helper.writeNewSettings("emailSettings", "emailcc", ccListNewV)        
        emailPrefixNewV = self.emailPrefixField.GetValue()
        with open("emailPrefix.txt", "w") as f:
            f.write(emailPrefixNewV)
        loopTimeNewV = self.timeCtrl.GetValue() 
        Helper.writeNewSettings("loopTime", "loopTime", loopTimeNewV)
    
    def OnClose(self, evt):
        ret = wx.MessageBox('如果有自动运行中的任务, 它将会被强制关闭. 仍然确认退出吗?',  '☆☆☆确认☆☆☆', wx.OK|wx.CANCEL)
        if ret == wx.OK:
            if self.t:
                self.t.flag = True
            evt.Skip()
        
    def setDirValue(self, evt, btnLable):
        p = None
        dlg = wx.DirDialog(self, btnLable, style=wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            p = dlg.GetPath()
            btnID = evt.GetId()
            fields = self.panel.GetChildren()
            for i in fields:
                if i.Id ==btnID:
                    if isinstance(i, wx.TextCtrl):
                        i.SetValue(p)
                        break
        dlg.Destroy()
    
    def updateLog(self, p):
        pi = p.stdout.readlines()
        for line in pi:
            self.logCtrl.AppendText(line)  
        
        
        self.manuallyRunBtn.Enable(enable=True)
        
    def manuallyRun(self, evt):
        self.updateSourceCodeNewV = self.checkboxUpdateApkSourceCode.GetValue()
        self.buildAPKNewV = self.checkboxBuildApk.GetValue()
        self.submitapktosvnNewV = self.checkboxSubmitApk.GetValue()
        self.sendemailNewV = self.checkboxSendEmail.GetValue()
        sourceCodeRemoteField = self.sourceCodeRemoteField.GetValue()
        localDir = self.sourceCodeLocalField.GetValue()
        apkGenerateDir = self.apkGeneratedDirField.GetValue()
        release = self.radio2.GetValue()
        localSvnApkDir = self.apkCommitDirField.GetValue()
        apkRemoteField = self.apkRemoteField.GetValue()
        timeCtrl = self.timeCtrl.GetValue()
        emailServerField = self.emailServerField.GetValue()
        emailUserNameField = self.emailUserNameField.GetValue()
        emailPwdField = self.emailPwdField.GetValue()
        emailReceiversField = self.emailReceiversField.GetValue()
        emailCCField = self.emailCCField.GetValue()
        emailPrefixNewV = self.emailPrefixField.GetValue()
        with open("emailPrefix.txt", "w") as f:
            f.write(emailPrefixNewV)
        l = [sourceCodeRemoteField, localDir, apkGenerateDir, localSvnApkDir,apkRemoteField, timeCtrl, emailServerField,emailUserNameField,emailPwdField,emailReceiversField]
        if "" in l:
            dlg = wx.MessageDialog(self.panel,'除<邮件抄送>外, 任一设置项均不能为空 !!!',  '☆☆☆请检查☆☆☆', wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
        else:
            ps = [release, sourceCodeRemoteField, localDir, apkGenerateDir, localSvnApkDir,apkRemoteField, emailServerField,emailUserNameField,emailPwdField,emailReceiversField, emailCCField if emailCCField!='' else 'NONE', self.updateSourceCodeNewV, self.buildAPKNewV, self.submitapktosvnNewV, self.sendemailNewV]
            cmd = "python helper.py"
            for i in ps:
                if isinstance(i, bool):
                    i=str(i)
                cmd+=" "+i
            print(cmd)
            self.p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            threading._start_new_thread(self.updateLog, (self.p,))
            self.manuallyRunBtn.Enable(enable=False)
            
            
    def updateStatus(self, msg):
        self.SetStatusText(msg, number=0)
        
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Center()
    frame.Show()
    app.MainLoop()


