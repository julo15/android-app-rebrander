import sys
import json
import os.path
import xmltodict
import shutil

# python brand_it.py ~/Documents/myThemeFolder ~/FooAppRoot signingPassword

def copyDrawablesFile(source, baseDestFolder, destDpiFolder, destFilename):
   # todo: check if dest file actually exists
   destFolder = os.path.join(baseDestFolder, "app/src/main/res", destDpiFolder)
   if not os.path.exists(destFolder):
      os.mkdir(destFolder)

   destFullPath = os.path.join(destFolder, destFilename)
   print("Copying from %s to %s" % (source, destFullPath))
   shutil.copy(source, destFullPath)
   return

# check params
if len(sys.argv) != 4:
   print("Usage: %s <theme dir> <source root dir> <signing password>")
   quit()
else:
   parameterFilename = os.path.join(sys.argv[1], "parameters.json")
   sourceDir = sys.argv[2]
   print("Reading parameters from %s" % parameterFilename)

# open parameters file
with open(parameterFilename) as parameterFile:
    parameters = json.load(parameterFile)

# generate parameters
parameters["gen_submitButtonDisabledBgColor"] = parameters["submitButtonBgColor"].replace("#", "#96")
parameters["gen_submitButtonDisabledTextColor"] = parameters["submitButtonTextColor"].replace("#", "#96")

# all file copies are relative to the theme folder
os.chdir(sys.argv[1])

# basic app info
print("Package name: %s" % parameters["package"])
print("Version code: %s" % parameters["versionCode"])
print("Version name: %s" % parameters["versionName"])

brandName = parameters["brandName"]
workDir =  os.path.join(sys.argv[1], "android")

print("Brand name: %s" % brandName)
print("Work directory: %s" % workDir)

# clean out the old directory
if os.path.exists(workDir):
   shutil.rmtree(workDir)
shutil.copytree(sourceDir, workDir)

# copy non-drawable assets/resources
shutil.copy(parameters["quicksandFont"], os.path.join(workDir, "app/src/main/assets"))
shutil.copy(parameters["quicksandBoldFont"], os.path.join(workDir, "app/src/main/assets"))

# copy drawable images
DRAWABLE_MDPI = "drawable-mdpi"
DRAWABLE_HDPI = "drawable-hdpi"
DRAWABLE_XHDPI = "drawable-xhdpi"
DRAWABLE_XXHDPI = "drawable-xxhdpi"
DRAWABLE_XXXHDPI = "drawable-xxxhdpi"

copyDrawablesFile(parameters["logo"], workDir, DRAWABLE_XHDPI, "logo.png")
copyDrawablesFile(parameters["logoLowDpi"], workDir, DRAWABLE_MDPI, "logo.png")

# TODO: Use copyDrawablesFile to copy over more drawables

APP_ICON_FILENAME = "icon.png"
copyDrawablesFile(parameters["appLogoAndroid48x48"], workDir, DRAWABLE_MDPI, APP_ICON_FILENAME)
copyDrawablesFile(parameters["appLogoAndroid72x72"], workDir, DRAWABLE_HDPI, APP_ICON_FILENAME)
copyDrawablesFile(parameters["appLogoAndroid96x96"], workDir, DRAWABLE_XHDPI, APP_ICON_FILENAME)
copyDrawablesFile(parameters["appLogoAndroid144x144"], workDir, DRAWABLE_XXHDPI, APP_ICON_FILENAME)
copyDrawablesFile(parameters["appLogoAndroid192x192"], workDir, DRAWABLE_XXXHDPI, APP_ICON_FILENAME) 

# now work in the new project
os.chdir(workDir)

# manifest
manifestFilename = "./app/src/main/AndroidManifest.xml"
if os.path.exists(manifestFilename) == False:
   print("Cannot find %s" % manifestFilename)
   quit()

with open(manifestFilename) as file:
   manifest = file.read()
   document = xmltodict.parse(manifest)
   root = document["manifest"]

   #root["@package"] = data["package"]
   root["@android:versionCode"] = parameters["versionCode"]
   root["@android:versionName"] = parameters["versionName"]
   file.close()
   newFile = open(manifestFilename, "w")
   newFile.write(xmltodict.unparse(document,  pretty = True))
   newFile.close()

# gradle.build
gradleBuildFilename = "./app/build.gradle"
with open(gradleBuildFilename, 'r') as file:
   array = []
   for line in file:
      if (line.strip().startswith("applicationId")):
         array.append("        applicationId \"%s\"\n" % parameters["package"])
      else:
         array.append(line)
   file.close()
   newFile = open(gradleBuildFilename, "w")
   for item in array:
      newFile.write("%s" % item)
   newFile.close()

# colors
colorsFilename = "./app/src/main/res/values/colors.xml"
with open(colorsFilename) as file:
   xml = file.read()
   document = xmltodict.parse(xml)
   colors = document["resources"]["color"]
   for color in colors:
       if '@replaceWith' in color:
           color["#text"] = parameters[color["@replaceWith"]]
   file.close()
   newFile = open(colorsFilename, "w")
   newFile.write(xmltodict.unparse(document,  pretty = True))
   newFile.close()

# strings
stringsFilename = "./app/src/main/res/values/strings.xml"
with open(stringsFilename) as file:
    xml = file.read()
    document = xmltodict.parse(xml)
    strings = document["resources"]["string"]
    for string in strings:
        if '@replaceWithFont' in string:
            string["#text"] = os.path.basename(parameters[string["@replaceWithFont"]])
        elif '@replaceWith' in string:
            string["#text"] = parameters[string["@replaceWith"]]
    file.close()
    newFile = open(stringsFilename, "w")
    newFile.write(xmltodict.unparse(document, pretty = True))
    newFile.close()

# dimens
dimensFilename = "./app/src/main/res/values/dimens.xml"
with open(dimensFilename) as file:
    xml = file.read()
    document = xmltodict.parse(xml)
    dimens = document["resources"]["dimen"]
    for dimen in dimens:
        if '@type' in dimen:
            if dimen['@type'] == 'logo':
                if parameters["isLogoPortrait"]:
                    dimen['#text'] = '@dimen/' + dimen['@portraitDimen'];
    file.close()
    newFile = open(dimensFilename, "w")
    newFile.write(xmltodict.unparse(document, pretty = True))
    newFile.close()

# build and sign
os.environ["KEYSTOREPWD"] = sys.argv[3];
os.environ["KEYPWD"] = sys.argv[3];
os.system("chmod +x gradlew")
os.system("./gradlew clean")
os.system("./gradlew assembleRelease")
