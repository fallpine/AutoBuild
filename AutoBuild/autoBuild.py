#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import commands
import requests
import Tkinter
import tkMessageBox

# --------需配置项--------
# 项目名
projectName = 'xxx'
# 项目路径，要以“/”结尾，下文会进行拼接操作
projectPath = 'xxx/'
# 编译后archive文件保存的路径，要以“/”结尾，下文会进行拼接操作
archivePath = 'xxx/'
# ipa包保存的路径，要以“/”结尾，下文会进行拼接操作
ipaPath = 'xxx/'
# 项目scheme名，可通过xcodebuild -list查询
projectScheme = 'xxx'
# 打包用到的plist文件的保存路径，要以“/”结尾，下文会进行拼接操作
plistPath = 'xxx/'

# 蒲公英账号
pgyerUserKey = "xxx"
pgyerApiKey = "xxx"

# 苹果账号
developerAccount = '账号'
appSpecificPassword = 'App 专用密码'
# --------需配置项到此结束--------

# 打包类型(Debug、Release)
buildEnvironment = 'Debug'
# 工作空间路径
workspacePath = projectPath + projectName + '.xcworkspace'
# 生成的archive文件路径
archiveFilePath = archivePath + projectName + '.xcarchive'

# archive
def archiveProject():
    # 删除文件夹中的文件
    commands.getoutput('rm -rf %s'%archivePath)
    # 创建文件夹
    mkdir(archivePath)

    print "正在编译。。。"
    # clean
    commands.getoutput('xcodebuild clean -workspace %s -scheme %s -configuration %s'%(workspacePath, projectScheme, buildEnvironment))

    # archive
    commands.getoutput('xcodebuild archive -workspace %s -scheme %s -configuration %s -archivePath %s'%(workspacePath, projectScheme, buildEnvironment, archiveFilePath))
    print "编译完成"

# buildIpa
def buildIpa():
    print "正在生成ipa。。。"
    # 删除文件夹中的文件
    commands.getoutput('rm -rf %s'%ipaPath)
    mkdir(ipaPath)
    
    pPath = plistPath + 'ExportOptions_' + buildEnvironment + '.plist'
    
    commands.getoutput('xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s'%(archiveFilePath, ipaPath, pPath))
    print "ipa生成完成"

# 上传蒲公英
def uploadIpaToPgyer(ipaPath):
    isExists = os.path.exists(ipaPath)
    if not isExists:
        print "没有找到对应上传的ipa包"
        return
    else:
        print "开始上传到蒲公英。。。"
        url='http://www.pgyer.com/apiv1/app/upload'
        data={
            'uKey':pgyerUserKey,
            '_api_key':pgyerApiKey,
            'installType':'2',  # 1：公开，2：密码安装，3：邀请安装
            'password':'',
            'updateDescription':des
        }
        files={'file':open(ipaPath,'rb')}
        r=requests.post(url,data=data,files=files)

    myMessageBox("上传成功")

# 上传App Store
def uploadIpaToAppStore(ipaPath):
    isExists = os.path.exists(ipaPath)
    if not isExists:
        print "没有找到对应上传的ipa包"
        return
    else:
        print "正在上传到AppStore。。。"
        altoolPath = '/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/Frameworks/ITunesSoftwareService.framework/Support/altool'

        r1 = os.system('%s -v -f %s -u %s -p %s -t ios'%(altoolPath, ipaPath, developerAccount, appSpecificPassword))
        # 如果出错，可加上 --output-format xml 输出详细信息
#        r1 = os.system('%s -v -f %s -u %s -p %s -t ios --output-format xml'%(altoolPath, ipaPath, developerAccount, appSpecificPassword))

        # 上传ipa包
        if r1 == 0:
            r2 = os.system('%s --upload-app -f %s -t ios -u %s -p %s'%(altoolPath, ipaPath, developerAccount, appSpecificPassword))
            # 如果出错，可加上 --output-format xml 输出详细信息
#            r2 = os.system('%s --upload-app -f %s -t ios -u %s -p %s --output-format xml'%(altoolPath, ipaPath, developerAccount, appSpecificPassword))
            if r2 == 0:
                myMessageBox("上传成功")
            else:
                myMessageBox("上传失败")
        else:
            myMessageBox("上传失败")

# 消息提示框
def myMessageBox(mess):
    print mess
    tkMessageBox.showinfo("提示", mess)


# 创建文件夹
def mkdir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print path + '文件夹创建成功'
        return True
    else:
        print path + '目录已经存在'
        return False

if __name__ == '__main__':
    while True:
        buildType = raw_input("请选择打包环境(1:Debug 2:Release):")

        # 只能输入1或2
        if buildType == '1':
            buildEnvironment = 'Debug'
            break
        elif buildType == '2':
            buildEnvironment = 'Release'
            break

    while True:
        uploadType = raw_input("请选择发布环境(1:pgyer 2:App Store):")

        # 只能输入1或2
        if uploadType == '1' or uploadType == '2':
            break

    if uploadType == '1':
        des = raw_input("请输入更新的日志描述:")

    # 编译
    archiveProject()
    # 打包
    buildIpa()
    # 上传ipa
    ipaPathName = ipaPath + projectScheme + '.ipa'
    if uploadType == '1':
        uploadIpaToPgyer(ipaPathName)
    elif uploadType == '2':
        uploadIpaToAppStore(ipaPathName)
