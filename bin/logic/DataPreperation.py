import numpy as np


def RemoveParagraphs(RawDocument):
    CleanedArray = []
    for Element in RawDocument:
        if (Element.endswith('\n')):
            CleanedArray.append(Element[:-1])
        else:
            CleanedArray.append(Element)
    return CleanedArray


def ReadBaseTypes():
    bt = open("../config/BaseTypes.txt")
    BaseTypes = bt.readline().split(' ')
    bt.close()
    return BaseTypes


def ReadConversionChart():
    cc = open("../config/ConversionChart.txt")
    CleanedCC = RemoveParagraphs(cc.readlines())
    ConversionChart = []
    for Rule in CleanedCC:
        ConversionChart.append(Rule.split(' '))
    ConversionChart = np.array(ConversionChart)
    cc.close()
    return ConversionChart


def ReadJsonTypes():
    jt = open("../config/MatchJsonTypes.txt")
    CleanedJT = RemoveParagraphs(jt.readlines())
    JsonTypes = []
    for Match in CleanedJT:
        JsonTypes.append(Match.split(' '))
    JsonTypes = np.array(JsonTypes)
    jt.close()
    return JsonTypes


class Variable:
    def ConvertName(self, OriginalName):
        ConvertedName = OriginalName.replace('_', ' ').title().replace(' ', '')
        return ConvertedName

    def __init__(self, OriginalName='', Type='', IsArray=False, JsonType='', HasDefault=False, DefaultValue='',
                 NeedsInclude=False):
        self._HasDefault = HasDefault
        self._DefaultValue = DefaultValue
        self.SetOriginalName(OriginalName)
        self.SetType(Type)
        self._IsArray = IsArray
        self.SetJsonType(JsonType)
        self._ArrayJsonType = JsonType[:-5]
        self._NeedsInclude = NeedsInclude

    def SetOriginalName(self, OriginalName):
        self._OriginalName = OriginalName.lower()

        if(not self._HasDefault):
            self._Name = self.ConvertName(OriginalName)
        else:
            self._Name = self.ConvertName(OriginalName).upper()

        self._NameWithDefault = self._Name + ' = ' + self._DefaultValue

    def SetType(self, Type):
        self._Type = Type
        self._ArrayType = 'TArray<' + Type + '>'

    def SetIsArray(self, IsArray):
        self._IsArray = IsArray

    def SetNeedsInclude(self, NeedsInclude):
        self._NeedsInclude = NeedsInclude

    def SetJsonType(self, JsonType):
        self._JsonType = JsonType
        if (JsonType):
            self._ArrayJsonType = JsonType[:-5]

    def SetHasDefault(self, HasDefault):
        self._HasDefault = HasDefault

    def SetDefaultValue(self, DefaultValue):
        self._DefaultValue = DefaultValue

    def GetName(self):
        return self._Name

    def GetOriginalName(self):
        return self._OriginalName

    def GetNameWithDefault(self):
        return self._NameWithDefault

    def GetType(self):
        return self._Type

    def GetArrayType(self):
        return self._ArrayType

    def IsArray(self):
        return self._IsArray

    def GetJsonType(self):
        return self._JsonType

    def GetArrayJsonType(self):
        return self._ArrayJsonType

    def HasDefault(self):
        return self._HasDefault

    def GetDefaultValue(self):
        return self._DefaultValue

    def NeedsInclude(self):
        return self._NeedsInclude


def MakeVariableArray(MsgContent, PackageName):
    BaseTypes = ReadBaseTypes()
    ConversionChart = ReadConversionChart()
    JsonTypes = ReadJsonTypes()

    OutArray = []
    for i in range(0, len(MsgContent)):
        MsgContent[i] = ' '.join(MsgContent[i].split())
        if (not MsgContent[i] or MsgContent[i][0] == '#'):
            continue
        if (MsgContent[i].count('#') >= 1):
            SplitLine = MsgContent[i].split('#')[0].rstrip().split(' ')
        else:
            SplitLine = MsgContent[i].rstrip().split(' ')
        NewVariable = Variable()

        if (SplitLine[1].count('=') >= 1):
            NewVariable.SetHasDefault(True)
            NewVariable.SetDefaultValue(SplitLine[1].split('=')[-1])
            NewVariable.SetOriginalName(SplitLine[1].split('=')[0])
        else:
            NewVariable.SetHasDefault(False)
            NewVariable.SetOriginalName(SplitLine[1])

        if (SplitLine[0][-1:] == ']'):
            NewVariable.SetIsArray(True)
            SplitLine[0] = SplitLine[0][:SplitLine[0].index('[')] + '[]'
            if (SplitLine[0][:-2] in ConversionChart[:, 0]):
                LocalCC = ConversionChart[:, 0].tolist()
                NewVariable.SetType(ConversionChart[LocalCC.index(SplitLine[0][:-2])][1].replace('/', '::'))
            else:
                if (SplitLine[0][:-2] not in BaseTypes and SplitLine[0][:-2].count('/') == 0):
                    NewVariable.SetType(PackageName + '::' + SplitLine[0][:-2])
                else:
                    NewVariable.SetType(SplitLine[0][:-2].replace('/', '::'))

        else:
            NewVariable.SetIsArray(False)
            if (SplitLine[0] in ConversionChart[:, 0]):
                LocalCC = ConversionChart[:, 0].tolist()
                NewVariable.SetType(ConversionChart[LocalCC.index(SplitLine[0])][1].replace('/', '::'))
            else:
                if (SplitLine[0] not in BaseTypes and SplitLine[0].count('/') == 0):
                    NewVariable.SetType(PackageName + '::' + SplitLine[0])
                else:
                    NewVariable.SetType(SplitLine[0].replace('/', '::'))

        if (NewVariable.GetType() in JsonTypes[:, 0]):
            LocalJT = JsonTypes[:, 0].tolist()
            NewVariable.SetJsonType(JsonTypes[LocalJT.index(NewVariable.GetType())][1])
        else:
            NewVariable.SetJsonType('ObjectField')
        if (not (NewVariable.GetType() in ReadBaseTypes() or NewVariable.GetType() in ReadConversionChart()[:, 1])):
            NewVariable.SetNeedsInclude(True)
        else:
            NewVariable.SetNeedsInclude(False)
        OutArray.append(NewVariable)
    return OutArray
