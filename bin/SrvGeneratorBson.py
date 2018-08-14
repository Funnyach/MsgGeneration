import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import argparse as ap
from string import Template
import logic.DataPreperation as Prep
import logic.Generation as Gen


def Main(Package, Name):
    if Package.exists():
        for file in list(Package.glob('*.srv')):
            with file.open() as SrvFile:
                # Load the template for the srv file
                md = open('../Templates/SrvTemplateBson.txt')
                MainDoc = Template(md.read())
                md.close

                # Open a file, save its name and content
                SrvTemplateContent = SrvFile.readlines()
                SrvName = file.stem

                # Remove all \n from the contents of the service template
                SrvTemplateContent = Prep.RemoveParagraphs(SrvTemplateContent)

                # Create variable Arrays for Request and Response Variables
                ReqVariables = Prep.MakeVariableArray(SrvTemplateContent[:SrvTemplateContent.index('---')], Name)
                ResVariables = Prep.MakeVariableArray(SrvTemplateContent[SrvTemplateContent.index('---')+1:], Name)

                # Write the content to the C++ Template provided in the Template folder
                MainDocument = Template(MainDoc.safe_substitute(packagename=Name, srvname=SrvName, includes=(
                            Gen.GenIncludes(ReqVariables) + Gen.GenIncludes(ResVariables))))
                MainDocument = Template(
                    MainDocument.safe_substitute(reqprivatevariables=Gen.GenPrivateVariables(ReqVariables, 3),
                                                 reqconstructor=Gen.GenConstructor(ReqVariables, 'Request', 4),
                                                 reqsetters=Gen.GenSetters(ReqVariables, 3),
                                                 reqgetters=Gen.GenGetters(ReqVariables, 3),
                                                 reqfromjson=Gen.GenFromJson(ReqVariables, 4),
                                                 reqtojsonobject=Gen.GenToJsonObject(ReqVariables, 4),
                                                 reqtobsonobject=Gen.GenToBsonObject(ReqVariables, 4),
                                                 reqfrombson=Gen.GenFromBson(ReqVariables, 4),
                                                 reqtostring=Gen.GenToString(ReqVariables, SrvName + '::Request', 4)))
                MainDocument = MainDocument.safe_substitute(resprivatevariables=Gen.GenPrivateVariables(ResVariables, 3),
                                                            resconstructor=Gen.GenConstructor(ResVariables, 'Response', 4),
                                                            ressetters=Gen.GenSetters(ResVariables, 3),
                                                            resgetters=Gen.GenGetters(ResVariables, 3),
                                                            resfromjson=Gen.GenFromJson(ResVariables, 4),
                                                            restojsonobject=Gen.GenToJsonObject(ResVariables, 4),
                                                            restobsonobject=Gen.GenToBsonObject(ResVariables, 4),
                                                            resfrombson=Gen.GenFromBson(ResVariables, 4),
                                                            restostring=Gen.GenToString(ResVariables, SrvName + '::Response', 4))

                if(Package.parent.name == Name):
                    OutputPath = Package / '..' / Name
                else:
                    OutputPath = Package / Name
                
                OutputPath.mkdir(exist_ok=True)
                
                OutputFile = OutputPath / (SrvName + '.h')
                Output = open(str(OutputFile),'w')
                
                Output.write(MainDocument)
                
                Output.close()
    else:
        print("Folder %s does not exist", Package)

if(__name__ == '__main__'): 
    parser = ap.ArgumentParser(description='Generates UROSBridge compatible C++ files from srv files in a ROS Package.')
    parser.add_argument('--path', '-p', help='Provide the path to the ROS Package you want to generate the C++ files for.')
    parser.add_argument('--usegui', '-g', action='store_true', help='Use this if you want to open a filedialog to pick your path.')
    parser.add_argument('--srvfolder', '-sf', help='Use this if instead of a ROS Package you are selecting a folder directly containing the .srv files. Requires a namespace to be provided.')

    args = parser.parse_args()

    if(args.path and not args.usegui):
        dirpath = args.path
    elif(args.usegui and args.path):
        tk.Tk().withdraw()
        dirpath = filedialog.askdirectory(initialdir=args.path, title ='Please select a ROS Package.')
    elif(args.usegui and not args.path):
        tk.Tk().withdraw()
        dirpath = filedialog.askdirectory(initialdir=os.path.join(os.path.dirname(__file__), '..'), title ='Please select a ROS Package.')
    else:
        parser.error('A path needs to be specified. Use the -p option to specify a path or see --help for other options.')

    dirpath = Path(dirpath)

    PackageName = ''

    if(not args.srvfolder):
        srvdir = dirpath / 'srv'
        PackageName = dirpath.name
    else:
        srvdir = dirpath
        PackageName = args.srvfolder
    Main(srvdir, PackageName)

