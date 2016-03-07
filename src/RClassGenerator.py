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

# 判断是否是资源目录
def isResDir(projectOrResDir):
    manifestFile = os.path.join(projectOrResDir, 'AndroidManifest.xml')
    gradleFile = os.path.join(projectOrResDir, 'build.gradle')
    resTypes = ('drawable', 'layout', 'anim', 'animator', 'values')
    if not os.path.exists(manifestFile) and not os.path.exists(gradleFile):
        (_, dirNames, fileNames) = os.walk(projectOrResDir).next()
        if len(fileNames) == 0:
            for folder in dirNames:
                for resType in resTypes:
                    if folder.startswith(resType):
                        return True
    return False

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

def getDefaultAaptFile(sdkdir):
    toolsPath = os.path.join(sdkdir, 'build-tools')
    if os.path.exists(toolsPath):
        _, dirNames, _ = os.walk(toolsPath).next()
        if len(dirNames) != 0:
            verPath = os.path.join(toolsPath, dirNames[0])
            aaptPath = os.path.join(verPath, 'aapt.exe')
            print 'aapt is at ' + aaptPath
            return aaptPath

def getDefaultAndroidjarFile(sdkdir):
    platformPath = os.path.join(sdkdir, 'platforms')
    if os.path.exists(platformPath):
        _, dirNames, _ = os.walk(platformPath).next()
        if len(dirNames) != 0:
            verPath = os.path.join(platformPath, dirNames[0])
            androidjarPath = os.path.join(verPath, 'android.jar')
            print 'android.jar is at ' + androidjarPath
            return androidjarPath

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
    if packageName is not None and packageName != '':
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
    
def getExtraAddedStr(newLine):
    extraStr = \
'''import android.content.Context;
import android.util.Log;

import java.lang.ref.WeakReference;
import java.lang.reflect.Field;

public final class R {
    private static String mPackageName;
    private static WeakReference<Context> mContextRef;

    public static void init(Context context) {
        if (context != null) {
            mPackageName = context.getPackageName();
            // try to get R class in the package
            try {
                Class.forName(mPackageName + ".R");
                mContextRef = null;
            }
            // if R class is not exist, record the context by WeakReference
            catch (ClassNotFoundException e) {
                Log.i("Eplay init info","No R class");
                mContextRef = new WeakReference<>(context);
            }
        }
    }

    private static int getResId(String resName, String resType) {
        // The WeakReference is null indicates the R class exists. We can use reflection to get the resource id.
        // Using reflection to get the resource id is much faster than getResources().getIdentifier()
        if (mContextRef == null) {
            try {
                Field field = Class.forName(mPackageName + ".R$" + resType).getField(resName);
                return (int)field.get(null);
            }
            catch (Throwable t) {
                Log.e("get id failed", "id " + resName + " could not be found");
            }
        }
        // The WeakReference is not null indicates the R class does not exist.
        // We should use getResources().getIdentifier() method to get resource id.
        else {
            Context context = mContextRef.get();
            if (context != null) {
                return context.getResources().getIdentifier(resName, resType, mPackageName);
            }
        }
        return 0;
    }
'''
    if newLine != '\n':
        extraStr = extraStr.replace('\n', newLine)
    return extraStr

def convertR(isLibrary, RClassFile, destRClassPackage):
    # 获取R类文件中的换行符号
    fp = open(RClassFile, 'rU') 
    fp.readlines()
    newl = fp.newlines
    # 读取R类文件内容
    fp = codecs.open(RClassFile, 'rU', 'utf-8') 
    rlines = fp.readlines()
    fp.close()
    
    # 修改R类package和import和新增的函数
    newRLines = ['package ' + destRClassPackage + ";" + newl, newl, getExtraAddedStr(newl), newl]

    start = False
    inStyleable = False
    currentResType = None
    if isLibrary:
        resIDPrefix = 'public static int'
    else:
        resIDPrefix = 'public static final int'
    styleableResIDPrefix = 'public static final int[]'
    for index in range(len(rlines)):
        tempLine = rlines[index]
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
                        newLine = leftLine.rstrip()
                        newRLines.append(newLine + newl)
                        if not tempLine.strip().endswith('};'):
                            inStyleable = True
                    else:
                        if currentResType != 'styleable':
                            resName = resName[len(resIDPrefix):].strip()
                            newLine = leftLine.rstrip() + ' = getResId("' + resName + '", "' + currentResType + '");'
                            newRLines.append(newLine + newl)
                        else:
                            newRLines.append(tempLine)
        else:
            if tempLine.strip().startswith('public final class R {'):
                start = True
    newRLines = processComment(newRLines)
    processStyleable(newRLines, resIDPrefix, styleableResIDPrefix, newl)
    return newRLines

def processComment(RLines):
    isInComment = False
    newRLines = []
    for fileLine in RLines:
        if not isInComment:
            if fileLine.lstrip().startswith('/**'):
                isInComment = True
            else:
                newRLines.append(fileLine)
        if isInComment:
            if fileLine.rstrip().endswith('*/'):
                isInComment = False
    return newRLines

def processStyleable(newRLines, resIDPrefix, styleableResIDPrefix, newl):
    for index in range(len(newRLines)):
        tempLine = newRLines[index]
        splitLine = tempLine.split('=')
        leftLine = splitLine[0]
        resName = splitLine[0].strip()
        if resName.startswith(styleableResIDPrefix):
            resName = resName[len(styleableResIDPrefix):].strip()
            styleableDict = {}
            nextIndex = index
            while True:
                nextIndex += 1
                nextLine = newRLines[nextIndex]
                parsedLine = parseStyleableLine(nextLine, resName, resIDPrefix)
                if parsedLine is None:
                    break
                styleableDict[parsedLine[0]] = parsedLine[1]
            allStyleable = ""
            for temp in range(len(styleableDict)):
                allStyleable = allStyleable + "attr." + styleableDict[str(temp)]
                if temp != len(styleableDict) - 1:
                    allStyleable = allStyleable + ", "
            newLine = leftLine.rstrip() + ' = { ' + allStyleable + ' };' + newl
            newRLines[index] = newLine

def parseStyleableLine(styleableLine, styleableName, resIDPrefix):
    if styleableLine.find('=') == -1:
        return
    splitLine = styleableLine.split('=')
    resName = splitLine[0].strip()
    if not resName.startswith(resIDPrefix):
        return
    resName = resName[len(resIDPrefix):].strip()
    if not resName.startswith(styleableName):
        return
    resName = resName[len(styleableName):]
    if not resName.startswith('_'):
        return
    resName = resName[1:]
    resValue = splitLine[1].strip()
    if not resValue.endswith(';'):
        return
    resValue = resValue[:-1]
    return (resValue, resName)

def writeToFile(filePath, fileContentList):
    # 写入目标R类所在的目录
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    destRClassFile = os.path.join(filePath, 'R.java')
    destRClassFp = codecs.open(destRClassFile, 'w', 'utf-8')
    destRClassFp.writelines(fileContentList)
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
    if configParser is None:
        raise RuntimeError('Get parser failed')
    # 获取配置文件中配置的工程目录和R类文件的包名称
    ProjectOrResDir = configParser.get('Dir', 'ProjectOrResDir')
    sdkdir = configParser.get('Dir', 'sdkdir')
    # 没有相应配置，返回
    if not os.path.exists(sdkdir) or not os.path.exists(ProjectOrResDir):
         raise RuntimeError('Invalid parameters')

    # 获取目标R类的路径
    destRClassPackage = configParser.get('RClass', 'RClassPackage').strip('.')
    # 判断所给路径是工程路径还是资源文件夹路径
    isRes = isResDir(ProjectOrResDir)
    if isRes:
        processResDir(ProjectOrResDir, sdkdir, destRClassPackage)
    else:
        # 判断工程是Eclipse还是Android Studio
        isEclipse = isEclipseProject(ProjectOrResDir)
        isAndroidStudio = isAndroidStudioProject(ProjectOrResDir)
        # 既不是Eclipse，也不是Android Studio
        if not isEclipse and not isAndroidStudio:
            raise RuntimeError('Unknown project type')
        # 判断是否要替换代码中的import R类
        isReplaceCode = False
        if configParser.has_option('RClass', 'ReplaceCode'):
            isReplace = configParser.get('RClass', 'ReplaceCode')
            if isReplace.lower() == 'true':
                isReplaceCode = True
        processProjectDir(isEclipse, ProjectOrResDir, sdkdir, destRClassPackage, isReplaceCode)

def processResDir(resDir, sdkdir, destRClassPackage):
    # 获取android sdk中的aapt文件路径和android.jar文件路径
    aaptFile = getDefaultAaptFile(sdkdir)
    androidjarFile = getDefaultAndroidjarFile(sdkdir)
    # 获取不到文件，或者文件不存在，返回
    if aaptFile is None or not os.path.exists(aaptFile):
         raise RuntimeError('Cannot find aapt.exe in ' + sdkdir)
    if androidjarFile is None or not os.path.exists(androidjarFile):
         raise RuntimeError('Cannot find android.jar in ' + sdkdir)
    # 通过aapt生成R.java类路径(使用资源目录的同级目录)
    RPath = os.path.dirname(resDir)
    # AndroidManifest.xml文件路径（使用AndroidRClassGenerator中自带的AndroidManifest.xml）
    manifestFile = os.path.join(os.path.dirname(__file__), 'AndroidManifest.xml')

    isLibrary = True
    command = aaptFile + ' p -J '+ RPath + ' -S ' + resDir + ' -M ' + manifestFile + ' -I ' + androidjarFile
    # 对Library工程需要添加参数--non-constant-id，这样生成的R.java中的资源id就是public static int，否则是public static final int
    if isLibrary:
        command += ' --non-constant-id'
    print 'Try to execute command: ' + command
    os.system(command)
    # 获取生成的R.java文件路径
    RClassFile = os.path.join(RPath, 'R.java')
    if not os.path.exists(RClassFile):
        raise RuntimeError('R class is not generated')

    newRLines = convertR(isLibrary, RClassFile, destRClassPackage)
    writeToFile(RPath, newRLines)

def processProjectDir(isEclipse, projectDir, sdkdir, destRClassPackage, isReplaceCode):
    # 获取android sdk中的aapt文件路径和android.jar文件路径
    aaptFile = getAaptFile(isEclipse, projectDir, sdkdir)
    androidjarFile = getAndroidjarFile(isEclipse, projectDir, sdkdir)
    # 获取不到文件，或者文件不存在，返回
    if aaptFile is None or not os.path.exists(aaptFile):
         raise RuntimeError('Cannot find aapt.exe in ' + sdkdir)
    if androidjarFile is None or not os.path.exists(androidjarFile):
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
        command += ' --non-constant-id'
    print 'Try to execute command: ' + command
    ret = os.system(command)
    if ret != 0:
        print 'Find errors in resource folder'
        exit(1)
    # 获取生成的R.java文件路径
    RClassFile = getRClassFile(isEclipse, projectDir, RPath)
    if not os.path.exists(RClassFile):
        raise RuntimeError('R class is not generated')

    newRLines = convertR(isLibrary, RClassFile, destRClassPackage)

    destRClassPath = getDestRClassPath(isEclipse, projectDir, destRClassPackage)
    writeToFile(destRClassPath, newRLines)

    if isReplaceCode:
        package = getPackageName(isEclipse, projectDir)
        if package == destRClassPackage:
            print 'the package name is the same, and no need to replace'
        srcPathList = getSrcPathList(isEclipse, projectDir)
        replaceCodeImport(srcPathList, package, destRClassPackage)

if  __name__ == '__main__':
    process()