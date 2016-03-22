# AndroidRClassGenerator
AndroidRClassGenerator is used to generate R.java class under specific package for android res folder

# Configurations
Before running AndroidRClassGenerator, the configurations in config.ini should be set. The meaning of each parameter is described as follows.

1. ProjectOrResDir: the path of the android library project(Could be an Eclipse project or an Android Studio project). Also you can specify an resource path in Android project.

2. sdkdir: the path of Android SDK

3. RClassPackage: the destination class name of the R class.

4. ReplaceCode: using to indicates whether replace the import information in codes. If it is set as true, the replace code process will be execute after R class generated.
If ProjectOrResDir is set as the resources path, this parameter will be ignored.

---------------------------------------------------------分割线---------------------------------------------------------
# AndroidRClassGenerator
此工具用来生成R.java类

# 参数配置
在使用前需要先配置config.ini，config.ini中各个参数的含义如下。

1. ProjectOrResDir：表示library工程的路径（可以是Eclipse的工程，也可以是Android Studio的工程）。也可以直接指定到某个资源目录。
2. sdkdir：Android SDK的路径
3. RClassPackage：要生成的目标R类的包名
4. ReplaceCode：是否替换代码中的import信息，true表示替换，false表示不替换。当ProjectOrResDir配置的是资源目录时，此项配置会被忽略。
例如library工程的包名为x.y.z，RClassPackage为a.b.c，则当ReplaceCode为true时会自动将代码中的import x.y.z.R，改为import a.b.c。

# library开发者的使用方法
对library开发者来说，需要生成一个包含指定包名的R类放到代码中，然后将其他代码中所有用到默认R类（即该library工程包名下R类）的地方都替换为生成的R类。
具体配置流程如下。

1. 配置ProjectOrResDir为工程的路径，可以是Eclipse的工程，也可以是Android Studio的工程。
2. 配置sdkdir为本地的Android SDK的路径
3. 配置RClassPackage为需要生成的R类的包名，此包名不可和library的包名完全相同。以免在app工程编译时出现相同类名的编译错误。
4. ReplaceCode一般应配置为true。如果已经替换过一次，且没有新的代码需要替换，可以设置为false。
5. 运行RClassGenerator.py
6. 在library工程入口代码处（例如初始化，或者第一个界面显示时）调用R.init(context)，这里的R类是新生成的R类，context是某个Activity。

# app开发者的使用方法
对app开发者来说，需要生成一个包含library包名的R类放到app工程的代码中。
具体配置流程如下。

1. 如果是Eclipse的library工程，配置ProjectOrResDir为library工程中res目录的路径，如果是Android Studio的工程，需要先将res目录从aar文件中解压出来，然后配置ProjectOrResDir为解压后的res目录路径。
2. 配置sdkdir为本地的Android SDK的路径
3. 配置RClassPackage为library的包名，library的包名可以在library中的AndroidManifest.xml文件中找到
4. ReplaceCode参数在ProjectOrResDir配置为资源目录时会被自动忽略。
5. 运行RClassGenerator.py
6. 在app工程主Activity的onCreate()中调用R.init(this)，这里的R类是新生成的R类

# 为什么需要手动生成R.java类
## Android library工程
Android 工程根据用途的不同分为app工程和library工程。
app工程用来生成可以在Android系统上运行的apk程序，提交到应用市场给用户使用。
library工程不会生成apk，而是生成sdk，用来给其他开发者使用。
对library工程来说，如果library工程中包含了资源文件，如layout，drawable，string，dimen等，那么在生成的sdk中就需要包含这些资源文件。
如果是Eclipse library工程，需要将整个res目录放到sdk中。如果是Android Studio的library工程，会在生成的aar文件中自动包含res目录。

## Android library工程中的R.java类
R.java是Android中一个非常重要的类，代码大量使用R类来获取各类资源的id，根据资源id来找到对应的资源。
如R.id.framelayout，R.drawable.bg，R.string.app_name等。
然而对library工程来说，R.java类并不会包含在library工程编译后的jar包或arr包中。而是在app工程编译时生成的。
显然library工程必须包含在app工程中才能使用。一个app工程可以通过引用方式来包含若干个library工程。
当一个app工程在编译时，会先将各个library工程的资源和app工程的资源合并到一起，然后生成一个app工程包名下的R.java类。
接着会生成其引用的各个library工程对应的R.java类。这里会用到每个library工程中提供的另外一个文件，也就是AndroidManifest.xml文件。
library工程的AndroidManifest.xml文件中包含了包名称的配置，生成的R.java类就在对应的包名下面。
例如，一个被引用的library工程中的AndroidManifest.xml文件中配置的package="com.cclink.mylib"，则app工程在编译时会为该library工程生成一个com.cclink.mylib.R的类。
最后app工程全部java代码，app工程的R类，所有library工程的R.java类，都会被编译，并和所有library工程的jar包合并到一起，然后在转换成一个dex文件。

## Android library工程的特殊使用方式
一个library工程会以sdk的形式提供给其他开发者来使用。如前所述，其他开发者在开发app时，如果通过引用的方式来使用该library工程，则app工程编译时会自动为library工程生成一个R类，并打包到apk中。
然后，app的开发者并不总是希望通过引用的方式来使用一个library。他们有时需要将library工程的jar和res直接拷贝到app工程来使用，有时需要将所有library工程的jar和res拷贝到一起来使用。
这有时是为了方便，减少工作量，有时是没有办法通过引用方式来使用library，因为根本就找不到一个app的主工程。
这在游戏app开发时非常常见。很多引擎只提供了一个目录，用来放置各个Android插件，根本就找不到一个主工程，来在Eclipse或Android Studio中导入，并建立引用关系。
例如，Unity3D中通常都是将android插件直接拷贝到/Assets/Plugins/Android目录中来使用，虽然Unity3D提供了导出Android工程的功能，但使用起来非常麻烦。
其他引擎也差不多，除了Cocos2dx之外，很少有引擎能够通过直接引用方式来使用Android library插件。

## Android library工程特殊使用方式带来的问题
如果通过这种将文件拷贝到一起的方式来使用library工程，app在编译时根本就找不到原先各个library工程中的AndroidManifest.xml文件，更不会为各个library工程生成对应的R类。当app在运行时，library中代码由于找不到对应的R类，会出现ClassNotFound的异常。

## 解决这种使用方式带来的问题
要解决这个问题，需要从两个角度来考虑。
从library开发者的角度来看，需要让library工程编译后的sdk能够支持这种直接拷贝的使用方式。
为了达到此目录，需要将代码中所有使用R类来获取资源id的地方替换为其他的实现方式。AndroidRClassGenerator能够生成一个新的R类，新的R类中使用了不同的方式来获取资源id，同时提供了和原先R类一样的访问资源的方式。
只需要将代码中原先的import R类的信息替换替换为新的R类即可访问到对应的资源id，AndroidRClassGenerator可同时生成R类，并完成代码import的替换。
从app开发者的角度来看，如果一个library工程没有对这种使用方式做兼容，而又没法通过引用方式来使用该library时，需要能够让该library打包到apk后能够正常运行。
为了达到此目录，需要为该library工程生成一个library工程包名下的R类，然后将该R类编译打包到apk中。这样library工程中的代码在运行就不会找不到对应的R类了。AndroidRClassGenerator可以根据library工程中的res目录生成对应的R类。

# 实现原理
通过用AndroidRClassGenerator生成R类代替了原本应该在app编译时生成的R类，用这种方式来让library中代码能够正确的得到资源id。由于资源id只有在apk编译时才能最终确定，所以AndroidRClassGenerator生成的R类不能用某次编译时的常量来代替。 
有两种方式可以获取到资源id：一种是通过反射app包名下的R类来获取，一种是通过getResources().getIdentifier()方法来获取。 
通过反射方式来获取资源id的原理是，虽然app编译时不会为每个library生成单独的R类，但是仍然会生成一个app包名下的R类，这个R类中包含了所有library中的资源id（当然也还包含app自身的全部资源的id），通过反射读取这个R类，可以得到对应的资源id。 getResources().getIdentifier()是android sdk提供的一个api，通过此接口可以获取到指定类型，指定名称的资源id。 
AndroidRClassGenerator生成的R类同时包含了这两种实现方式，它首先会尝试通过反射方式来获取系统资源id，如果反射方式获取失败，再尝试用getResources().getIdentifier()方式来获取。 
之所以先用反射方式来获取资源id，是因为反射方式比getResources().getIdentifier()方式要快得多。但反射方式的缺点是必须要存在一个app包名下的R类。如果这个类不存在（例如，通过Unity3D直接编译出的apk中就不包含R类），则反射方式失效。无论有没有app包名下的R类，context.getResources().getIdentifier()都能够获取到资源id，但context.getResources().getIdentifier()方式比反射方式要慢一些。