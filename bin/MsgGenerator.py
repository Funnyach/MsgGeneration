import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import argparse as ap
from string import Template
import logic.DataPreperation as Prep
import logic.Generation as Gen

def Main(Package, Name):
    if(Package.exists()):
        for file in list(Package.glob('*.msg')):
            with file.open() as MsgFile:
                # Load the template for the msg file
                md = open('../Templates/MsgTemplate.txt')
                MainDoc = Template(md.read())
                md.close

                # Open a file, save its name and content
                MsgTemplateContent = MsgFile.readlines()
                MsgName = file.stem

                # Remove all \n from the contents of the service template
                MsgTemplateContent = Prep.RemoveParagraphs(MsgTemplateContent)

                # Create variable Array
                Variables = Prep.MakeVariableArray(MsgTemplateContent, Name)

                # Write the content to the C++ Template provided in the Template folder
                MainDocument = Template(
                    MainDoc.safe_substitute(packagename=Name, msgname=MsgName, includes=(Gen.GenIncludes(Variables))))
                MainDocument = MainDocument.safe_substitute(privatevariables=Gen.GenPrivateVariables(Variables),
                                                            constructor=Gen.GenConstructor(Variables, MsgName),
                                                            setters=Gen.GenSetters(Variables),
                                                            getters=Gen.GenGetters(Variables),
                                                            fromjson=Gen.GenFromJson(Variables),
                                                            tojsonobject=Gen.GenToJsonObject(Variables),
                                                            tostring=Gen.GenToString(Variables, MsgName))

                if (Package.parent.name == Name):
                    OutputPath = Package / '..' / Name
                else:
                    OutputPath = Package / Name

                OutputPath.mkdir(exist_ok=True)

                OutputFile = OutputPath / (MsgName + '.h')
                Output = open(str(OutputFile), 'w')

                Output.write(MainDocument)

                Output.close()

    else:
        print("Folder %s does not exist", Package)

if(__name__ == '__main__'):
    parser = ap.ArgumentParser(description='Generates UROSBridge compatible C++ files from msg files in a ROS Package.')
    parser.add_argument('--path', '-p', help='Provide the path to the ROS Package you want to generate the C++ files for.')
    parser.add_argument('--usegui', '-g', action='store_true', help='Use this if you want to open a filedialog to pick your path.')
    parser.add_argument('--msgfolder', '-mf', help='Use this if instead of a ROS Package you are selecting a folder directly containing the .msg files. Requires a namespace to be provided.')

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

    if(not args.msgfolder):
        msgdir = dirpath / "msg"
        PackageName = dirpath.name
    else:
        msgdir = dirpath
        PackageName = args.msgfolder
    Main(msgdir, PackageName)
