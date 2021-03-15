import requests
from requests.exceptions import RequestException
import os
import re
import ast
from collections import defaultdict
import json

class DataSource:
    '''This creates a list of data sources'''
    def __init__(self):
        '''instatiate the data_source object'''
        self.dataSourceList=defaultdict(list)

        uploadDataList = True
        while uploadDataList:
            print('''
                  Type 'YES' or 'Y' to load data source file. 
                  Else type 'NO' or 'N' to enter data website address directly.\n
                  ''')
            print('-'*70,'\n')
            response = input(' >> : ').lower()

            # get file location.
            if response =='yes' or response == 'y':
                print('''
                      Please ensure file is in current working directory.
                      or
                      Use type 'Full Path' of file.
                      And each data source web address is on a single line.\n
                      ''')
                print('-'*70,'\n')
                filePath = input('Enter file name >>> ')

                # Extract the full file path.
                if os.path.isfile(os.path.join(os.getcwd(),filePath))==True:
                    abs_filePath = os.path.join(os.getcwd(),filePath)
                elif os.path.isabs(filePath):
                    abs_filePath=filePath 
                elif os.path.getsize(os.path.join(os.getcwd(),abs_filePath))==0:
                    print('Empty file.')
                    continue
                else:
                    error_message='''
                    File Not Found. 
                    Ensure file is in the current working directory. 
                    Or give full file path'''
                    InvalidFileError = IOError(error_message)
                    print('File Error: ',InvalidFileError)
                    continue

#-----------------------------------------------------------------------------

                # navigate through the given file, and validate.
                # data sources.

                with open(abs_filePath, 'r') as filecontent:
                    #read file content as list and extract the unique sources.
                    filecontentList=sorted(list(set(filecontent.readlines())))
                    formatRe = re.compile(r'((http[s]?:\/\/www\.)|(http[s]?:\/\/)|(www\.))')
                    #validate and reformat list.
                    formattedList=[formatRe.sub('http://',i) for i in
                                   filecontentList if formatRe.search(i) is not
                                  None]
                    secondList=['http://'+i for i in filecontentList if
                                formatRe.search(i) is None]
                    formattedList.extend(secondList)
                    # Ensure it is a genuine website address.
                    formattedList = self.validateList(formattedList)
                    temp_list = [i.strip() for i in formattedList]
                    
                # check if the source file is empty.
                if 'dataSourceList.txt' in os.listdir(os.getcwd()):
                    if\
                    os.path.getsize(os.path.join(os.getcwd(),'dataSourceList.txt'))==0:
                        self.RemoveSource()
                    pass
                    
              # check if data source list file already exists. 
                if 'dataSourceList.txt' in os.listdir(os.getcwd()):

                    # append given list to temp source list.
                    self.dataSourceList['from_file'].extend(temp_list)
                    self.dataSourceList = dict(self.dataSourceList)

                    with open('dataSourceList.txt', 'r') as temp:
                        # open file as dictionary
                        temp_content = temp.read()
                        temp_dict = ast.literal_eval(temp_content)

                    # combine the dictionaries
                    new_dict=self.merge_dict(temp_dict,self.dataSourceList)
                    self.dataSourceList = new_dict
                    
                    for key in self.dataSourceList.keys():
                        unique_values = list(set(self.dataSourceList[key]))
                        self.dataSourceList[key] = unique_values

                    # write the new file contents.
                    with open('dataSourceList.txt', 'w') as temp:
                        temp.write(str(self.dataSourceList))
                    break

                else: # new data source list creation.      
                    self.dataSourceList['from_file'].extend(temp_list)
                    self.dataSourceList = dict(self.dataSourceList)
                    print(self.dataSourceList)
                    with open('dataSourceList.txt', 'w') as temp:
                        temp.write(str(self.dataSourceList))
                    break

#-----------------------------------------------------------------------------
                        
            # accept web address directly.
            if response == 'no' or response ==  'n':
                print('Type in the web address of the data source')
                dataAddress=input('>>> ')
                
                formatRe = re.compile(r'((http[s]?:\/\/www\.)|(http[s]?:\/\/)|(www\.))')
                # reformat the web address.
                if formatRe.search(dataAddress) is not None:
                    dataAddress = formatRe.sub('http://',dataAddress)
                if formatRe.search(dataAddress) is None:
                    dataAddress = 'http://'+dataAddress
             
                try: # validate the web address.
                    if requests.Session().get(dataAddress).status_code == 200:
                        dataAddress = dataAddress
                except RequestException:
                    print('''URLError: Invalid URL.
                      \n''')
                    
                    continue 

                # check if the source file is empty.
                if 'dataSourceList.txt' in os.listdir(os.getcwd()):
                    if\
                    os.path.getsize(os.path.join(os.getcwd(),'dataSourceList.txt'))==0:
                        self.RemoveSource()
                    pass

                # check if source list exists.
                if 'dataSourceList.txt' in os.listdir(os.getcwd()):
                    self.dataSourceList['direct_entry'].append(dataAddress)
                    self.dataSourceList = dict(self.dataSourceList)

                    with open('dataSourceList.txt', 'r') as temp:
                        temp_content = temp.read()
                        temp_dict = ast.literal_eval(temp_content)
                        

                    # combine the two dictionaries.
                    new_dict=self.merge_dict(temp_dict,self.dataSourceList)
                    self.dataSourceList = new_dict

                    for key in self.dataSourceList.keys():
                        unique_values = list(set(self.dataSourceList[key]))
                        self.dataSourceList[key] = unique_values
                        
                    # write the new dictionary to file.
                    with open('dataSourceList.txt', 'w') as temp:
                        temp.write(str(self.dataSourceList))
                                
                    break

                else: # new source list creation.     
                    # add to dictionary
                    self.dataSourceList['direct_entry'].append(dataAddress)
                    self.dataSourceList = dict(self.dataSourceList)
                    # add to data source file
                    with open('dataSourceList.txt', 'w') as temp:
                        temp.write(str(self.dataSourceList))
                    break

            else:
                continue
                

    def __str__(self):
        if len(self.dataSourceList) != 0:
            return json.dumps(self.dataSourceList, indent=4)
        else: return 'There is no data source'

    def merge_dict(self,dict1,dict2):
        'Merge dictionaries and keep values of common keys in lists'
        dict3 = {**dict1, **dict2}
        for key, value in dict3.items():
            if key in dict1 and key in dict2:
                if dict1[key]==None or dict2[key]==None:
                    return dict3
                else:
                    dict3[key] = [*value,*dict1[key]]
        return dict3

    def validateList(self,sData):
        validList = []
        for i in sData:
            if requests.Session().get(i.strip()).status_code==200:
                validList.append(i)
        return validList
                 
    def DelItem(self, item_address):
        # delete item from the source list.
        try:
            for key,value in self.dataSourceList:
                if item_address in self.dataSourceList[key]:
                    self.dataSourceList.remove(item_address)
        except:
            print(f'No such item "{item_key}".')
        finally:
            with open(dataSourceList.txt, 'w') as temp:
                temp.write(str(self.dataSourceList))

    def RemoveSource(self):
        # removes the data source. Use with care.
        if os.path.exists('dataSourcesList.txt'):
            os.remove('dataSourcesList.txt')
        else: print('File does not exist')
        
if __name__=='__main__':
    a = DataSource()
    print(a)
