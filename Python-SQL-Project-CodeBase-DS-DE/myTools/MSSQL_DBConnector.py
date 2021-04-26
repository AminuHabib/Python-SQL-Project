import platform

from myTools import DBConnector as db
import myTools.ModuleInstaller as mi

#This will install the necessary library needed to run the project
try:
    import pyodbc
except:
    mi.installModule("pyodbc")
    import pyodbc


class MSSQL_DBConnector(db.DBConnector):
    """This class inherits from the abstract class _DBConnector and implements _selectBestDBDriverAvailable for a MSSQL server connection"""

    #Constructor
    def __init__(self: object, DSN, dbserver: str, dbname: str, dbusername: str, \
                 dbpassword: str, trustedmode: bool =  False, viewname: str = "", isPasswordObfuscated:bool = True):
        
        super().__init__(DSN = DSN, dbserver = dbserver, dbname= dbname, dbusername = dbusername, \
            dbpassword = dbpassword, trustedmode = trustedmode, viewname = viewname, isPasswordObfuscated = isPasswordObfuscated)

        self._selectBestDBDriverAvailable()

    #Choose the best available driver to establish a connection
    def _selectBestDBDriverAvailable(self: object) -> None:
        lstAvailableDrivers:list[str] = pyodbc.drivers()
        
        identifiedOS: str = platform.system()


        if (lstAvailableDrivers is not None):
            
            if(len(lstAvailableDrivers) > 0):
               
                if('windows' in identifiedOS.lower()):
                    #According to recommendations found here: https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows
                    if ("ODBC Driver 17 for SQL Server" in lstAvailableDrivers):
                         self._driver = "ODBC Driver 17 for SQL Server"
                         self.selectedDriver="ODBC Driver 17 for SQL Server"
                         self.selectedDriver="ODBC Driver 17 for SQL Server"

                    if ("ODBC Driver 13.1 for SQL Server" in lstAvailableDrivers):
                         self._driver = "ODBC Driver 13.1 for SQL Server"
                         self.selectedDriver="ODBC Driver 17 for SQL Server"
                         self.selectedDriver="ODBC Driver 17 for SQL Server"
                  


            else:
                raise Exception('pyobdc cannot find any DB drivers installed on the system')
        else:
            raise Exception('pyodbc fails to extract the DB drivers installed on the system')


