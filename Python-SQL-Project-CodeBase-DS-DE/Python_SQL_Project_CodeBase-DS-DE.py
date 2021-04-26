import getpass

from myTools import MSSQL_DBConnector as mssql
from myTools import DBConnector as dbc
import myTools.ContentObfuscation as ce


try:
    import pandas as pd
except:
    mi.installModule("pandas")
    import pandas as pd

try:
    import argparse as agp
except:
    mi.installModule("argparse")
    import argparse as agp

try:
    import os.path 
except:
    mi.installModule("os.path")
    import os.path



try:
    import pyodbc
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'pyodbc'])
finally:
    import pyodbc


def printSplashScreen():
    print("*************************************************************************************************")
    print("\t THIS SCRIPT ALLOWS TO EXTRACT SURVEY DATA FROM THE SAMPLE SEEN IN SQL CLASS")
    print("\t IT REPLICATES THE BEHAVIOUR OF A STORED PROCEDURE & TRIGGER IN A PROGRAMMATIC WAY")
    print("\t COMMAND LINE OPTIONS ARE:")
    print("\t\t -h or --help: print the help content on the console")
    print("*************************************************************************************************\n\n")



def processCLIArguments()-> dict:
    
    retParametersDictionary:dict = None
    
    dbpassword:str = ''
    obfuscator: ce.ContentObfuscation = ce.ContentObfuscation()

    try:
        argParser:agp.ArgumentParser = agp.ArgumentParser(add_help=True)

        #-n annotates DSN in the CLIArguments
        argParser.add_argument("-n", "--DSN", dest="dsn", \
                                action='store', default= None, help="Sets the SQL Server DSN descriptor file - Take precedence over all access parameters", type=str)
        #-s annotates Server name in the CLIArguments
        argParser.add_argument("-s", "--dbserver", dest="dbserver", \
                                action='store', default= None, help="Sets the SQL Server", type=str) 
        #-d annotates Database name in the CLIArguments
        argParser.add_argument("-d", "--dbname", dest="dbname", \
                                action='store', default= None, help="Sets the SQL database name", type=str)
        #-u annotates  dB userName in the CLIArguments
        argParser.add_argument("-u", "--dbusername", dest="dbusername", \
                                action='store', default= None, help="Sets the SQL database username", type=str)
        #-p annotates dB password in the CLIArguments
        argParser.add_argument("-p", "--dbuserpassword", dest="dbuserpassword", \
                                action='store', default= None, help="Sets the SQL database password", type=str)
        #-t annotates Connection trustMode in the CLIArguments
        argParser.add_argument("-t", "--trustedmode", dest="trustedmode", \
                                action='store', default= None, help="Sets the SQL trustmode", type=str)
        #-v annotates viewName in the CLIArguments
        argParser.add_argument("-v", "--viewname", dest="viewname", \
                                action='store', default= None, help="Sets the SQL database viewname", type=str)
        #-f annotates a directory called "persistencefilepath" which keeps a csv file in the CLIArguments
        argParser.add_argument("-f", "--persistencefilepath", dest="persistencefilepath", \
                                action='store', default= None, help="Sets the persistence file path", type=str)
        #-f annotates a directory called "resultsfilepath" which keeps a csv file in the CLIArguments
        argParser.add_argument("-r", "--resultsfilepath", dest="resultsfilepath", \
                                action='store', default= None, help="Sets the SQL result file path", type=str)

        #-s DESKTOP-SSD4DDF -d Survey_Sample_A19 -u sa -p 1234  -t True  -v vw_AllSurveyData -f filePath -r result 
        argParsingResults = argParser.parse_args()
        print(argParsingResults)
        
        retParametersDictionary = {
                    "dsn" : argParsingResults.dsn,        
                    "dbserver" : argParsingResults.dbserver,
                    "dbname" : argParsingResults.dbname,
                    "dbusername" : argParsingResults.dbusername,
                    "dbuserpassword" : dbpassword,
                    "trustedmode" : argParsingResults.trustedmode,
                    "viewname" : argParsingResults.viewname,
                    "persistencefilepath": argParsingResults.persistencefilepath,
                    "resultsfilepath" : argParsingResults.resultsfilepath
                }
        

    except Exception as e:
        print("Command Line arguments processing error: " + str(e))

    return retParametersDictionary

#To get the the survery structure from SurveyStructure table
def getSurveyStructure(connector: mssql.MSSQL_DBConnector) -> pd.DataFrame:
    
    surveyStructResults = None
    surveyQuery:str = 'SELECT * FROM SurveyStructure' 
    surveyStructResults:pd.DataFrame = connector.ExecuteQuery_withRS(surveyQuery)
    #TODO
    return surveyStructResults


#To check if persistenceFilePath does exist and contains a file 
def doesPersistenceFileExist(persistenceFilePath: str)-> bool:
    success = True
    if os.path.exists(persistenceFilePath):
        # path exists
        if os.path.isfile(persistenceFilePath): 
            # is it a file or a dir?
            # also works when file is a link and the target is writable
            #return os.access(fnm, os.W_OK)
            success = True
        else:
             success=False
            # path is a dir, so cannot write as a file
            #TODO
    else:
            success=False
    return success


#To check if the persistenceFilePath is writable
def isPersistenceFileDirectoryWritable(persistenceFilePath: str)-> bool:
    success = True
    
    pdir = os.path.dirname(persistenceFilePath)
    # target is creatable if parent dir is writable
    if os.access(pdir, os.W_OK):
        success=True
    else:
        os.chmod(persistenceFilePath, 777)
    return success

#To check if the actaul surveyStructure is not different from the stored surveyStructure in the persistenceFilePath
def compareDBSurveyStructureToPersistenceFile(surveyStructResults:pd.DataFrame, persistenceFilePath: str) -> bool:
    
    same_file = False
    persistenceSurveydf = pd.read_csv(persistenceFilePath)
    try:
        if persistenceSurveydf.equals(surveyStructResults):
            same_file = True
    except Exception as excp:
            print(excp)
    return same_file




def getAllSurveyDataQuery(connector: dbc.DBConnector) -> str:

    #IN THIS FUNCTION YOU MUST STRICTLY CONVERT THE CODE OF getAllSurveyData written in T-SQL, available in Survey_Sample_A19 and seen in class
    # Below is the beginning of the conversion
    # The Python version must return the string containing the dynamic query (as we cannot use sp_executesql in Python!)

    strQueryTemplateForAnswerColumn: str = """ COALESCE(( SELECT a.Answer_Value FROM Answer as a WHERE a.UserId = u.UserId AND a.SurveyId = <SURVEY_ID> AND a.QuestionId = <QUESTION_ID>), -1) AS ANS_Q<QUESTION_ID> """ 
    strQueryTemplateForNullColumnn: str = 'NULL AS ANS_Q<QUESTION_ID> '
    strQueryTemplateOuterUnionQuery: str = """SELECT UserId, <SURVEY_ID> as SurveyId, <DYNAMIC_QUESTION_ANSWERS> FROM [User] as u WHERE EXISTS ( SELECT * FROM Answer as a WHERE u.UserId = a.UserId AND a.SurveyId = <SURVEY_ID>)"""



    #MAIN LOOP, OVER ALL THE SURVEYS

    # FOR EACH SURVEY, IN currentSurveyId, WE NEED TO CONSTRUCT THE ANSWER COLUMN QUERIES
	#inner loop, over the questions of the survey
    # Cursors are replaced by a query retrived in a pandas df
    surveyQuery:str = 'SELECT SurveyId FROM Survey ORDER BY SurveyId' 
    surveyQueryDF:pd.DataFrame = connector.ExecuteQuery_withRS(surveyQuery)

    #CARRY ON THE CONVERSION
    #TODO
    #OutterForLoop over surveyId
        
    strFinalQuery: str = ''
    for i,data in surveyQueryDF.iterrows():
        currentSurveyId = data['SurveyId']
        print(currentSurveyId)
        strCurrentUnionQueryBlock: str = ''
       
        currentQuestionCursorStr:str = """SELECT * FROM ( SELECT SurveyId, QuestionId, 1 as InSurvey FROM SurveyStructure WHERE SurveyId = %s UNION SELECT %s as SurveyId,Q.QuestionId,0 as InSurvey FROM Question as Q WHERE NOT EXISTS(SELECT *FROM SurveyStructure as S WHERE S.SurveyId = %s AND S.QuestionId = Q.QuestionId )) as t ORDER BY QuestionId; """ % (currentSurveyId,currentSurveyId,currentSurveyId)
        currentQuestionCursorDF:pd.DataFrame = connector.ExecuteQuery_withRS(currentQuestionCursorStr)
       
        strColumnsQueryPart:str='';
        for j,currQData in currentQuestionCursorDF.iterrows():
    
            currentSurveyIdInQuestion = currQData['SurveyId']
            currentQuestionID = currQData['QuestionId']
            currentInSurvey = currQData['InSurvey']

            
            if currentInSurvey == 0 :
                strColumnsQueryPart= strColumnsQueryPart + strQueryTemplateForNullColumnn.replace('<QUESTION_ID>',str(currentQuestionID))
            else :
                strColumnsQueryPart= strColumnsQueryPart + strQueryTemplateForAnswerColumn.replace('<QUESTION_ID>',str(currentQuestionID))
            
            if j != len(currentQuestionCursorDF.index) - 1 :
                strColumnsQueryPart = strColumnsQueryPart + ', '
        ###Inner For loop ends

        ##BACK IN THE OUTER LOOP OVER SURVEYS
       
        strCurrentUnionQueryBlock = strCurrentUnionQueryBlock + strQueryTemplateOuterUnionQuery.replace('<DYNAMIC_QUESTION_ANSWERS>',str(strColumnsQueryPart))
        strCurrentUnionQueryBlock = strCurrentUnionQueryBlock.replace('<SURVEY_ID>', str(currentSurveyId)) 

        strFinalQuery = strFinalQuery + strCurrentUnionQueryBlock
        if i != len(surveyQueryDF.index)-1 :
            strFinalQuery = strFinalQuery + ' UNION '
    return strFinalQuery



#This represents the Trigger function in python
def refreshViewInDB(connector: dbc.DBConnector, baseViewQuery:str, viewName:str)->None:
    
    if(connector.IsConnected == True):
        
        try:
            createViewQuery = ' CREATE OR ALTER VIEW ' + viewName + ' AS ' + baseViewQuery
            connector.ExecuteQuery(createViewQuery)
        except Exception as excp:
            print(excp)

        



def surveyResultsToDF(connector: dbc.DBConnector, viewName:str)->pd.DataFrame:    
    results:pd.DataFrame =connector.ExecuteQuery_withRS( "Select * from "+viewName)
    return results;
    

  


def main():
    
    cliArguments:dict = None
    printSplashScreen()

    try:
        cliArguments = processCLIArguments()
    except Except as excp:
        print("Exiting")
        return

    if(cliArguments is not None):
        
        #if you are using the Visual Studio Solution, you can set the command line parameters within VS (it's done in this example)
        #For setting your own values in VS, please make sure to open the VS Project Properties (Menu "Project, bottom choice), tab "Debug", textbox "Script arguments"
        #If you are trying this script outside VS, you must provide command line parameters yourself, i.e. on Windows
        #python.exe Python_SQL_Project_Sample_Solution --DBServer <YOUR_MSSQL> -d <DBName> -t True
        #See the processCLIArguments() function for accepted parameters

        try:
            connector = mssql.MSSQL_DBConnector(DSN = cliArguments["dsn"], dbserver = cliArguments["dbserver"], \
                dbname = cliArguments["dbname"], dbusername = cliArguments["dbusername"], \
                dbpassword = cliArguments["dbuserpassword"], trustedmode = cliArguments["trustedmode"], \
                viewname = cliArguments["viewname"])
            connector.Open()
          
            surveyStructureDF:pd.DataFrame = getSurveyStructure(connector) #selecting data dbo.Surveystructure table

            if(doesPersistenceFileExist(cliArguments['persistencefilepath']) == False):

               if(isPersistenceFileDirectoryWritable(cliArguments['persistencefilepath']) == True): 
                    #pickle the dataframe in the path given by persistencefilepath
                    
                    df_savedSurveyStructure = surveyStructureDF.drop(surveyStructureDF.index[3])
                    df_savedSurveyStructure.to_csv(cliArguments['persistencefilepath'], index=False, header=True)
                    print("\nINFO - Content of SurveyResults table pickled in " + cliArguments['persistencefilepath'] + "\n")                   
                    #refresh the view using the function written for this purpose
                   
                    refreshViewInDB(connector, getAllSurveyDataQuery(connector), cliArguments['viewname'])
                    
            else:      
          
                if compareDBSurveyStructureToPersistenceFile(surveyStructureDF, cliArguments["persistencefilepath"]) :
                    print("New SurveyStructure is same as saved one, do nothing")
                else:
                     print('SurveyStructure is different than saved one, need to trigger view')
                     surveyStructureDF.to_csv(cliArguments['persistencefilepath'], index=False, header=True)
                     print("\nINFO - Content of SurveyResults table pickled in " + cliArguments['persistencefilepath'] )   
                     refreshViewInDB(connector, getAllSurveyDataQuery(connector), cliArguments['viewname'])

                surveyResultsDF = surveyResultsToDF(connector,cliArguments['viewname'])
                surveyResultsDF.to_csv(cliArguments["resultsfilepath"], index=False, header=True)
                print("\nDONE - Results exported in " + cliArguments["resultsfilepath"] + "\n")

            connector.Close()
        except Exception as excp:
            print(excp)
    else:
        print("Inconsistency: CLI argument dictionary is None. Exiting")
        return


#To execute the main function
if __name__ == '__main__':
    main()