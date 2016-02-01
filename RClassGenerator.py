#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import ConfigParser
import xml.dom.minidom
import re

# 获取配置文件解释器
def getConfigParser() :
    configFile = os.path.join(os.path.dirname(__file__), 'config.ini')
    if os.path.exists(configFile):
        parser = ConfigParser.ConfigParser()
        parser.read(configFile)
        return parser

# 判断是否是Eclipse的工程
def isEclipseProject(projectDir):
    manifestFile = os.path.join(projectDir, 'AndroidManifest.xml')
    return os.path.exists(manifestFile)

# 判断是否是AndroidStudio的工程
def isAndroidStudioProject(projectDir):
    manifestFile = os.path.join(projectDir, 'AndroidManifest.xml')
    gradleFile = os.path.join(projectDir, 'build.gradle')
    if os.path.exists(manifestFile):
        return False
    else:
        return os.path.exists(gradleFile)

def getAaptFile(isEclipse, projectDir, sdkdir):
    # 对Eclipse工程，在工程目录的project.properties文件中配置有编译时使用的目标版本
    # 如：target=android-23
    if isEclipse:
        settingFile = os.path.join(projectDir, 'project.properties')
        if os.path.exists(settingFile):
            regex = re.compile(r'^\s*target\s*=\s*android-(\d+)')
            fp = open(settingFile, 'r')
            lines = fp.readlines()
            for line in lines:
                ret = regex.search(line)
                if ret:
                    buildVersion = ret.group(1)
                    toolsPath = os.path.join(sdkdir, 'build-tools')
                    if os.path.exists(toolsPath):
                        verList = []
                        _, dirNames, _ = os.walk(toolsPath).next()
                        for dirname in dirNames:
                            if dirname.startswith(buildVersion + '.'):
                                verList.append(dirname)
                        if len(verList) != 0:
                            ver = verList[-1]
                            verPath = os.path.join(toolsPath, ver)
                            aaptPath = os.path.join(verPath, 'aapt.exe')
                            print 'aapt is at ' + aaptPath
                            return aaptPath
    else:
        settingFile = os.path.join(projectDir, 'build.gradle')
        if os.path.exists(settingFile):
            regex = re.compile(r'^\s*buildToolsVersion\s*"(\S+)"')
            fp = open(settingFile, 'r')
            lines = fp.readlines()
            for line in lines:
                ret = regex.search(line)
                if ret:
                    buildVersion = ret.group(1)
                    toolsPath = os.path.join(sdkdir, 'build-tools')
                    verPath = os.path.join(toolsPath, buildVersion)
                    aaptPath = os.path.join(verPath, 'aapt.exe')
                    print 'aapt is at ' + aaptPath
                    return aaptPath

def getAndroidjarFile(isEclipse, projectDir, sdkdir):
    # 对Eclipse工程，在工程目录的project.properties文件中配置有编译时使用的目标版本
    # 如：target=android-23
    if isEclipse:
        settingFile = os.path.join(projectDir, 'project.properties')
        if os.path.exists(settingFile):
            regex = re.compile(r'^\s*target\s*=\s*(\S+)')
            fp = open(settingFile, 'r')
            lines = fp.readlines()
            for line in lines:
                ret = regex.search(line)
                if ret:
                    buildVersion = ret.group(1)
                    platformPath = os.path.join(sdkdir, 'platforms')
                    verPath = os.path.join(platformPath, buildVersion)
                    androidjarPath = os.path.join(verPath, 'android.jar')
                    print 'android.jar is at ' + androidjarPath
                    return androidjarPath
    else:
        settingFile = os.path.join(projectDir, 'build.gradle')
        if os.path.exists(settingFile):
            regex = re.compile(r'^\s*compileSdkVersion\s*(\d+)')
            fp = open(settingFile, 'r')
            lines = fp.readlines()
            for line in lines:
                ret = regex.search(line)
                if ret:
                    buildVersion = ret.group(1)
                    platformPath = os.path.join(sdkdir, 'platforms')
                    verPath = os.path.join(platformPath, 'android-' + buildVersion)
                    androidjarPath = os.path.join(verPath, 'android.jar')
                    print 'android.jar is at ' + androidjarPath
                    return androidjarPath

def getIsLibraryProject(isEclipse, projectDir):
    # 对Eclipse工程，在工程目录的project.properties文件中配置有该工程是否是library工程的标记
    # android.library=true
    isLibrary = False
    if isEclipse:
        settingFile = os.path.join(projectDir, 'project.properties')
        if os.path.exists(settingFile):
            regex = re.compile(r'^\s*android.library\s*=\s*(\S+)')
            fp = open(settingFile, 'r')
            lines = fp.readlines()
            for line in lines:
                ret = regex.search(line)
                if ret:
                    libraryTag = ret.group(1).strip()
                    if libraryTag == 'true':
                        isLibrary = True
                    elif libraryTag == 'false':
                        isLibrary = False
                    print 'This is a library project? ' + str(isLibrary)
                    return isLibrary
    else:
        settingFile = os.path.join(projectDir, 'build.gradle')
        if os.path.exists(settingFile):
            regex = re.compile(r"^\s*apply plugin:\s*'com\.android\.(\S+)'")
            fp = open(settingFile, 'r')
            lines = fp.readlines()
            for line in lines:
                ret = regex.search(line)
                if ret:
                    libraryTag = ret.group(1).strip()
                    if libraryTag == 'library':
                        isLibrary = True
                    elif libraryTag == 'application':
                        isLibrary = False
                    print 'This is a library project? ' + str(isLibrary)
                    return isLibrary
    
def getRPath(isEclipse, projectDir):
    if isEclipse:
        path = os.path.join(projectDir, 'gen')
        print 'The R.java is in to generate at ' + path
        return path
    else:
        path = os.path.join(projectDir, r'build\generated\source\r\release')
        print 'The R.java is in to generate at ' + path
        return path
    
def getResPath(isEclipse, projectDir):
    if isEclipse:
        path = os.path.join(projectDir, 'res')
        print 'The project res path is ' + path
        return path
    else:
        path = os.path.join(projectDir, r'src\main\res')
        print 'The project res path is ' + path
        return path
    
def getManifestFile(isEclipse, projectDir):
    if isEclipse:
        manifestFile = os.path.join(projectDir, 'AndroidManifest.xml')
        print 'The manifest file is ' + manifestFile
        return manifestFile
    else:
        manifestFile = os.path.join(projectDir, r'src\main\AndroidManifest.xml')
        print 'The manifest file is ' + manifestFile
        return manifestFile
    
def getPackageName(isEclipse, projectDir):
    manifestFile = getManifestFile(isEclipse, projectDir)
    if os.path.exists(manifestFile):
        # 解析xml文件
        dom = xml.dom.minidom.parse(manifestFile)
        # 找出manifest节点
        manifestNodeList = dom.getElementsByTagName('manifest')
        if len(manifestNodeList) == 1:
            manifestNode = manifestNodeList[0]
            packageName = manifestNode.getAttribute('package')
            print 'The package name is ' + packageName
            return packageName

def getRClassFile(isEclipse, projectDir, RPath):
    packageName = getPackageName(isEclipse, projectDir)
    if packageName != None and packageName != '':
        splitPackageName = packageName.split('.')
        RClassFile = RPath
        for splitItem in splitPackageName:
            RClassFile = os.path.join(RClassFile, splitItem)
        RClassFile = os.path.join(RClassFile, 'R.java')
        print 'The generated R.java is ' + RClassFile
        return RClassFile

def getSrcPathList(isEclipse, projectDir):
    srcPath = []
    if isEclipse:
        cfgFile = os.path.join(projectDir, '.classpath')
        if os.path.exists(cfgFile):
            dom = xml.dom.minidom.parse(cfgFile)
            root = dom.documentElement
            items = root.getElementsByTagName('classpathentry')
            for item in items:
                itemKind = item.getAttribute('kind')
                if itemKind == 'src':
                    itemPath = item.getAttribute('path')
                    if itemPath != 'gen':
                        srcPath.append(os.path.join(projectDir, itemPath))
            return srcPath
        else:
            srcPath.append(os.path.join(projectDir, 'src'))
            return srcPath
    else:
        cfgFile = os.path.join(projectDir, 'build.gradle')
        if os.path.exists(cfgFile):
            cfgFp = open(cfgFile, 'r')
            inSourceSetsCfg = False
            braceCount = 0
            for cfgLine in cfgFp:
                stripLine = cfgLine.strip()
                if stripLine.startswith('sourceSets'):
                    inSourceSetsCfg = True
                if inSourceSetsCfg:
                    pos = stripLine.find('java.srcDirs')
                    if pos != -1:
                        stripLine = stripLine[pos + len('java.srcDirs'):].lstrip()
                        assert len(stripLine) > 2
                        if stripLine[0:2] == '+=':
                            srcPath.append(os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'java'))
                            stripLine = stripLine[2:]
                        stripLine = stripLine.lstrip(' [=').rstrip(']')
                        splitLine = stripLine.split(',')
                        for splitItem in splitLine:
                            splitItem = splitItem.strip(' \'"')
                            if len(splitItem) != 0:
                                if os.path.sep != '/':
                                    splitItem = splitItem.replace('/', os.path.sep)
                                elif os.path.sep != '\\':
                                    splitItem = splitItem.replace('\\', os.path.sep)
                                srcPath.append(os.path.join(projectDir, splitItem))
                        break
                    braceCount += stripLine.count('{')
                    braceCount -= stripLine.count('}')
                    if braceCount <= 0:
                        break
            if len(srcPath) == 0:
                srcPath.append(os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'java'))
            return srcPath
        else:
            srcPath.append(os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'java'))
            return srcPath
    
def getDestRClassPath(isEclipse, projectDir, destRClassPackage):
    if isEclipse:
        destRClassPath = os.path.join(projectDir, 'src')
        splitPackageName = destRClassPackage.split('.')
        for splitItem in splitPackageName:
            destRClassPath = os.path.join(destRClassPath, splitItem)
        print 'The new R.java is ' + destRClassPath
        return destRClassPath
    else:
        destRClassPath = os.path.join(projectDir, r'src\main\java')
        splitPackageName = destRClassPackage.split('.')
        for splitItem in splitPackageName:
            destRClassPath = os.path.join(destRClassPath, splitItem)
        print 'The new R.java is ' + destRClassPath
        return destRClassPath
    
def getExtraAddedStr():
    return \
'''import java.lang.reflect.Field;

import android.content.Context;
import android.content.res.Resources;
import android.util.Log;

public final class R {
    private static Resources mResources;
    private static String mPackageName;
    
    public static void init(Context context) {
        if (context != null) {
            mResources = context.getResources();
            mPackageName = context.getPackageName();
            try {
                Class.forName(mPackageName + ".R");
            } catch (Exception e) {
                Log.e("init error","No R class");
            }
        }
    }
    
    public static void release() {
        mResources = null;
        mPackageName = null;
    }
    
    private static final int getResId(String resName, String resType) {
        int id = 0;
        if (mResources != null && mPackageName != null) {
            try {
                id = mResources.getIdentifier(resName, resType, mPackageName);
            } catch (Throwable t) {
                Log.e("get id failed", "id " + resName + " could not be found");
            }
        }
        if (id == 0) {
            Log.e("get id failed", "id " + resName + " is 0");
        }
        return id;
    }
    
    @SuppressWarnings("unused")
    private static final int[] getStyleableId(String resName) {
        try {
            Field[] fields2 = Class.forName(mPackageName + ".R$styleable").getFields();
            for (Field f : fields2) {
                if (f.getName().equals(resName)) {
                    return (int[])f.get(null);
                }
            }
        }
        catch (Throwable t) {
            Log.e("get id failed", "Styleable id " + resName + " could not be found");
        }
        return null;
    }
'''
    
def convertR(isLibrary, RClassFile, destRClassPackage):
    # 获取R类文件中的换行符号
    fp = open(RClassFile, 'rU') 
    fp.readlines()
    newl = fp.newlines
    # 读取R类文件内容
    fp = codecs.open(RClassFile, 'rU', 'utf-8') 
    rlines = fp.readlines()
    fp.close()
    
    # 修改R类内容
    newRLines = []
    newRLines.append('package ' + destRClassPackage + ";" + newl)
    newRLines.append(newl)
    newRLines.append(getExtraAddedStr())
    newRLines.append(newl)
    
    start = False
    inStyleable = False
    currentResType = None
    if isLibrary:
        resIDPrefix = 'public static int'
    else:
        resIDPrefix = 'public static final int'
    styleableResIDPrefix = 'public static final int[]'
    for tempLine in rlines:
        if start:
            if tempLine.find('=') == -1:
                stripedLine = tempLine.strip()
                if inStyleable:
                    if stripedLine == '};':
                        inStyleable = False
                else:
                    if stripedLine.startswith('public static final class'):
                        currentResType = stripedLine[26:-2].strip()
                    elif stripedLine == '}' or stripedLine == '};':
                        currentResType = None
                    newRLines.append(tempLine)
            else:
                if currentResType is not None:
                    splitLine = tempLine.split('=')
                    leftLine = splitLine[0]
                    resName = splitLine[0].strip()
                    if resName.startswith(styleableResIDPrefix):
                        resName = resName[len(styleableResIDPrefix):].strip()
                        if resName != '':
                            newLine = leftLine.rstrip() + ' = getStyleableId("' + resName + '");'
                            newRLines.append(newLine + newl)
                            inStyleable = True
                    else:
                        resName = resName[len(resIDPrefix):].strip()
                        if resName != '':
                            newLine = leftLine.rstrip() + ' = getResId("' + resName + '", "' + currentResType + '");'
                            newRLines.append(newLine + newl)
        else:
            if tempLine.strip().startswith('public final class R {'):
                start = True
    return newRLines
    
def writeToFile(filePath, fileContentList):
    # 写入目标R类所在的目录
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    destRClassFile = os.path.join(filePath, 'R.java')
    destRClassFp = codecs.open(destRClassFile, 'w', 'utf-8')
    isInComment = False
    for fileLine in fileContentList:
        if not isInComment:
            if fileLine.lstrip().startswith('/**'):
                isInComment = True
        if isInComment:
            if fileLine.rstrip().endswith('*/'):
                isInComment = False
        else:
            destRClassFp.write(fileLine)

    destRClassFp.close()
    
def replaceCodeImport(srcPathList, package, RPackageName):
    srcImportString = 'import ' + package + '.R;'
    replaceImportString = 'import ' + RPackageName + '.R;'
    srcImportString = srcImportString.encode('ascii')
    replaceImportString = replaceImportString.encode('ascii')
    for srcPath in srcPathList:
        for parent, _, fileNames in os.walk(srcPath):
            for temp in fileNames:
                if not temp.endswith('.java'):
                    continue
                codeFile = os.path.join(parent, temp)
                # open and read the file
                fp = open(codeFile, 'r')
                codeFileContent = fp.readlines()
                fp.close()
                
                atImportPart = False
                isChanged = False
                for index in range(len(codeFileContent)):
                    thisLine = codeFileContent[index]
                    if not atImportPart and thisLine.find('import ') != -1:
                        atImportPart = True
                    if atImportPart:
                        if thisLine.strip() != '' and not thisLine.find('import ') != -1:
                            break
                        if thisLine.find(srcImportString) != -1:
                            codeFileContent[index] = thisLine.replace(srcImportString, replaceImportString)
                            isChanged = True 
                if isChanged:
                    print 'replacing file ' + temp
                    fp = open(codeFile, 'w')
                    fp.writelines(codeFileContent)
                    fp.close()
    
def process():
    configParser = getConfigParser()
    if configParser == None:
        return
    # 获取配置文件中配置的工程目录和R类文件的包名称
    projectDir = configParser.get('Dir', 'ProjectDir')
    sdkdir = configParser.get('Dir', 'sdkdir')
    # 没有相应配置，返回
    if not os.path.exists(sdkdir) or not os.path.exists(projectDir):
         raise RuntimeError('Invalid parameters')
    # 判断工程是Eclipse还是Android Studio
    isEclipse = isEclipseProject(projectDir)
    isAndroidStudio = isAndroidStudioProject(projectDir)
    # 既不是Eclipse，也不是Android Studio
    if not isEclipse and not isAndroidStudio:
        raise RuntimeError('Unknown project type')
    
    # 获取android sdk中的aapt文件路径和android.jar文件路径
    aaptFile = getAaptFile(isEclipse, projectDir, sdkdir)
    androidjarFile = getAndroidjarFile(isEclipse, projectDir, sdkdir)
    # 获取不到文件，或者文件不存在，返回
    if aaptFile == None or not os.path.exists(aaptFile):
         raise RuntimeError('Cannot find aapt.exe in ' + sdkdir)
    if androidjarFile == None or not os.path.exists(androidjarFile):
         raise RuntimeError('Cannot find android.jar in ' + sdkdir)
    # 通过aapt生成R.java类路径，项目中res文件夹路径和AndroidManifest.xml文件路径
    RPath = getRPath(isEclipse, projectDir)
    resPath = getResPath(isEclipse, projectDir)
    manifestFile = getManifestFile(isEclipse, projectDir)
    if not os.path.exists(RPath):
        os.mkdir(RPath)
    if not os.path.exists(resPath) or not os.path.exists(manifestFile):
         raise RuntimeError('Cannot find resPath or manifest file in ' + projectDir)
    # 判断工程是否是Library工程
    isLibrary = getIsLibraryProject(isEclipse, projectDir)
    command = aaptFile + ' p -m -J '+ RPath + ' -S ' + resPath + ' -M ' + manifestFile + ' -I ' + androidjarFile
    # 对Library工程需要添加参数--non-constant-id，这样生成的R.java中的资源id就是public static int，否则是public static final int
    if isLibrary:
        command = command + ' --non-constant-id'
    print 'Try to execute command: ' + command
    os.system(command)
    # 获取生成的R.java文件路径
    RClassFile = getRClassFile(isEclipse, projectDir, RPath)
    if not os.path.exists(RClassFile):
        return;
    
    # 获取目标R类的路径
    if configParser.has_option('RClass', 'RClassPackage'):
        destRClassPackage = configParser.get('RClass', 'RClassPackage').strip('.')
    else:
        destRClassPackage = getPackageName(isEclipse, projectDir)
        
    newRLines = convertR(isLibrary, RClassFile, destRClassPackage)
    
    destRClassPath = getDestRClassPath(isEclipse, projectDir, destRClassPackage)
    writeToFile(destRClassPath, newRLines)
    
    # 判断是否要替换代码中的import信息（ReplaceCode可以不存在）
    if configParser.has_option('RClass', 'ReplaceCode'):
        isReplace = configParser.get('RClass', 'ReplaceCode')
        if isReplace.lower() == 'true':
            package = getPackageName(isEclipse, projectDir)
            if package == destRClassPackage:
                print 'the package name is the same, and no need to replace'
            srcPathList = getSrcPathList(isEclipse, projectDir)
            replaceCodeImport(srcPathList, package, destRClassPackage)

if  __name__ == '__main__':
    process()