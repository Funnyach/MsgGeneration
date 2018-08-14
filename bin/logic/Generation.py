def GenIncludes(Variables):
    Includes = ''
    AlreadyIncluded = []
    for Variable in Variables:
        if(Variable.NeedsInclude() and not Variable.GetType() in AlreadyIncluded):
            Includes += '#include "' + Variable.GetType().replace('::', '/') + '.h"\n'
            AlreadyIncluded.append(Variable.GetType())
    return Includes

def GenPrivateVariables(Variables, Indent = 2):
    PrivateVariables = ''
    for Variable in Variables:
        if(Variable.IsArray()):
            PrivateVariables += Variable.GetArrayType()
        else:
            PrivateVariables += Variable.GetType()
        PrivateVariables += ' '
        if(Variable.HasDefault()):
            PrivateVariables += Variable.GetNameWithDefault()
        else:
            PrivateVariables += Variable.GetName()
        PrivateVariables += ';\n'
        PrivateVariables += '\t' * Indent
    PrivateVariables = PrivateVariables[:-(Indent+1)] # Remove paragraph and indent from last line
    return PrivateVariables

def GenConstructor(Variables, ClassName, Indent = 3):
    Constructor = ClassName + '('

    for Variable in Variables:
        if (Variable.IsArray()):
            Constructor += Variable.GetArrayType()
        else:
            Constructor += Variable.GetType()
        Constructor += ' In'
        Constructor += Variable.GetName()
        Constructor += ',\n'
        Constructor += '\t' * Indent

    Constructor = Constructor[:-(Indent + 2)] + ')'

    Constructor += '\n'  # Paragraph
    Constructor += '\t' * Indent  # Default Indentation
    Constructor += ':\n'  # Constructor initialization starts here
    Constructor += '\t' * Indent

    for Variable in Variables:
        Constructor += Variable.GetName()
        Constructor += '(In' + Variable.GetName() + ')'
        Constructor += ',\n'
        Constructor += '\t' * Indent
    Constructor = Constructor[:-(Indent + 2)]

    return Constructor

def GenGetters(Variables, Indent = 2):
    Getters = '// Getters \n' + '\t' * Indent

    for Variable in Variables:
        if(Variable.IsArray()):
            Type = Variable.GetArrayType()
        else:
            Type = Variable.GetType()
        Name = Variable.GetName() # For shorter lines
        Getters += Type + ' Get' + Name + '() const { return ' + Name + '; }\n'
        Getters += '\t' * Indent
    Getters = Getters[:-(Indent+1)]
    return Getters

def GenSetters(Variables, Indent = 2):
    Setters = '// Setters \n' + '\t' * Indent

    for Variable in Variables:
        if(Variable.IsArray()):
            Type = Variable.GetArrayType()
        else:
            Type = Variable.GetType()
        Name = Variable.GetName() # For shorter lines
        Setters += 'void Set' + Name + '(' + Type + ' In' + Name + ') { ' + Name + ' = In' + Name + '; }\n'
        Setters += '\t' * Indent
    Setters = Setters[:-(Indent+1)]
    return Setters


def GenFromJson(Variables, Indent = 3):
    FromJson = ''

    ArrayFlag = False
    for Variable in Variables:
        if (Variable.IsArray()):
            ArrayFlag = True

    if (ArrayFlag):
        FromJson += 'TArray<TSharedPtr<FJsonValue>> ValuesPtrArr;\n\n'
        FromJson += '\t' * Indent

    for Variable in Variables:
        if (not Variable.IsArray()):
            if (Variable.GetJsonType() == 'ObjectField'):
                FromJson += Variable.GetName() + ' = ' + Variable.GetType() + '::GetFromJson(JsonObject->GetObjectField(TEXT("' + Variable.GetOriginalName() + '")));\n\n'
            else:
                FromJson += Variable.GetName() + ' = JsonObject->Get' + Variable.GetJsonType() + '(TEXT("' + Variable.GetOriginalName() + '"));\n\n'
            FromJson += '\t' * Indent
        else:
            FromJson += Variable.GetName() + '.Empty();\n' + '\t' * Indent
            FromJson += 'ValuesPtrArr = JsonObject->GetArrayField(TEXT("' + Variable.GetOriginalName() + '"));\n' + '\t' * Indent
            FromJson += 'for (auto &ptr : ValuesPtrArr)\n' + '\t' * Indent
            if (Variable.GetJsonType() == 'ObjectField'):
                FromJson += '\t' + Variable.GetName() + '.Add(' + Variable.GetType() + '::GetFromJson(ptr->AsObject()));\n\n' + '\t' * Indent
            else:
                FromJson += '\t' + Variable.GetName() + '.Add(ptr->As' + Variable.GetJsonType()[
                                                                         :-5] + '());\n\n' + '\t' * Indent
    FromJson = FromJson[:-(Indent + 1)]
    return FromJson


def GenFromBson(Variables, Indent = 3):
    FromBson = ''

    ArrayFlag = False
    for Variable in Variables:
        if (Variable.IsArray()):
            ArrayFlag = True

    if (ArrayFlag):
        FromBson += 'TArray<TSharedPtr<FBsonValue>> ValuesPtrArr;\n\n'
        FromBson += '\t' * Indent

    for Variable in Variables:
        if (not Variable.IsArray()):
            if (Variable.GetJsonType() == 'ObjectField'):
                FromBson += Variable.GetName() + ' = ' + Variable.GetType() + '::GetFromBson(BsonObject->GetObjectField(TEXT("' + Variable.GetOriginalName() + '")));\n\n'
            else:
                FromBson += Variable.GetName() + ' = BsonObject->Get' + Variable.GetJsonType() + '(TEXT("' + Variable.GetOriginalName() + '"));\n\n'
            FromBson += '\t' * Indent
        else:
            FromBson += Variable.GetName() + '.Empty();\n' + '\t' * Indent
            FromBson += 'ValuesPtrArr = BsonObject->GetArrayField(TEXT("' + Variable.GetOriginalName() + '"));\n' + '\t' * Indent
            FromBson += 'for (auto &ptr : ValuesPtrArr)\n' + '\t' * Indent
            if (Variable.GetJsonType() == 'ObjectField'):
                FromBson += '\t' + Variable.GetName() + '.Add(' + Variable.GetType() + '::GetFromBson(ptr->AsObject()));\n\n' + '\t' * Indent
            else:
                FromBson += '\t' + Variable.GetName() + '.Add(ptr->As' + Variable.GetJsonType()[
                                                                         :-5] + '());\n\n' + '\t' * Indent
    FromBson = FromBson[:-(Indent + 1)]
    return FromBson


def GenToJsonObject(Variables, Indent = 3):
    ToJsonObject = ''

    ToJsonObject += 'TSharedPtr<FJsonObject> Object = MakeShareable<FJsonObject>(new FJsonObject());\n\n'
    ToJsonObject += '\t' * Indent

    for Variable in Variables:
        if (Variable.IsArray()):
            ToJsonObject += 'TArray<TSharedPtr<FJsonValue>> ' + Variable.GetName() + 'Array;\n' + '\t' * Indent
            ToJsonObject += 'for (auto &val : ' + Variable.GetName() + ')\n' + '\t' * Indent
            if (Variable.GetJsonType() == 'ObjectField'):
                ToJsonObject += '\t' + Variable.GetName() + 'Array.Add(MakeShareable(new FJsonValue' + Variable.GetJsonType()[
                                                                                                       :-5] + '(val.ToJsonObject())));\n' + '\t' * Indent
            else:
                ToJsonObject += '\t' + Variable.GetName() + 'Array.Add(MakeShareable(new FJsonValue' + Variable.GetJsonType()[
                                                                                                       :-5] + '(val)));\n' + '\t' * Indent
            ToJsonObject += 'Object->SetArrayField(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + 'Array);\n'

        else:
            if (Variable.GetJsonType() == 'ObjectField'):
                ToJsonObject += 'Object->SetObjectField(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + '.ToJsonObject());\n'
            else:
                ToJsonObject += 'Object->Set' + Variable.GetJsonType() + '(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + ');\n'
        ToJsonObject += '\n' + '\t' * Indent

    ToJsonObject += 'return Object;\n'

    return ToJsonObject


def GenToBsonObject(Variables, Indent = 3):
    ToBsonObject = ''

    ToBsonObject += 'TSharedPtr<FBsonObject> Object = MakeShareable<FBsonObject>(new FBsonObject());\n\n'
    ToBsonObject += '\t' * Indent

    for Variable in Variables:
        if (Variable.IsArray()):
            ToBsonObject += 'TArray<TSharedPtr<FBsonValue>> ' + Variable.GetName() + 'Array;\n' + '\t' * Indent
            ToBsonObject += 'for (auto &val : ' + Variable.GetName() + ')\n' + '\t' * Indent
            if (Variable.GetJsonType() == 'ObjectField'):
                ToBsonObject += '\t' + Variable.GetName() + 'Array.Add(MakeShareable(new FBsonValue' + Variable.GetJsonType()[
                                                                                                       :-5] + '(val.ToBsonObject())));\n' + '\t' * Indent
            else:
                ToBsonObject += '\t' + Variable.GetName() + 'Array.Add(MakeShareable(new FBsonValue' + Variable.GetJsonType()[
                                                                                                       :-5] + '(val)));\n' + '\t' * Indent
            ToBsonObject += 'Object->SetArrayField(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + 'Array);\n'

        else:
            if (Variable.GetJsonType() == 'ObjectField'):
                ToBsonObject += 'Object->SetObjectField(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + '.ToBsonObject());\n'
            else:
                ToBsonObject += 'Object->Set' + Variable.GetJsonType() + '(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + ');\n'
        ToBsonObject += '\n' + '\t' * Indent

    ToBsonObject += 'return Object;\n'

    return ToBsonObject

def GetProperStringFormatting(Variable):
    if (Variable.GetJsonType() == 'ObjectField'):
        return '%s.ToString()'
    elif (Variable.GetJsonType() == 'BoolField'):
        return 'FString::FromInt(%s)'
    elif (Variable.GetJsonType() == 'StringField'):
        return '%s'
    else:
        if (Variable.GetType() == 'float' or Variable.GetType() == 'double'):
            return 'FString::SanitizeFloat(%s)'
        else:
            return 'FString::FromInt(%s)'

def GenToString(Variables, MsgName, Indent = 3):
    ToString = '\n'

    for Variable in Variables:
        if(Variable.IsArray()):
            ToString += '\t'*Indent + 'FString ' + Variable.GetName() + 'String = "[ ";\n'
            ToString += '\t'*Indent + 'for (auto &value : ' + Variable.GetName() + ')\n'
            ToString += '\t'*(Indent+1) + Variable.GetName() + 'String += ' + GetProperStringFormatting(Variable) % 'value' + ' + TEXT(", ");\n'
            ToString += '\t'*Indent + Variable.GetName() + 'String += " ] ";\n'

    ToString += '\t'*Indent + 'return TEXT("' + MsgName + ' { '
    for Variable in Variables:
        if(Variable.IsArray()):
            ToString += Variable.GetOriginalName() + ' =") + ' + Variable.GetName() + 'String +\n'
            ToString += '\t'*(Indent+1) + 'TEXT(", '
        else:
            ToString += Variable.GetOriginalName() + ' = ") + ' + GetProperStringFormatting(Variable) % Variable.GetName() + ' +\n'
            ToString += '\t'*(Indent+1) + 'TEXT(", '

    ToString = '\t'*(Indent+1) + ToString [:-2] + ' } ");\n'

    return ToString
